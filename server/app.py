"""Re-export the FastAPI app for openenv_serve deployment mode."""

from tasks.server.app import app  # noqa: F401
from tasks.server.app import main as _main


def main(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run the environment server locally."""
    _main(host=host, port=port)


if __name__ == "__main__":  # pragma: no cover
    main()
