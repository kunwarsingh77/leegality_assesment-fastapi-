from fastapi import HTTPException


class NodeNotFoundError(HTTPException):
    def __init__(self, name: str):
        super().__init__(status_code=404, detail=f"Node '{name}' not found")


class DuplicateNodeError(HTTPException):
    def __init__(self, name: str):
        super().__init__(status_code=400, detail=f"Node '{name}' already exists")


class DuplicateEdgeError(HTTPException):
    def __init__(self, source: str, destination: str):
        super().__init__(
            status_code=400,
            detail=f"Edge from '{source}' to '{destination}' already exists",
        )


class NoPathError(HTTPException):
    def __init__(self, source: str, destination: str):
        super().__init__(
            status_code=404,
            detail=f"No path exists between '{source}' and '{destination}'",
        )
