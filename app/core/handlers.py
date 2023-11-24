import app.models

class Handler:
    """Stores netmiko connection handlers to make them accessible from different locations."""
    handlers = {key:dict() for key in app.models.device_vendor_mapping.keys()}
            
    @classmethod
    def get_handlers(cls):
        return cls.handlers