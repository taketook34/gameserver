

class CageIsFilledError(Exception):
    
    def __init__(self, message="An error occurred"):
        # Call the base class constructor to initialize the message
        super().__init__(message)

class FileIsExists(Exception):

    def __init__(self, message="File is exists!"):
        # Call the base class constructor to initialize the message
        super().__init__(message)