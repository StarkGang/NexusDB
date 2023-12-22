class InvalidMongoURL(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidSQLitePath(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidPostgreSQLURL(Exception):
    def __init__(self, message):
        super().__init__(message)
