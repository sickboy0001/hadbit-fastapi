from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from ..dependencies import templates, get_current_user
from ..database import get_db
from ..services.post_service import get_recent_posts
from ..services.hadbit import get_habits

router = APIRouter()

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login")
        
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@router.get("/settings", response_class=HTMLResponse)
async def settings(request: Request, user = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("settings.html", {"request": request, "user": user})

@router.get("/test_supabase", response_class=HTMLResponse)
async def test_supabase(request: Request, user = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return RedirectResponse(url="/login")

    posts = []
    error_msg = None
    try:
        # サービス層経由でデータを取得
        posts = get_recent_posts(db)
    except Exception as e:
        error_msg = f"データ取得エラー: {str(e)}"

    return templates.TemplateResponse("test_supabase.html", {"request": request, "user": user, "posts": posts, "error": error_msg})

@router.get("/hadbit/records", response_class=HTMLResponse)
async def hadbit_records(request: Request, user = Depends(get_current_user), db: Session = Depends(get_db)):
    if user:
        print(f"hadbit_records called with user")
    else:
        print("hadbit_records called: No user")

    if not user:
        return RedirectResponse(url="/login")

    habits = []
    try:
        # 習慣マスタを取得 (テーブル名: habits, カラム: id, name 等を想定)
        habits = get_habits(db,user)
    except Exception as e:
        print(f"Error fetching habits: {e}")

    return templates.TemplateResponse("hadbit_records.html", {"request": request, "user": user, "habits": habits})

@router.get("/hadbit/settings", response_class=HTMLResponse)
async def hadbit_settings(request: Request, user = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("hadbit_settings.html", {"request": request, "user": user})

@router.get("/hadbit/analytics", response_class=HTMLResponse)
async def hadbit_analytics(request: Request, user = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("hadbit_analytics.html", {"request": request, "user": user})

@router.get("/hadbit/records/{id}/edit", response_class=HTMLResponse)
async def record_edit_view(request: Request, id: int, user = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("hadbit_record_edit.html", {"request": request, "user": user, "id": id})