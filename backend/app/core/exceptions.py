from fastapi import Request, status
from fastapi.responses import JSONResponse

class NotFoundException(Exception):
    def __init__(self, name: str):
        self.name = name

async def not_found_exception_handler(request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": f"{exc.name} not found"},
    )
