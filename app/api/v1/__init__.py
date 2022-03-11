from app.api.v1.device import device_router
from app.api.v1.connect import connect_router
from app.api.v1.info import info_router
from app.api.v1.command import command_router
from fastapi import APIRouter

api_router=APIRouter()
api_router.include_router(device_router, prefix="/device")
api_router.include_router(connect_router, prefix="/connect")
api_router.include_router(info_router, prefix="/info")
api_router.include_router(command_router, prefix="/command")