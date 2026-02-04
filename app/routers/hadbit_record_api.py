from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import json
from app.dependencies import templates, get_current_user
from app.database import get_db
from app.services.hadbit_record_service import (
    create_hadbit_record, 
    get_logs, 
    delete_hadbit_record, 
    get_log, 
    update_hadbit_record
)

router = APIRouter()

def get_now_jst():
    return datetime.now(timezone(timedelta(hours=9))).replace(tzinfo=None)

@router.post("/api/hadbit/records/create")
async def save_record(
    request: Request,
    hadbit_item_id: int = Form(...),
    record_date: datetime = Form(default_factory=get_now_jst),
    memo: str = Form(""),
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user:
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})
    
    new_record = create_hadbit_record(db, user.id, hadbit_item_id, record_date, memo)
    db.commit()
    
    # HTMXリクエストの場合のみHTMLとToastヘッダーを返す
    if request.headers.get("HX-Request"):
        # 全件取得してリスト全体を更新する
        logs = get_logs(db, user.id)

        # リスト全体のHTMLを生成
        table_html = templates.get_template("hadbit/partials/records_table.html").render({"logs": logs})

        response = HTMLResponse(content=table_html)
        toast_msg = f'登録しました <span class="underline font-bold ml-2 cursor-pointer" onclick="htmx.ajax(\'GET\', \'/hadbit/records/{new_record.id}/edit\', {{target:\'#modal-container\', swap:\'innerHTML\'}})">編集</span>'
        response.headers["HX-Trigger"] = json.dumps({"toast": toast_msg})
        return response

    # 他のクライアントの場合はJSONを返す
    return JSONResponse(content={
        "id": new_record.id,
        "item_id": new_record.item_id,
        "done_at": new_record.done_at.isoformat() if new_record.done_at else None,
        "comment": new_record.comment
    })

@router.put("/api/hadbit/records/regist/{log_id}")
async def update_record(
    request: Request,
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
    db.commit()
        
    if request.headers.get("HX-Request"):
        # 全件取得してリスト全体を更新する（日付変更によるグループ移動に対応するため）
        logs = get_logs(db, user.id)
        
        # リスト全体のHTML (swap_all=True で id="records-list" を OOB swap)
        table_html = templates.get_template("hadbit/partials/records_table.html").render({"logs": logs, "swap_all": True})
        
        response = HTMLResponse(content=table_html)
        response.headers["HX-Trigger"] = json.dumps({"toast": "保存しました。"})
        return response

    updated_log = get_log(db, user.id, log_id)
    return JSONResponse(content={
        "id": updated_log.id,
        "item_id": updated_log.item_id,
        "done_at": updated_log.done_at.isoformat() if updated_log.done_at else None,
        "comment": updated_log.comment
    })

@router.post("/api/hadbit/records/restore")
async def restore_record(
    hadbit_item_id: int = Form(...),
    record_date: datetime = Form(default_factory=get_now_jst),
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
    request: Request,
    log_id: int,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user:
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})
    
    deleted_record = delete_hadbit_record(db, user.id, log_id)
    db.commit()
    
    if not deleted_record:
        if request.headers.get("HX-Request"):
            return HTMLResponse(content="")
        return JSONResponse(status_code=404, content={"message": "Record not found"})

    if request.headers.get("HX-Request"):
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

    return JSONResponse(content={
        "id": log_id,
        "item_id": deleted_record.item_id,
        "done_at": deleted_record.done_at.isoformat() if deleted_record.done_at else None,
        "comment": deleted_record.comment
    })