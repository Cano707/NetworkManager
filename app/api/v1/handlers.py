import app.models

class Handlers:
    handlers={key:dict() for key in app.models.device_vendor_mapping.keys()}
            
    @classmethod
    def get_handlers(cls):
        return cls.handlers