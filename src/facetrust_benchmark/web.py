from __future__ import annotations

import argparse
import asyncio
import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from facetrust_benchmark import __version__
from facetrust_benchmark.deepfake_detector import warm_detector
from facetrust_benchmark.detector_storage import detect_upload
from facetrust_benchmark.settings import STATIC_DIR


@asynccontextmanager
async def lifespan(_app: FastAPI) -> Any:
    await asyncio.to_thread(warm_detector)
    yield

app = FastAPI(
    title="FaceTrust Deepfake Detector",
    version=__version__,
    description="Image deepfake detection and benchmark demo console.",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.middleware("http")
async def no_cache_for_static(request: Any, call_next: Any) -> Any:
    response = await call_next(request)
    if request.url.path == "/" or request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["Pragma"] = "no-cache"
    return response


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse((STATIC_DIR / "index.html").read_text(encoding="utf-8"))


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "FaceTrust Deepfake Detector",
        "version": __version__,
        "task": "image-deepfake-detection",
        "engine": "ai-vision-core",
    }


@app.post("/api/detect", status_code=200)
async def detect(
    image: UploadFile = File(...),
) -> JSONResponse:
    try:
        return JSONResponse(await detect_upload(image))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Detector failed: {type(exc).__name__}: {exc}",
        ) from exc


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Any, exc: HTTPException) -> JSONResponse:
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)


def main() -> None:
    import uvicorn

    parser = argparse.ArgumentParser(description="Start FaceTrust Deepfake Detector web.")
    parser.add_argument("--host", default=os.getenv("FACETRUST_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("FACETRUST_PORT", "8000")))
    args = parser.parse_args()
    uvicorn.run("facetrust_benchmark.web:app", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
