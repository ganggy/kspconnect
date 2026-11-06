"""Entry point to run the FastAPI REST / OpenAPI Server."""

import uvicorn
from src.config import REST_HOST, REST_PORT

if __name__ == "__main__":
    print(f"🚀 Starting KSP Hospital AI Gateway on http://{REST_HOST}:{REST_PORT}")
    print(f"📖 OpenAPI Docs available at: http://{REST_HOST}:{REST_PORT}/docs")
    uvicorn.run("src.server.rest_app:app", host=REST_HOST, port=REST_PORT, reload=False)
