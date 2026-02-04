from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.dependencies import templates, get_current_user
from app.database import get_db
from app.services.hadbit_service import (
    get_hadbits,
)
from app.services.hadbit_record_service import (
    get_logs, 
    get_log, 
)

router = APIRouter()

@router.get("/hadbit/records", response_class=HTMLResponse)
async def hadbit_records(request: Request, user = Depends(get_current_user), db: Session = Depends(get_db)):
    if user:
        print(f"hadbit_records called with user")
    else:
        print("hadbit_records called: No user")

    if not user:
        return RedirectResponse(url="/login")

    habits = []
    logs = []
    try:
        # 習慣マスタを取得 (テーブル名: habits, カラム: id, name 等を想定)
        habits = get_hadbits(db,user)
        logs = get_logs(db, user.id)
    except Exception as e:
        print(f"Error fetching data: {e}")

    return templates.TemplateResponse("hadbit/records.html", {"request": request, "user": user, "habits": habits, "logs": logs})


@router.get("/hadbit/records/calendar", response_class=HTMLResponse)
async def get_calendar_view(request: Request, user = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return HTMLResponse("Unauthorized", status_code=401)
    
    logs = []
    try:
        logs = get_logs(db, user.id)
    except Exception as e:
        print(f"Error fetching logs for calendar: {e}")
        
    return templates.TemplateResponse("hadbit/partials/records_calendar.html", {"request": request, "logs": logs})


@router.get("/hadbit/records/heatmap", response_class=HTMLResponse)
async def get_heatmap_view(request: Request, user = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return HTMLResponse("Unauthorized", status_code=401)
    
    logs = []
    try:
        logs = get_logs(db, user.id)
    except Exception as e:
        print(f"Error fetching logs for heatmap: {e}")
        
    return templates.TemplateResponse("hadbit/partials/records_heatmap.html", {"request": request, "logs": logs})


@router.get("/hadbit/records/dategrid", response_class=HTMLResponse)
async def get_dategrid_view(request: Request, user = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return HTMLResponse("Unauthorized", status_code=401)
    
    logs = []
    try:
        logs = get_logs(db, user.id)
    except Exception as e:
        print(f"Error fetching logs for dategrid: {e}")
        
    return templates.TemplateResponse("hadbit/partials/records_dategrid.html", {"request": request, "logs": logs})


@router.get("/hadbit/records/{id}/edit", response_class=HTMLResponse)
async def record_edit_view(request: Request, id: int, user = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return RedirectResponse(url="/login")
    log = get_log(db, user.id, id)
    return templates.TemplateResponse("hadbit/partials/record_edit_modal.html", {"request": request, "user": user, "log": log})

# d:\work\dev\fastapi\hadbit-fastapi\app\routers\hadbit_router.py
