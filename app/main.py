import os
import sys
from pathlib import Path

# 自分の親ディレクトリを sys.path に追加する
# これにより "from app.xxx" が Workers 上でも動くようになります
base_path = Path(__file__).resolve().parent.parent
if str(base_path) not in sys.path:
    sys.path.insert(0, str(base_path))
    
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import auth, hadbit_record_router, hadbit_router, pages, system


app = FastAPI()


# 静的ファイルのマウント
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

@app.get("/")
def read_root():
    return {"message": "Hello from sub-directory!"}


# ルーターの登録
app.include_router(auth.router)
app.include_router(pages.router)
app.include_router(system.router)
app.include_router(hadbit_router.router)
app.include_router(hadbit_record_router.router)
