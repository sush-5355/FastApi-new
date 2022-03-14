from SocialSwag_enum import *
from SocialSwag_model import *
import fastapi

router = fastapi.APIRouter(prefix='/en')

@router.post('/Authenticate', tags=['EN'])
async def ENAuthenticate(data: AuthenticateParams):
    doc = {
        "layout" : data.layout,
        "page"  : data.page
    }

    return await EN(**doc).create()