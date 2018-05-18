import logging


class BaseUtility:
    _loggername = None

    def __init__(self, loglevel=logging.INFO):
        if self._loggername is None:
            raise DevError("_loggername attribute should be set.")
        logging.basicConfig()
        self._logger = logging.getLogger(self._loggername)
        self._logger.setLevel(loglevel)



class DevError(Exception):
    pass
