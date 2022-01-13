class APIError(Exception):

    def __init__(self, message, status=400):
        self.message = message
        self.status = status
        super().__init__(self.message)
