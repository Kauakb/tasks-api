# turns every error into the same JSON shape, with the right HTTP status:
# {"error": "CODE", "message": "readable text"} (+ "fields" for 422)
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from services import ConflictError, NotFoundError

logger = logging.getLogger(__name__)


def error_response(status: int, code: str, message: str, **extra) -> JSONResponse:
    return JSONResponse(
        status_code=status, content={"error": code, "message": message, **extra}
    )


async def not_found(request: Request, exc: NotFoundError) -> JSONResponse:
    return error_response(404, "NOT_FOUND", str(exc))


async def conflict(request: Request, exc: ConflictError) -> JSONResponse:
    return error_response(409, "CONFLICT", str(exc))


# loc says where the error is, e.g. ("body", "confidence") or ("path", "problem_id")
def field_name(error: dict) -> str:
    if error["type"] == "json_invalid":
        return "body"
    return ".".join(str(part) for part in error["loc"][1:]) or str(error["loc"][0])


async def validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    fields = [
        {"field": field_name(error), "message": error["msg"]} for error in exc.errors()
    ]
    return error_response(
        422, "VALIDATION_ERROR", "Request validation failed", fields=fields
    )


# errors raised by the framework itself: unknown route (404), wrong method (405)
async def http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    if exc.status_code == 404:
        response = error_response(
            404, "NOT_FOUND", f"Route {request.url.path} not found"
        )
    elif exc.status_code == 405:
        response = error_response(
            405,
            "METHOD_NOT_ALLOWED",
            f"Method {request.method} not allowed on {request.url.path}",
        )
    else:
        response = error_response(exc.status_code, "HTTP_ERROR", str(exc.detail))
    # keeps headers like "Allow: GET" on a 405
    response.headers.update(exc.headers or {})
    return response


# anything unexpected: the details go to the log, never to the response
async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unexpected error on %s %s", request.method, request.url, exc_info=exc)
    return error_response(500, "INTERNAL_ERROR", "Internal server error")


def register(app: FastAPI) -> None:
    app.add_exception_handler(NotFoundError, not_found)
    app.add_exception_handler(ConflictError, conflict)
    app.add_exception_handler(RequestValidationError, validation_error)
    app.add_exception_handler(StarletteHTTPException, http_error)
    app.add_exception_handler(Exception, unexpected_error)
