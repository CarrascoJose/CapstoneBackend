

class URLDoesNotExist(Exception):

    def __init__(self, message="Given Url does not exist"):
        self.message = message
        super().__init__(self.message)
        
        