"""Defines the about routes"""
from fastapi import APIRouter, HTTPException
from fastapi_utils.cbv import cbv
from app.core.about_backend import About
import app.models

about_router=APIRouter()

@cbv(about_router)
class AboutAPI:
    """Represents API endpoints for `/api/v1/about/`."""
        
    @about_router.get("/devices")
    def supported_devices(self):
        """Returns supported device kinds.

        Returns:
            dict: List of supported device kinds
        """
        print("[i] AboutAPI - supported_devices: Request received")
        try:
            return About.supported_devices()
        except:
            raise
    
    @about_router.get("/devices/{device_kind}")
    def supported_vendors(self, device_kind: app.models.DeviceKinds):
        """Returns supported vendors for `device_kind`

        Args:
            device_kind (app.models.DeviceKinds): Supported device kinds

        Returns:
            dict: List of supported vendors for `device_kind`
        """
        print("[i] AboutAPI - supported_vendors: Request received")
        try:
            return About.supported_vendors(device_kind=device_kind)
        except:
            raise
    
    @about_router.get("/devices/{device_kind}/{vendor}")
    def supported_vendor_models(self, device_kind: app.models.DeviceKinds, 
                                vendor: app.models.Vendors):
        """Returns supported models for `vendor` of `device_kind`

        Args:
            device_kind (app.models.DeviceKinds): Supported device kinds
            vendor (app.models.Vendors): Supported vendors

        Raises:
            VendorNotSupportedException: Raise of `vendor` is not supported

        Returns:
            dict: List of supported models for `vendor` of `device_kind`
        """
        print("[i] AboutAPI - supported_vendor_models: Request received")
        try:
            return About.supported_vendor_models(device_kind=device_kind, vendor=vendor)
        except:
            raise

    @about_router.get("/netmiko/device_types")
    def device_types_netmiko(self, connection_type: str):
        print("[i] AboutAPI - device_types_netmiko: Request received")
        try:
            return About.device_types_netmiko(connection_type)
        except:
            raise
        