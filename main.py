from fastapi import FastAPI

from routes.routes_post import router as post_router
from routes.routes_get import router as get_router
from routes.routes_patch import router as patch_router
from routes.routes_put import router as put_router
from routes.routes_delete import router as delete_router

from exception.exception import integrity_exception_handler, global_exception_handler

app = FastAPI()

app.include_router(post_router)
app.include_router(get_router)
app.include_router(patch_router)
app.include_router(put_router)
app.include_router(delete_router)

app.exception_handler(integrity_exception_handler)
app.exception_handler(global_exception_handler)

@app.get("/")
def read_root():
    return {"Hello": "World"}