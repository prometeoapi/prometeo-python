

class BaseSession(object):
    """
    Base class that handles calling the API endpoints that use session keys.
    """

    def __init__(self, client, status, session_key):
        self._client = client
        self._status = status
        self._session_key = session_key

    def get_status(self):
        """
        Returns this session's status

        :rtype: str
        """
        return self._status

    def get_session_key(self):
        """
        Returns this session's session key

        :rtype: str
        """
        return self._session_key
