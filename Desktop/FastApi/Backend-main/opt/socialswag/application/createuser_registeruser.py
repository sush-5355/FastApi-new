from SocialSwag_enum import *
from SocialSwag_model import *
import fastapi

router = fastapi.APIRouter(prefix='/createuser')

@router.post('/registerUser', tags=['CreateUser'])
async def CreateUserregisterUser(data: registerUserParams):
    doc = {"name" : data.name,
            "email" : data.email,
            "country" : data.country}

    return await CreateUser(**doc).create()