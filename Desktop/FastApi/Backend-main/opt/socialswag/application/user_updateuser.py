from SocialSwag_enum import *
from SocialSwag_model import *
import fastapi

router = fastapi.APIRouter(prefix='/user')

@router.post('/updateUser', tags=['User'])
async def UserupdateUser(data: updateUserParams):
    ...