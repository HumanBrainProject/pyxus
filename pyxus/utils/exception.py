class NexusException(Exception):
    """Exception raised when a Nexus call fails

    Attributes:
    http_status_code -- code returned by the API
    message -- message for the exception
    """
    def __init__(self, http_status_code, message):
        self.http_status_code = http_status_code
        self.message = message
