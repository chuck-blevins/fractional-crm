from fastapi import FastAPI

def create_app() -> FastAPI:
    """
    Create a FastAPI instance and register a GET route at "/health" that returns {"status": "ok"}.
    """
    app = FastAPI()
    
    @app.get("/health")
    def health():
        return {"status": "ok"}
    
    return app

app = create_app()
