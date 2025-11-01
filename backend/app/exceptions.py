from fastapi import Request
from fastapi.responses import JSONResponse

class DuplicateRecordError(Exception):
    def __init__(self, detail: str):
        self.detail = detail

async def duplicate_record_exception_handler(request: Request, exc: DuplicateRecordError):
    return JSONResponse(
        status_code=409,
        content={"detail": exc.detail},
    )
