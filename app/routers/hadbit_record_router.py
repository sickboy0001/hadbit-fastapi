from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
import json
from ..dependencies import templates, get_current_user
from ..database import get_db
from ..services.hadbit_service import (
    get_hadbits,
)
from ..services.hadbit_record_service import (
    create_hadbit_record, 
    get_logs, 
    delete_hadbit_record, 
    get_log, 
    update_hadbit_record_memo,
    update_hadbit_record
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


@router.get("/hadbit/records/{id}/edit", response_class=HTMLResponse)
async def record_edit_view(request: Request, id: int, user = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return RedirectResponse(url="/login")
    log = get_log(db, user.id, id)
    return templates.TemplateResponse("hadbit/partials/record_edit_modal.html", {"request": request, "user": user, "log": log})


@router.post("/api/records")
async def save_record(
    request: Request,
    hadbit_item_id: int = Form(...),
    record_date: datetime = Form(default_factory=datetime.now),
    memo: str = Form(""),
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user:
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})
    
    new_record = create_hadbit_record(db, user.id, hadbit_item_id, record_date, memo)
    db.commit()
    
    # 登録したレコードの詳細を取得（表示用）
    log = get_log(db, user.id, new_record.id)
    # if log:
    #     print(f"New record created: {log.log_id}, item_id: {log.item_id}, done_at: {log.done_at},child_name:{log.child_name}, parent_name:{log.parent_name}")

    # if not log:
    #     return HTMLResponse(content="""
    #     <div hx-swap-oob="beforeend:#toast-container">
    #         <div class="alert alert-error shadow-lg mb-2">
    #             <span>エラー: 登録情報の取得に失敗しました。</span>
    #         </div>
    #     </div>
    #     """)

    # テンプレートを使用して行のHTMLを生成
    table_html = templates.get_template("hadbit/partials/records_table.html").render({"logs": [dict(log._mapping)], "oob": True})

    # トーストのHTMLを生成
    toast_html = templates.get_template("hadbit/partials/toast_registered.html").render({"log_id": log.log_id})

    return HTMLResponse(content=f"{table_html}{toast_html}")

@router.put("/api/records/regist/{log_id}")
async def update_record(
    log_id: int,
    record_date: datetime = Form(...),
    memo: str = Form(""),
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user:
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})
    
    # レコードを特定して更新
    update_hadbit_record(db, user.id, log_id, record_date, memo)
        
    # 更新後のデータを取得して表示
    log = get_log(db, user.id, log_id)
    
    # 行の更新用HTML (update=True で行置換モード)
    table_html = templates.get_template("hadbit/partials/records_table.html").render({"logs": [dict(log._mapping)], "update": True})
    
    # トースト通知
    toast_html = templates.get_template("hadbit/partials/toast_registered.html").render({"log_id": log.log_id, "message": "保存しました。"})

    return HTMLResponse(content=f"{table_html}{toast_html}")

@router.post("/api/records/restore")
async def restore_record(
    hadbit_item_id: int = Form(...),
    record_date: datetime = Form(default_factory=datetime.now),
    memo: str = Form(""),
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user:
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})
    
    create_hadbit_record(db, user.id, hadbit_item_id, record_date, memo)
    db.commit()
    
    return HTMLResponse(content="", status_code=200)

@router.delete("/api/logs/delete/{log_id}")
async def delete_record(
    log_id: int,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user:
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})
    
    deleted_record = delete_hadbit_record(db, user.id, log_id)
    db.commit()
    
    if not deleted_record:
        return HTMLResponse(content="")

    # 復元用のデータをJSON文字列として準備
    restore_vals = json.dumps({
        "hadbit_item_id": deleted_record.item_id,
        "record_date": deleted_record.done_at.isoformat(),
        "memo": deleted_record.comment or ""
    })

    # トーストのHTMLを生成
    toast_html = templates.get_template("hadbit/partials/toast_deleted.html").render({
        "log_id": log_id,
        "restore_vals": restore_vals
    })

    return HTMLResponse(content=toast_html)

@router.get("/api/records/{log_id}/memo")
async def get_memo_form(log_id: int, user = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})
    
    log = get_log(db, user.id, log_id)
    if not log:
        return HTMLResponse("Error")
    
    memo = log.comment or ""
    return HTMLResponse(f"""
        <form hx-patch="/api/records/{log_id}/memo" hx-swap="outerHTML" class="flex items-center gap-1">
            <input type="text" name="memo" value="{memo}" class="input input-bordered input-xs w-full max-w-xs" autofocus>
            <button type="submit" class="btn btn-xs btn-primary">保存</button>
            <button type="button" class="btn btn-xs" hx-get="/api/records/{log_id}/memo/view" hx-swap="outerHTML">×</button>
        </form>
    """)

@router.get("/api/records/{log_id}/memo/view")
async def get_memo_view(log_id: int, user = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})
    
    log = get_log(db, user.id, log_id)
    memo = log.comment or ""
    display_text = memo if memo else '<span class="text-gray-400 text-xs">(メモなし)</span>'
    
    return HTMLResponse(f"""
        <div hx-get="/api/records/{log_id}/memo" hx-trigger="click" hx-swap="outerHTML" class="cursor-pointer hover:bg-base-200 p-1 rounded min-h-[1.5rem] min-w-[4rem]">
            {display_text}
        </div>
    """)

@router.patch("/api/records/{log_id}/memo")
async def update_memo(log_id: int, memo: str = Form(""), user = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})
    
    update_hadbit_record_memo(db, user.id, log_id, memo)
    db.commit()
    
    # 更新後の表示ビューを返す（get_memo_viewと同じHTML構造）
    display_text = memo if memo else '<span class="text-gray-400 text-xs">(メモなし)</span>'
    return HTMLResponse(f"""
        <div hx-get="/api/records/{log_id}/memo" hx-trigger="click" hx-swap="outerHTML" class="cursor-pointer hover:bg-base-200 p-1 rounded min-h-[1.5rem] min-w-[4rem]">
            {display_text}
        </div>
    """)

# d:\work\dev\fastapi\hadbit-fastapi\app\routers\hadbit_router.py
