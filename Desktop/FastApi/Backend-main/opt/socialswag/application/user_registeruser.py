from SocialSwag_enum import *
from SocialSwag_model import *
import fastapi

router = fastapi.APIRouter(prefix='/user')

@router.post('/registerUser', tags=['User'])
async def UserregisterUser(data: registerUserParams):
    ...