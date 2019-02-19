from BluenetLib.lib.core.BluenetCore import BluenetCore

class Bluenet(BluenetCore):
    """
    This is a wrapper class to expose an API through the BluenetLib package.
    """
    
    def __init__(self, catchSIGINT=True):
        super().__init__(catchSIGINT)

