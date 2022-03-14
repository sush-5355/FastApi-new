from SocialSwag_enum import *
from SocialSwag_model import *
import fastapi

router = fastapi.APIRouter(prefix='/user')

@router.post('/loginWithPassword', tags=['User'])
async def UserloginWithPassword(data: loginWithPasswordParams):
    ...