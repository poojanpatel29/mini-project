from fastapi import FastAPI

from Routes.routes_post import router as post_router
from Routes.routes_get import router as get_router
from Routes.routes_patch import router as patch_router
from Routes.routes_put import router as put_router
from Routes.routes_delete import router as delete_router

app = FastAPI()

app.include_router(post_router)
app.include_router(get_router)
app.include_router(patch_router)
app.include_router(put_router)
app.include_router(delete_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}