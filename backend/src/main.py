from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database.database import create_tables

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from .medico.router_medico import router as medico_router
from .auth.router_auth import router as auth_router

# Register routers
app.include_router(auth_router)
app.include_router(medico_router, prefix="/api")

# Create database tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": f"Bem-vindo ao {settings.app_name}",
        "version": settings.app_version,
        "status": "online"
    }


@app.get("/health")
async def health_check():
    """Health check for monitoring"""
    return {"status": "healthy"}