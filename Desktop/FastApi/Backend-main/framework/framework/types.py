import typing
import pydantic
import pydantic.utils
import cryptography.fernet
import framework
import base64
import framework.settings
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF



class Secret(str):

    @classmethod
    def __modify_schema__(cls, field_schema: typing.Dict[str, typing.Any]) -> None:
        pydantic.utils.update_not_none(field_schema, type='string', writeOnly=True, format='password')

    @classmethod
    def __get_validators__(cls) -> 'typing.CallableGenerator':
        yield cls.validate

    @classmethod
    def get_key(cls, key=None):
        hkdf = HKDF(
            algorithm=hashes.SHA256(),  # You can swap this out for hashes.MD5()
            length=32,
            salt=None,    # You may be able to remove this line but I'm unable to test
            info=None,    # You may also be able to remove this line
            backend=default_backend()
        )
        if not key and framework.ctx.exists():
            key = cls.gettenants()[0]
        password = key if key else "framework"
        return base64.urlsafe_b64encode(hkdf.derive(password.encode()))

    @classmethod
    def gettenants(cls):
        if len(framework.settings.domain_mapping):
            basedomain = framework.ctx['tenant']
            domains = list(set(list(framework.settings.domain_mapping.values()))) + list(set(list(framework.settings.domain_mapping.keys())))
            return [basedomain] + [d for d in [d.split(".")[0] for d in domains] if d != basedomain]
        else:
            return [framework.ctx['tenant']]
        # domain = framework.ctx['domain'].netloc
        # if not domain:
        #     return [framework.ctx['tenant']]
        # tenant_url = domain.split(".")[0]
        # if tenant_url == framework.ctx['tenant']:
        #     return [framework.ctx['tenant']]
        # else:
        #     return [tenant_url, framework.ctx['tenant']]

    @classmethod
    def validate(cls, value: str, config: str = None) -> 'Secret':
        if isinstance(value, cls):
            return value
        dec_key = config if isinstance(config, str) else None
        if isinstance(value, str) and not value.startswith('enc#_'):
            value = 'enc#_' + cryptography.fernet.Fernet(cls.get_key(dec_key)).encrypt(value.encode()).decode()
        return cls(value)


    def __repr__(self) -> str:
        return f"Secret('{self}')"


    def __eq__(self, other: typing.Any) -> bool:
        return isinstance(other, Secret) and self.get_secret() == other.get_secret()

    def get_secret(self,cyberTenant=None) -> str:
        if not framework.ctx.exists():
            return cryptography.fernet.Fernet(self.get_key(cyberTenant)).decrypt(self[5:].encode()).decode()
        else:
            tenants = self.gettenants()
            # print(tenants)
            if len(tenants) == 1:
                return cryptography.fernet.Fernet(self.get_key(tenants[0])).decrypt(self[5:].encode()).decode()
            exception = None
            for tenant in tenants:
                try:
                    return cryptography.fernet.Fernet(self.get_key(tenant)).decrypt(self[5:].encode()).decode()
                except Exception as e:
                    exception = str(e)
            print("Exception in decode %s" % exception)
            return self
