from app.routers.search import router as search_router
from app.routers.history import router as history_router
from app.routers.collections import router as collections_router
from app.routers.phonetics_router import router as phonetics_router

__all__ = ["search_router", "history_router", "collections_router", "phonetics_router"]
