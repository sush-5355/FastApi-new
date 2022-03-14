
import framework.elasticmodel
import framework.queryparams
import framework.types
from SocialSwag_enum import *
from SocialSwag_model import *
import fastapi
router = fastapi.APIRouter()















@router.post('/employee', response_model=Employee, tags=['Employee'])
async def create(inputObj: EmployeeCreate):
    
    return await inputObj.create()





@router.put('/employee', response_model=Employee, tags=['Employee'])
async def update(inputObj: Employee):
    
    
    return await inputObj.update()


@router.get('/employee/{id}', response_model=Employee, tags=['Employee'])
async def get(id: str):
    return await Employee.get(id)


@router.get('/employee', response_model=EmployeeGetResp, tags=['Employee'])
async def get_all(response: fastapi.Response, params = fastapi.Depends(framework.queryparams.QueryParams)):
    if params.download:
        response.headers['Content-Disposition'] = f'attachment; filename="employee.html"'
    return await Employee.get_all(params)


@router.delete('/employee/{id}', tags=['Employee'])
async def delete(id: str):
    return await Employee().delete(id)


@router.delete('/employee/{id}/bulkdelete', tags=['Employee'])
async def bulkdelete(response: fastapi.Response, id: str, inputobjs: EmployeeBulkDelete):
    return await Employee().bulkdelete(inputobjs.ids)





@router.post('/createuser', response_model=CreateUser, tags=['CreateUser'])
async def create(inputObj: CreateUserCreate):
    
    return await inputObj.create()





@router.put('/createuser', response_model=CreateUser, tags=['CreateUser'])
async def update(inputObj: CreateUser):
    
    
    return await inputObj.update()


@router.get('/createuser/{id}', response_model=CreateUser, tags=['CreateUser'])
async def get(id: str):
    return await CreateUser.get(id)


@router.get('/createuser', response_model=CreateUserGetResp, tags=['CreateUser'])
async def get_all(response: fastapi.Response, params = fastapi.Depends(framework.queryparams.QueryParams)):
    if params.download:
        response.headers['Content-Disposition'] = f'attachment; filename="createuser.html"'
    return await CreateUser.get_all(params)


@router.delete('/createuser/{id}', tags=['CreateUser'])
async def delete(id: str):
    return await CreateUser().delete(id)


@router.delete('/createuser/{id}/bulkdelete', tags=['CreateUser'])
async def bulkdelete(response: fastapi.Response, id: str, inputobjs: CreateUserBulkDelete):
    return await CreateUser().bulkdelete(inputobjs.ids)































@router.post('/en', response_model=EN, tags=['EN'])
async def create(inputObj: ENCreate):
    
    return await inputObj.create()





@router.put('/en', response_model=EN, tags=['EN'])
async def update(inputObj: EN):
    
    
    return await inputObj.update()


@router.get('/en/{id}', response_model=EN, tags=['EN'])
async def get(id: str):
    return await EN.get(id)


@router.get('/en', response_model=ENGetResp, tags=['EN'])
async def get_all(response: fastapi.Response, params = fastapi.Depends(framework.queryparams.QueryParams)):
    if params.download:
        response.headers['Content-Disposition'] = f'attachment; filename="en.html"'
    return await EN.get_all(params)


@router.delete('/en/{id}', tags=['EN'])
async def delete(id: str):
    return await EN().delete(id)


@router.delete('/en/{id}/bulkdelete', tags=['EN'])
async def bulkdelete(response: fastapi.Response, id: str, inputobjs: ENBulkDelete):
    return await EN().bulkdelete(inputobjs.ids)


