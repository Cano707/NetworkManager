from app.models.router import vendor_model_mapping as router_vendor_model_mapping
from app.models.switch import vendor_model_mapping as switch_vendor_model_mapping
from app.models.router import autodetect_vendor_mapping as router_autodetect_vendor_model_mapping
from app.models.switch import autodetect_vendor_mapping as switch_autodetect_vendor_model_mapping
from enum import Enum


# Mapping from supported devices to supported vendors
device_vendor_mapping={
    "router": router_vendor_model_mapping,
    "switch": switch_vendor_model_mapping
}

# Autodeteect mapping
autodetect_device_vendor_mapping={
    "router": router_autodetect_vendor_model_mapping,
    "switch": switch_autodetect_vendor_model_mapping
}

# Enum of supported vendors for FastAPI to use for verification.
def create_vendor_list(mapping):
    result=list()
    devices=mapping.keys()
    for device in devices:
        vendors=mapping[device].keys()
        result.extend(vendors)
    unique=list(set(result))
    return list(zip(unique, unique))

class StrEnum(str, Enum):
    """Enum where members are also (and must be) strs"""

Vendors=StrEnum("Vendors", create_vendor_list(device_vendor_mapping))

# Create a mapping from supported devices to supported devices {"cisco_ios_serial": "cisco_ios_serial", ...}
# Reason: Swagger will use the auto-generated numbers to show the choices, since the names must be shown 
# this mapping is necessary.
#CLASS_MAPPER_FOR_ENUM={name: name for _, name in enumerate(CLASS_MAPPER.keys())}

#DeviceTypesNetmiko=Enum("DeviceTypesNetmiko", CLASS_MAPPER_FOR_ENUM)
#print(DeviceTypesNetmiko.__members__)
    
    
# Represents supported devices which will be used by fastapi for verification.
DeviceKinds=StrEnum("DeviceKinds", [(key, key) for key in device_vendor_mapping.keys()])
