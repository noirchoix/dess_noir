from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.logging import configure_logging
from routers.dess import router as dess_router

configure_logging()
app = FastAPI(title='DESS Bridge Physics Lab API', version='1.0.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, 'http://localhost:5173', 'http://127.0.0.1:5173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(dess_router)

@app.get('/')
def root():
    return {'ok': True, 'service': 'DESS Bridge Physics Lab API', 'docs': '/docs'}

@app.get("/__routes")
def routes_debug():
    return {
        "loaded_main": __file__,
        "routes": sorted([getattr(route, "path", "") for route in app.routes]),
    }
