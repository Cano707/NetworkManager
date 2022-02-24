from app.api.v1.device import device_router
from app.api.v1.connect import connect_router
from fastapi import APIRouter

api_router=APIRouter()
api_router.include_router(device_router, prefix="/device")
api_router.include_router(connect_router, prefix="/connect")