import app.models

class Handlers:
    """Stores netmiko handlers to make them accessible
    from differnet locations.
    """
    handlers={key:dict() for key in app.models.device_vendor_mapping.keys()}
            
    @classmethod
    def get_handlers(cls):
        return cls.handlers