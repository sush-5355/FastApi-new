import base64
import os
import json
import fastapi
import fastapi.security
import glob
import importlib
import os
import jwt
import uuid
import httpx
import typing
import traceback
import framework.context
import framework.tenant
import framework.settings
import framework.redispool
import contextvars
from pydantic.fields import Field

app = fastapi.FastAPI()
KEYCLOAK_URL = 'https://beta.mycybercns.com'
KEYCLOAK_ADMIN = framework.settings.keycloak_admin
KEYCLOAK_ADMIN_PASSWORD = framework.settings.keycloak_password
cookie_name = framework.settings.cookie_name
private_key = ''
if framework.settings.JWTPath and os.path.exists(framework.settings.JWTPath):
    private_key = open(framework.settings.JWTPath).read()

@app.on_event("startup")
def onStart():
    for filename in glob.glob("**/*.py", recursive=True):
        if filename.startswith("_"):
            continue
        modname = os.path.splitext(filename)[0].replace(os.sep, '.')
        # print("Loading:",modname)
        mod = importlib.import_module(modname)
        
        # If a variable by name "roter" is defined load that directly
        # Else go through the module and if any of the variable is a router load that...
        symbol = getattr(mod, 'router', None)
        if isinstance(symbol, fastapi.APIRouter):
            app.include_router(symbol, prefix="/api")
        else:
            for attr in dir(mod):
                if not attr.startswith("_"):
                    symbol = getattr(mod, attr)
                    if isinstance(symbol, fastapi.APIRouter):
                        # print("Loading module:", modname, " Route:",attr, [(x.path, x.name)  for x in symbol.routes])
                        app.include_router(symbol, prefix="/api")
    # print("Loaded modules:")
    # for route in app.routes:
    #     print(route.path, route.name)


# Api to push data to redis server
async def createInternalErrorMessage(errFormat):
    try:
        id = str(uuid.uuid4()).replace("-", "")
        conn = await framework.redispool.get_redis_connection()
        await conn.setex("internalerror_" + id, 60, errFormat)
        return True, id
    except:
        return False, ""


async def get_permission():
    rpt = framework.context.context.get('rpt', {})
    data = {"me": ['read'], "logout": ["read"]}
    data.update({permission['rsname'].lower().split("_")[0]: permission.get('scopes', []) for permission in rpt.get('authorization', {}).get('permissions', [])})
    data['includes'] = rpt.get('includes', '')
    data['excludes'] = rpt.get('excludes', '')
    return data


async def get_resource_operation(method, path):
    pathparams = path.split('/')
    resource = pathparams[2].lower()
    operation = {'post': 'create', 'put': 'update', 'get': 'read', 'delete': 'delete'}.get(method.lower())
    if pathparams[-1] == "":
        pathparams = pathparams[:-1]
    if method.lower() == 'post' and len(pathparams) == 4 and pathparams[3]:
        operation = pathparams[3].lower()
    elif method.lower() == 'post' and len(pathparams) == 5:
        operation = pathparams[4].lower()
    elif method.lower() == 'get' and len(pathparams) == 5:
        operation = pathparams[4].lower()

    return resource, operation


async def has_permission(method:str, path:str):
    permissions = await get_permission()
    resource, operation = await get_resource_operation(method, path)
    # print(method, resource, operation, permissions, True if resource in permissions and operation in permissions[resource] else False)
    # return True
    return True if resource in permissions and operation in permissions[resource] else False


@app.middleware('http')
async def authMiddleware(request: fastapi.Request, call_next):
    # print(framework.ctx['tenantObj'].id, framework.ctx['tenantObj'].auth)
    response = fastapi.Response(None, 403)
    return await call_next(request)
    if request.url.path in ['/docs', '/openapi.json', '/api/login',
                            '/api/cyberutils/dummy/sendSlackMsg'] + framework.settings.noauth_urls:
        return await call_next(request)

    cookie = request.cookies.get(cookie_name, None)
    if not cookie:
        redirect_url = f'https://{request.base_url.hostname}/auth/realms/{framework.ctx["tenant"]}/protocol/openid-connect/auth?client_id={framework.ctx["tenant"]}client&response_type=code&redirect_uri={framework.ctx["oauth_redirect"]}&scope=email openid&state=123'
        response = fastapi.responses.JSONResponse({'url': redirect_url}, 401)
        # response = fastapi.responses.RedirectResponse(redirect_url)
        # response.set_cookie(key="framework_url", value=request.url)
    elif cookie:
        if await has_permission(request.method, request.scope['path']):
            response: fastapi.responses.Response = await call_next(request)

    # JWT encode if enabled and key available
    if framework.settings.enableJWTEncode and private_key:
        body = b""
        async for section in response.body_iterator:
            body += section
        resp_body = body.decode('utf-8')
        resp_body = json.loads(resp_body)
        content = jwt.encode(resp_body, private_key, algorithm='RS256')
        response.headers['content-length'] = str(len(content))
        return fastapi.responses.Response(content=content,
                                          status_code=response.status_code,
                                          headers=dict(response.headers),
                                          media_type=response.media_type)

    return response    


