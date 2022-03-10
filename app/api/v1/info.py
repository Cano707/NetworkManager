from fastapi import APIRouter
from fastapi_utils.cbv import cbv
import app.models

info_router=APIRouter()

@cbv(info_router)
class InfoCBV:
    @info_router.get("/info/supported-devices")
    def supported_devices(self):
        devices=list(app.models.device_vendor_mapping.keys())
        return {"supported-devices": devices}
    
    @info_router.get("/info/supported-vendors/{device_kind}")
    def supported_vendors(self, device_kind: app.models.DeviceKinds):
        vendors=list(app.models.device_vendor_mapping[device_kind.value].keys())
        return {"vendors": vendors}
    
    #TODO - Importante!
    @info_router.get("/info//supported-models/{vendor}/{device_kind}")
    def supported_vendor_models(self, device_kind: app.models.DeviceKinds, vendor: app.models.Vendors):
        if device_kind.value not in app.models.device_vendor_mapping.keys():
            return {"Error": f"Device {device_kind} not supported."}
        if vendor.value not in app.models.device_vendor_mapping[device_kind.value].keys():
            return {"Error": f"Vendor {vendor} not supported."}
        supported_models=app.models.device_vendor_mapping[device_kind.value][vendor.value]
        supported_models_names=[model.__doc__ for model in supported_models]
        return {"supported-models": supported_models_names}