

class BaseSession(object):

    def __init__(self, client, status, session_key):
        self._client = client
        self._status = status
        self._session_key = session_key

    def get_status(self):
        return self._status

    def get_session_key(self):
        return self._session_key
