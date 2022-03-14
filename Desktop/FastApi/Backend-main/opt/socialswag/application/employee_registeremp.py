from SocialSwag_enum import *
from SocialSwag_model import *
import fastapi

router = fastapi.APIRouter(prefix='/employee')

@router.post('/registerEmp', tags=['Employee'])
async def EmployeeregisterEmp(data: registerEmpParams):
    ...