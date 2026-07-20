from src.repositories.config import configure_database
from src.modules.rag import configure_settings

def configure_app():
    configure_settings()
    configure_database()