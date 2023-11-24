"""Defines the about routes"""
from fastapi import HTTPException
import app.models
from netmiko.ssh_dispatcher import CLASS_MAPPER


class About:
    """Represents API endpoints for `/api/v1/about/`."""
        
    @classmethod
    def supported_devices(cls):
        """Returns supported device kinds.

        Returns:
            dict: List of supported device kinds
        """
        devices=list(app.models.device_vendor_mapping.keys())
        return {"detail": devices}

    @classmethod    
    def supported_vendors(cls, device_kind: app.models.DeviceKinds):
        """Returns supported vendors for `device_kind`

        Args:
            device_kind (app.models.DeviceKinds): Supported device kinds

        Returns:
            dict: List of supported vendors for `device_kind`
        """
        vendors=list(app.models.device_vendor_mapping[device_kind.value].keys())
        return {"detail": vendors}
    
    @classmethod
    def supported_vendor_models(cls, device_kind: app.models.DeviceKinds, 
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
        if vendor.value not in app.models.device_vendor_mapping[device_kind.value].keys():
            raise HTTPException(status_code=406, detail="VendorNotSupportedException")
        supported_models=list(app.models.device_vendor_mapping[device_kind.value][vendor.value].keys())
        return {"detail": supported_models}
    
    @classmethod
    def device_types_netmiko(cls, connection_type: str):
        connection_types = ["ssh", "serial", "telnet"]
        
        if connection_type not in connection_types:
            raise HTTPException(status_code=406, detail="Connection type not supported")
        
        device_types = []
        
        keys_total = CLASS_MAPPER.keys()
        
        for key in keys_total:
            if connection_type in key:
                device_types.append(key)
                
        return {"detail": device_types}