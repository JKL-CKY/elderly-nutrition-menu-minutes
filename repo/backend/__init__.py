from .database import Base, engine, get_db
from . import models
from . import schemas
from .routers import elderly_router, nutrition_router, meeting_router, menu_router

models.Base.metadata.create_all(bind=engine)
