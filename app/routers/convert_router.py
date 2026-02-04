from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, templates
from app.services.convert_service import ConvertService

router = APIRouter(
    prefix="/convert",
    tags=["convert"]
)

@router.get("/", response_class=HTMLResponse)
async def convert_preview(request: Request, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "ログインが必要です"})
    
    data = ConvertService.get_preview_data(db, current_user)
    
    return templates.TemplateResponse("convert/step01.html", {
        "request": request,
        "step": "preview",
        "data": data,
        "user": current_user
    })

@router.post("/confirm", response_class=HTMLResponse)
async def convert_confirm(request: Request, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "ログインが必要です"})

    # 確認画面でもデータを再取得して表示
    data = ConvertService.get_preview_data(db, current_user)
    
    return templates.TemplateResponse("convert/step01.html", {
        "request": request,
        "step": "confirm",
        "data": data,
        "user": current_user
    })

@router.post("/execute", response_class=HTMLResponse)
async def convert_execute(request: Request, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if not current_user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "ログインが必要です"})

    try:
        result = ConvertService.execute_conversion(db, current_user)
        return templates.TemplateResponse("convert/step01.html", {
            "request": request,
            "step": "result",
            "result": result,
            "user": current_user
        })
    except Exception as e:
        return templates.TemplateResponse("convert/step01.html", {
            "request": request,
            "step": "error",
            "error": str(e),
            "user": current_user
        })