def serve(host: str, port: int) -> None:
    """Start the local API server."""
    try:
        import uvicorn
    except ImportError as exc:
        raise RuntimeError("Install API dependencies before starting the server.") from exc

    uvicorn.run("nomad.api.server:create_app", host=host, port=port, factory=True)