@app.middleware('http')
async def contextMiddleware(request: fastapi.Request, call_next):
    data = {}
    data['domain'] = request.base_url
    data['tenantObj'] = framework.tenant.Tenant()
    tenant = request.base_url.hostname.split('.')[0]
    if framework.settings.domain_mapping and request.base_url.hostname in framework.settings.domain_mapping:
        tenant = framework.settings.domain_mapping[request.base_url.hostname].split('.')[0]
    data['tenant'] = tenant
    data['oauth_redirect'] = f'{request.base_url}api/login'.replace('http://', 'https://')
    cookie_id = request.cookies.get(cookie_name, None)
    if cookie_id:
        rIns = await framework.redispool.get_redis_connection()
        cookie = await rIns.hget("CookieStore", cookie_id)
        if cookie:
            if isinstance(cookie, bytes):
                cookie = cookie.decode()
            data['rpt'] = json.loads(base64.urlsafe_b64decode(cookie.split('.')[1]+'=====').decode())

    _starlette_context_token: contextvars.Token = framework.context._request_scope_context_storage.set(data)
    try:
        resp = await call_next(request)
    except Exception as error:
        print(error)
        """
        Exception error
        """
        errFormat = '''Error:
        Stack Trace:
        %s
        ''' % (traceback.format_exc())
        print(errFormat)
        status, id = await createInternalErrorMessage(traceback.format_exc())
        resp_message = "Internal Error"
        if status:
            resp_message += ":- %s" % id
        response = fastapi.responses.JSONResponse(resp_message, 500)
        # response = fastapi.Response(resp_message, 500)
        return response
    framework.context._request_scope_context_storage.reset(_starlette_context_token)
    return resp


