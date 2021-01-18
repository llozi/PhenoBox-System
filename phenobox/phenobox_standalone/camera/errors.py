class CameraError(Exception):
    def __init__(self, message, detail=None):
        self.message = message
        if hasattr(self, 'detail'):
            self.detail = detail

    def __str__(self):
        if hasattr(self, 'detail'):
          return '%s - %s' % (self.message, self.detail)
        else:
          return '%s' % self.message


class CaptureError(CameraError):
    def __init__(self, message, detail=None):
        super(CaptureError, self).__init__(message, detail)

class ConnectionError(CameraError):
    def __init__(self, message, detail=None):
        super(ConnectionError, self).__init__(message, detail)

