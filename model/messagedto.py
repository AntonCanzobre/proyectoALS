# MessageDTO
from datetime import datetime
class MessageDto:
    def __init__(self, msg):
        self._msg = msg
        self._time = datetime.now()
    @property
    def msg(self):
        return self._msg
    @property
    def time(self):
        return self._time
    def __str__(self):
        return f"{self.time}: \"{self.msg}\""
    