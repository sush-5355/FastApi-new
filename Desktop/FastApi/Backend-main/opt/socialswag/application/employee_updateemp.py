from SocialSwag_enum import *
from SocialSwag_model import *
import fastapi

router = fastapi.APIRouter(prefix='/employee')

@router.post('/updateEmp', tags=['Employee'])
async def EmployeeupdateEmp(data: updateEmpParams):
    ...