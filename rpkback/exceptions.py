class RpkException(Exception):
    ...


class HttpException(Exception):
    code = 500
    detail = "Server error"


class ItemNotFound(HttpException):
    code = 404
    detail = "Item not found"


class ItemAlreadyExists(HttpException):
    code = 409
    detail = "Item already exists"


class FileStorageError(HttpException):
    detail = "Some problem with files"


class PackageError(HttpException):
    code = 400
    detail = "Wrong package format"


class Forbidden(HttpException):
    code = 403
    detail = "Forbidden"
