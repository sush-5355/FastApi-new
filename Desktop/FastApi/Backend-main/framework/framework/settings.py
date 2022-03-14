import typing
import pydantic
import enum


class MultiTenancyMode(str, enum.Enum):
    SingleServerSingleDb = 'SingleServerSingleDb'
    SingleServerMultiDb = 'SingleServerMultiDb'
    MultiServerSingleDb = 'MultiServerSingleDb'
    MultiServerMultiDb = 'MultiServerMultiDb'


class Settings(pydantic.BaseSettings):
    app_name: str = "SocialSwag"
    cookie_name: str = "SocialSwag"

    # Keycloak Auth Server
    keycloak_url: pydantic.AnyHttpUrl = 'https://localhost:8443/auth/'
    keycloak_admin: str = 'admin'
    keycloak_password: str = 'Pa55w0rd@897'
    keycloak_dbpassword: str = 'Pa55w0rd@897'

    # Default TenantName
    default_tenant: str = ''

    # Redis cluster
    redis_url: pydantic.RedisDsn = "redis://localhost:6379"

    # Configuration parameters
    config_params: typing.Dict[str, typing.Any] = {}

    # DB Multitenancy model
    db_multi_tenancy_model: MultiTenancyMode = MultiTenancyMode.SingleServerSingleDb
    db_name: str = "framework"
    db_urls: typing.Dict[str, typing.List[pydantic.AnyUrl]] = {
                                            "mongo": [
                                                    "mongodb://localhost"
                                                    ],
                                            "elastic": [
                                                    "https://admin:admin@localhost:9200"
                                                    ]
                                            }
    kibana_urls: typing.Dict[str, typing.List[pydantic.AnyUrl]] = {
        "kibana": [
            "http://localhost:5601/"
        ]
    }
    domain_mapping: typing.Dict[str, str] = {}
    redis_cluster: bool = False
    report_s3_upload = False
    aws_access_key_id: str = ''
    aws_secret_access_key: str = ''
    enableJWTEncode: bool = False
    JWTPath: str = ''

    # Product name used for indexing
    product_name: str = 'socialswag'

    # user Custom Attributes
    custom_attributes: typing.List[str] = []

    # NoAuth URLS
    noauth_urls: typing.List[str] = []

    # Azure connection string to store product images
    azure_conn_str: str = ''

    # Payments gateways
    payment_gateways: typing.Dict[str, typing.Any] = {}

    @property
    def redis(self):
        import aioredis
        return aioredis.from_url(self.redis_url)

    def db_url(self, db):
        if self.db_multi_tenancy_model == MultiTenancyMode.SingleServerSingleDb or self.db_multi_tenancy_model == MultiTenancyMode.SingleServerMultiDb:
            return self.db_urls.get(db, [])[0]

    class Config:
        env_file = '.env'


settings = Settings()
