"""FastAPI app entrypoint for the Navis web environment."""

from __future__ import annotations

import uvicorn
from fastapi.responses import JSONResponse

from ..models import NavisWebAction, NavisWebObservation
from ..openenv_compat import create_app
from .navis_web_environment import NavisWebEnvironment

app = create_app(NavisWebEnvironment, NavisWebAction, NavisWebObservation, env_name="navis_web_env")


@app.get("/")
def root() -> JSONResponse:
    """Small landing response so the Space homepage isn't a 404."""

    return JSONResponse(
        {
            "name": "navis_web_env",
            "status": "ok",
            "message": "Navis Web Env API is running.",
            "endpoints": ["/health", "/reset", "/step", "/state", "/metadata", "/schema"],
        }
    )


def main(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run the environment server locally."""

    uvicorn.run("server.app:app", host=host, port=port, reload=False)


if __name__ == "__main__":  # pragma: no cover
    main()
