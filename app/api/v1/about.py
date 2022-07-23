from fastapi import APIRouter, HTTPException
from fastapi_utils.cbv import cbv
import app.models

about_router=APIRouter()

@cbv(about_router)
class AboutCBV:
    """Represents API endpoints for `/api/v1/about/`."""
    @about_router.get("/")
    def supported_devices(self):
        """Returns supported device kinds.

        Returns:
            dict: List of supported device kinds
        """
        devices=list(app.models.device_vendor_mapping.keys())
        return {"detail": devices}
    
    @about_router.get("/{device_kind}")
    def supported_vendors(self, device_kind: app.models.DeviceKinds):
        """Returns supported vendors for `device_kind`

        Args:
            device_kind (app.models.DeviceKinds): Supported device kinds

        Returns:
            dict: List of supported vendors for `device_kind`
        """
        vendors=list(app.models.device_vendor_mapping[device_kind.value].keys())
        return {"detail": vendors}
    
    @about_router.get("/{device_kind}/{vendor}")
    def supported_vendor_models(self, device_kind: app.models.DeviceKinds, vendor: app.models.Vendors):
        """Returns supported models for `vendor` of `device_kind`

        Args:
            device_kind (app.models.DeviceKinds): Supported device kinds
            vendor (app.models.Vendors): Supported vendors

        Raises:
            VendorNotSupportedException: Raise of `vendor` is not supported

        Returns:
            dict: List of supported models for `vendor` of `device_kind`
        """
        if vendor.value not in app.models.device_vendor_mapping[device_kind.value].keys():
            raise HTTPException(status_code=406, detail="VendorNotSupportedException")
        supported_models=list(app.models.device_vendor_mapping[device_kind.value][vendor.value].keys())
        return {"detail": supported_models}