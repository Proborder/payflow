from fastapi import HTTPException


class ProviderExceptions(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args):
        super().__init__(self.detail, *args)


class ProviderEmptyResponseExceptions(ProviderExceptions):
    detail = "Пустой ответ от провайдера"


class ProviderConnectionExceptions(ProviderExceptions):
    detail = "Провайдер недоступен"


class ServicePaymentExceptions(Exception):
    detail = "Неожиданная ошибка"

    def __init__(self, *args):
        super().__init__(self.detail, *args)


class ObjectNotFoundException(ServicePaymentExceptions):
    detail = "Объект не найден"


class PaymentNotFoundException(ServicePaymentExceptions):
    detail = "Платёж не найден"


class CircuitBreakerBlockedRequestExceptions(ServicePaymentExceptions):
    detail = "CircuitBreaker открыт. Запрос заблокирован"


class ServicePaymentHTTPExceptions(HTTPException):
    status_code = 500
    detail = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class PaymentNotFoundHTTPException(ServicePaymentHTTPExceptions):
    status_code = 404
    detail = "Платёж не найден"
