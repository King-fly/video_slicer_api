from .auth import router as auth_router
from .videos import router as videos_router
from .slices import router as slices_router
from .tasks import router as tasks_router

__all__ = ["auth_router", "videos_router", "slices_router", "tasks_router"]