@app.get("/api/login/{subrealm:path}")
async def login(request: fastapi.Request, subrealm: typing.Optional[str], code: typing.Optional[str] = None):
    tenant = framework.ctx["tenant"]
    realm = tenant + subrealm if subrealm else tenant
    if code:
        # Connect to Keycloak and get the client secret
        # 1. Connect to master realm and get access token (Login)
        # 2. Get the Id of the client
        # 3. With the Id get the client secret
        resp = None
        with httpx.Client(verify=False) as client:
            login_data = {
                "client_id": "admin-cli",
                "username": KEYCLOAK_ADMIN,
                "password": KEYCLOAK_ADMIN_PASSWORD,
                "grant_type": "password"
            }
            loginUrl = f'https://{request.base_url.hostname}/auth/realms/master/protocol/openid-connect/token'
            master_login_resp = client.post(loginUrl, data=login_data)
            # print('Keycloak Login response:', master_login_resp.text)
            auth_resp = master_login_resp.json()

            clientIdUrl = f'https://{request.base_url.hostname}/auth/admin/realms/{realm}/clients?clientId={realm}client'
            headers = {
                "Authorization": f'Bearer {auth_resp["access_token"]}'
            }
            client_id_resp = client.get(clientIdUrl,headers=headers)
            # print('Client Id Response:',client_id_resp.text)
            clientid_resp = client_id_resp.json()
            
            clientSecretUrl = f'https://{request.base_url.hostname}/auth/admin/realms/{realm}/clients/{clientid_resp[0]["id"]}/client-secret'
            client_secret_resp = client.get(clientSecretUrl,headers=headers)
            # print('Client Secret Response:',client_secret_resp.status_code)
            clientsecret_resp = client_secret_resp.json()

        # Get Access token for the loggedin user
        url = f'https://{request.base_url.hostname}/auth/realms/{realm}/protocol/openid-connect/token'
        data = {
            'grant_type': 'authorization_code',
            'client_id': f'{realm}client',
            'client_secret': clientsecret_resp['value'],
            'redirect_uri': framework.ctx["oauth_redirect"],
            'code': code
        }
        if subrealm:
            data['redirect_uri'] += f'/{subrealm}'
        resp = httpx.post(url, data=data, verify=False)
        # print("Token:", resp.status_code, resp.text)
        resp = resp.json()

        # Using the access token obtained above, get the RPT token
        data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:uma-ticket",
            "audience": f'{realm}client',
        }
        headers = {"Authorization": f'Bearer {resp["access_token"]}'}
        resp = httpx.post(url, data=data, headers=headers, verify=False)
        # print("RPT Token:", resp.status_code, resp.text)
    else:
        auth: str = request.headers.get('Authorization')
        if auth and auth.startswith("Basic"):
            cred = auth.split(" ")[1]
            userpass = base64.b64decode(cred).decode().split(":")
            url = f'https://{request.base_url.hostname}/auth/realms/{realm}/protocol/openid-connect/token'
            data = {
                'grant_type': 'client_credentials',
                'client_id': userpass[0],
                'client_secret': userpass[1],
                "scope":"email"
            }
            resp = httpx.post(url, data=data, verify=False)
            # print("Token:", resp.status_code, resp.text, data)

            if resp.status_code / 100 == 2:
                headers = {"Authorization": f'Bearer {resp.json()["access_token"]}'}
                # Using the access token obtained above, get the RPT token
                data = {
                    "grant_type": "urn:ietf:params:oauth:grant-type:uma-ticket",
                    "audience": userpass[0],
                }
                resp = httpx.post(url, data=data, headers=headers, verify=False)
                # print("RPT Token:", resp.status_code, resp.text)
        else:
            resp = None

    if not code:
        response = fastapi.responses.JSONResponse({"status": "Logged in Successfully"}, 200)
    else:
        # redirect_url = request.cookies.get("framework_url", "/api")
        redirect_url = "/"
        response = fastapi.responses.RedirectResponse(redirect_url)
    if resp and resp.status_code / 100 == 2:
        # Writing cookie details to redis for reducing cookie size
        # todo:- need to add redis-connection pool instead of opening every time
        cookie_id = str(uuid.uuid4())
        rIns = await framework.redispool.get_redis_connection()
        await rIns.hset("CookieStore", cookie_id, resp.json()["access_token"])
        response.set_cookie(cookie_name, cookie_id)
    else:
        if not code:
            response = fastapi.responses.JSONResponse({"status": "Invalid Credentials"}, 401)

    return response


@app.get("/api/logout")
async def logout(request: fastapi.Request):
    rpt = framework.context.context.get('rpt', {})
    usertype = rpt.get('usertype', '')
    tenant = framework.ctx['tenant']
    realm = tenant + 'iobud' if 'bud' in usertype.lower() else tenant
    redirect_url = f"https://{request.base_url.hostname}/auth/realms/{realm}/protocol/openid-connect/logout?redirect_uri=https%3A%2F%2F{request.base_url.hostname}%2Fauth%2Fadmin%2F{realm}%2Fconsole%2F%23%2Fforbidden"
    response = fastapi.responses.JSONResponse({'url': redirect_url}, 401)
    cookie_id = request.cookies.get(cookie_name, None)
    cookie = ""
    if cookie_id:
        rIns = await framework.redispool.get_redis_connection()
        if await rIns.hexists("CookieStore", cookie_id):
            cookie = await rIns.hget("CookieStore", cookie_id)
            if cookie and isinstance(cookie, bytes):
                cookie = cookie.decode()
        await rIns.hdel("CookieStore", cookie_id)
    response.delete_cookie(cookie_name)
    return response


@app.get("/api/me")
async def me():
    rpt = framework.context.context.get('rpt', {})
    me = {'permissions': await get_permission(), 'given_name': rpt.get('given_name', '-'),
          'family_name': rpt.get('family_name', '-'), 'email': rpt.get('email', '-')}
    # adding user's custom attributes if available
    customattribs = framework.settings.custom_attributes
    if customattribs:
        for cs in customattribs:
            csvalue = rpt.get(cs, '')
            if csvalue:
                me[cs] = csvalue
    return me
