from fastapi import HTTPException


class ServiceAnalyticsExceptions(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args):
        super().__init__(self.detail, *args)


class ObjectNotFoundException(ServiceAnalyticsExceptions):
    detail = "Объект не найден"


class TransactionNotFoundException(ServiceAnalyticsExceptions):
    detail = "Транзакция не найдена"


class ServiceAnalyticsHTTPExceptions(HTTPException):
    status_code = 500
    detail = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class TransactionNotFoundHTTPException(ServiceAnalyticsHTTPExceptions):
    status_code = 404
    detail = "Транзакция не найдена"
