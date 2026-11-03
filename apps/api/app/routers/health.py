from fastapi import APIRouter, Request


router = APIRouter()


@router.get("/health")
def health(request: Request):

    agent = request.app.state.agent

    return {
        "model": agent.model,
        # None while the warmup is still running
        "model_ready": request.app.state.model_ready
    }
