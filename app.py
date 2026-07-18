from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from src.api.generate_questions import questions_router
from src.modules.rag import configure_settings

app = FastAPI(
    title="Current Affairs Q&A Generator",
    description="Fetches live news and generates difficulty-graded quiz questions using LLaMA 3.",
    version="1.0.0",
)


@app.on_event("startup")
async def startup():
    configure_settings()

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")
@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


app.include_router(questions_router)