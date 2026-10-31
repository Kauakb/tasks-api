# the product rules. This layer knows nothing about HTTP: it raises domain
# errors, and errors.py turns them into HTTP responses


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass
