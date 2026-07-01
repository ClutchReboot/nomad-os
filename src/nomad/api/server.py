"""FastAPI server for Nomad."""

from nomad.core.conversation import ConversationService


def create_app(conversation: ConversationService | None = None):
    """Create the Nomad FastAPI app."""
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel
    except ImportError as exc:
        raise RuntimeError("Install API dependencies before starting the server.") from exc

    app = FastAPI(title="Nomad API")
    conversation_service = conversation or ConversationService()

    class ChatRequest(BaseModel):
        message: str

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/chat")
    def chat(request: ChatRequest) -> dict[str, str]:
        try:
            turn = conversation_service.handle_message(request.message)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        return {"message": turn.message, "response": turn.response}

    return app
