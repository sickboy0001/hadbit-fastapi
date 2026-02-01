from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routers import auth, hadbit_record_router, hadbit_router, pages, system


app = FastAPI()

# 静的ファイルのマウント
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


# ルーターの登録
app.include_router(auth.router)
app.include_router(pages.router)
app.include_router(system.router)
app.include_router(hadbit_router.router)
app.include_router(hadbit_record_router.router)
