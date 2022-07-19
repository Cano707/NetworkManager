from app.models.switch.cisco import models as cisco_switch_models
from app.models.switch.cisco import autodetect as cisco_autodetect_model

vendor_model_mapping= {
    "cisco": cisco_switch_models
}

autodetect_vendor_mapping={
    "cisco": cisco_autodetect_model
}