import datetime

# This is what the timestamp will be formatted as if one wants to put the timestamp in a file name
FORMAT_FOR_FILE_NAME = "_y%Y_m%m_d%d_h%H_m%M_s%S_us%f"

# This is a well-readable datetime format to be used when we have no character restrictions
# (like as a string in a json file)
STRING_DT_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


class Timestamp:
    """
    A class to foster code reuse when dealing with timestamps throughout the application
    The biggest reason for this was to internalize returning a filename-safe timestamp string represtation
    """

    def __init__(self):
        self._stamp = datetime.datetime.today()

    @classmethod
    def from_str(cls, timestamp: str):
        instance = Timestamp()
        instance._stamp = datetime.datetime.strptime(timestamp, STRING_DT_FORMAT)
        return instance

    def for_filename(self) -> str:
        """
        :return: a filename-safe representation of the timestamp
        """
        return self._stamp.strftime(FORMAT_FOR_FILE_NAME)

    def __str__(self):
        return self._stamp.strftime(STRING_DT_FORMAT)
