from ast import Name
from SocialSwag_enum import *
from SocialSwag_model import *
import fastapi

router = fastapi.APIRouter(prefix='/createuser')

@router.post('/verifyUser', tags=['CreateUser'])
async def CreateUserverifyUser(data: verifyUserParams):
    print(data.id)
    id = data.id
    obj = {"_id": id}
    try:

        olduserdata = await CreateUser().get(id=id)
        return ({"olduserdata": olduserdata})
    except IndexError as index:
        print(index)

        #print("error")
        
