class MissingConnectionData(Exception):
    """Raised when no connection is established."""

class ConnectionError(Exception):
    """Raised when a general error occurs in the connection process."""
    
class NoSuchDeviceException(Exception):
    """Raised when device does not exist."""
    
class NoConnectionPossibleException(Exception):
    """Raised when connecting failes"""