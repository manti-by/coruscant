class CoruscantBaseException(BaseException):
    exit_code = 1


class TempReadErrorException(CoruscantBaseException):
    exit_code = 2


class PostgresConnectionErrorException(CoruscantBaseException):
    exit_code = 3


class SQLiteConnectionErrorException(CoruscantBaseException):
    exit_code = 4
