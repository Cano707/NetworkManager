from app.api.v1.device import device_router
from app.api.v1.connect import connect_router
from app.api.v1.about import about_router
from app.api.v1.command import command_router
from fastapi import APIRouter

# Add subroutes to main API route
api_router=APIRouter()
api_router.include_router(device_router, prefix="/device")
api_router.include_router(connect_router, prefix="/connect")
api_router.include_router(about_router, prefix="/about")
api_router.include_router(command_router, prefix="/command")


#TODO - Export classes to core