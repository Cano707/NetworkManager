from app.models.router.cisco import models as cisco_router_models
from app.models.router.cisco import autodetect as cisco_autodetect_model
from app.models.router.cisco import CiscoBaseRouter

vendor_model_mapping={
    "cisco": cisco_router_models
}

autodetect_vendor_mapping={
    "cisco": {"func": CiscoBaseRouter.autodetect, "models": cisco_autodetect_model}
}