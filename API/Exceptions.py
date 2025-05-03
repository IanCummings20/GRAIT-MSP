class InvalidAuthentication(Exception):
    def __init__(self, message):
        super().__init__(message)

class BadRequestError(Exception):
    def __init__(self, message):
        super().__init__(message)
        
class NoConfigError(Exception):
    def __init__(self):
        super().__init__("No config file set! Set the config file at initialization or using the .set_config() method!")
        
class ParseError(Exception):
    def __init__(self, message):
        super().__init__(message)