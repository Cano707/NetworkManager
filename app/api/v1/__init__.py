from app.api.v1.device_manager import device_router
from app.api.v1.connection_manager import connect_router
from app.api.v1.about import info_router
from app.api.v1.commander import command_router
from fastapi import APIRouter

# Add subroutes to main API route 
api_router=APIRouter()
api_router.include_router(device_router, prefix="/device-manager")
api_router.include_router(connect_router, prefix="/connection-manager")
api_router.include_router(info_router, prefix="/about")
api_router.include_router(command_router, prefix="/commander")

#TODO - Export classes to core