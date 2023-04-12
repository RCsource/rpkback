class RpkException(Exception):
    ...


class HttpException(Exception):
    code = 500
    detail = "server error"


class ItemNotFound(HttpException):
    code = 404
    detail = "item not found"


class ItemAlreadyExists(HttpException):
    code = 409
    detail = "item already exists"


class FileStorageError(HttpException):
    detail = "some problem with files"


class PackageError(HttpException):
    code = 400
    detail = "wrong package format"


class Forbidden(HttpException):
    code = 403
    detail = "forbidden"
