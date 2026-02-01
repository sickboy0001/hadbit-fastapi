from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from ..dependencies import templates, get_current_user
from ..database import get_db
from ..services.post_service import get_recent_posts
from ..services.hadbit_service import (
    get_hadbits,
    get_parent_hadbit_items,
    get_hadbit_tree_max_sort_order,
    create_hadbit_tree,
    create_hadbit_item,
    get_hadbit_item,
    update_hadbit_item,
    delete_hadbit_item,
    restore_hadbit_item,
    move_hadbit_item_up,
    move_hadbit_item_down
)

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


@router.get("/hadbit/items", response_class=HTMLResponse)
async def hadbit_settings(request: Request, 
    user = Depends(get_current_user), 
    db: Session = Depends(get_db)
    ):
    if not user:
        return RedirectResponse(url="/login")
    habits = []
    try:
        # 習慣マスタを取得 (テーブル名: habits, カラム: id, name 等を想定)
        habits = get_hadbits(db,user)
    except Exception as e:
        print(f"Error fetching habits: {e}")

    return templates.TemplateResponse("hadbit/items.html", {"request": request, "user": user, "habits": habits})

@router.post("/hadbit/items/new", response_class=HTMLResponse)
async def create_new_habit_type(
    request: Request,
    user = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    「種別追加」ボタン押下時の処理
    デフォルト値で新しい習慣（種別・項目）を作成し、画面を再描画します。
    """
    # 1. 並び順の最大値を取得して、末尾に追加するための値を決定
    # (parent_sort_order の最大値を取得し、+1 する)
    max_sort = get_hadbit_tree_max_sort_order(db, user.id, 0)
    new_sort_order = (max_sort or 0) + 1

    # 親アイテム作成 (新規種別)
    parent_item_id = create_hadbit_item(db, user.id, "新規種別", "新規種別", "新しい種別です")
    
    # 親ツリー作成
    create_hadbit_tree(db, parent_item_id, user.id, 0, new_sort_order)

    # 子アイテム作成 (新規項目)
    child_item_id = create_hadbit_item(db, user.id, "新規項目", "新規項目", "新しい項目です")

    # 子ツリー作成
    create_hadbit_tree(db, child_item_id, user.id, parent_item_id, 1)

    db.commit()

    # 3. 最新のリストを取得
    # 一覧画面表示時と同じクエリで全データを取得し直します
    habits = get_hadbits(db, user)

    # 4. 画面全体をレンダリングして返却
    # hx-target="body" なので、ページ全体のHTMLを返します
    return templates.TemplateResponse("hadbit/items.html", {
        "request": request,
        "user": user,
        "habits": habits
    })

@router.post("/hadbit/items/{parent_id}/new_child", response_class=HTMLResponse)
async def create_new_child_item(
    request: Request,
    parent_id: int,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    指定された種別（parent_id）の中に新しい項目を追加する
    """
    # 指定された親配下での最大並び順を取得
    max_sort = get_hadbit_tree_max_sort_order(db, user.id, parent_id)
    new_sort_order = (max_sort or 0) + 1

    child_item_id = create_hadbit_item(db, user.id, "新規項目", "新規項目", "新しい項目です")
    create_hadbit_tree(db, child_item_id, user.id, parent_id, new_sort_order)
    
    db.commit()

    habits = get_hadbits(db, user)
    return templates.TemplateResponse("hadbit/items.html", {
        "request": request,
        "user": user,
        "habits": habits
    })

@router.get("/hadbit/items/{id}/edit", response_class=HTMLResponse)
async def get_item_edit_form(
    request: Request,
    id: int,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    編集ボタン押下時：右側の編集エリアに表示するフォームを返す
    """
    item = get_hadbit_item(db, id, user.id)
    if not item:
        return HTMLResponse("<div>対象のデータが見つかりません。</div>")

    parents = get_parent_hadbit_items(db, user.id)
    return templates.TemplateResponse("hadbit/item_edit_form.html", {
        "request": request,
        "item": item,
        "parents": parents
    })

@router.put("/hadbit/items/{id}", response_class=HTMLResponse)
async def update_habit_item_endpoint(
    request: Request,
    id: int,
    name: str = Form(...),
    short_name: str = Form(None),
    description: str = Form(None),
    parent_id: int = Form(None),
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    項目編集フォームの保存処理
    """
    # Noneの場合は空文字として扱う
    update_hadbit_item(db, id, user.id, name, short_name or "", description or "", parent_id)
    db.commit()

    # 更新後のリストを取得して画面全体を再描画
    habits = get_hadbits(db, user)
    return templates.TemplateResponse("hadbit/items.html", {
        "request": request,
        "user": user,
        "habits": habits
    })
    
@router.put("/hadbit/items/{id}", response_class=HTMLResponse)
async def update_habit_item_endpoint(
    request: Request,
    id: int,
    name: str = Form(...),          # 必須項目
    short_name: str = Form(None),   # 任意項目
    description: str = Form(None),  # 任意項目
    parent_id: int = Form(None),    # 任意項目（親カテゴリの移動用）
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    項目編集フォームの保存処理
    """
    # Noneの場合は空文字として扱うなどの前処理を行い、サービス層へ渡す
    update_hadbit_item(db, id, user.id, name, short_name or "", description or "", parent_id)
    db.commit()

    # 更新後のリストを取得して画面全体を再描画
    habits = get_hadbits(db, user)
    return templates.TemplateResponse("hadbit/items.html", {
        "request": request,
        "user": user,
        "habits": habits
    })

@router.delete("/hadbit/items/{id}", response_class=HTMLResponse)
async def delete_item(
    request: Request,
    id: int,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    項目の削除（論理削除）
    """
    delete_hadbit_item(db, id, user.id)
    db.commit()

    habits = get_hadbits(db, user)
    return templates.TemplateResponse("hadbit/items.html", {
        "request": request,
        "user": user,
        "habits": habits,
        "deleted_item_id": id  # Toast表示用
    })

@router.post("/hadbit/items/{id}/restore", response_class=HTMLResponse)
async def restore_item(
    request: Request,
    id: int,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    削除の取り消し
    """
    restore_hadbit_item(db, id, user.id)
    db.commit()

    habits = get_hadbits(db, user)
    return templates.TemplateResponse("hadbit/items.html", {
        "request": request,
        "user": user,
        "habits": habits,
        "restored_message": "元に戻しました。"
    })


@router.post("/hadbit/items/{id}/move_up", response_class=HTMLResponse)
async def move_item_up(
    request: Request,
    id: int,
    user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    指定されたアイテムを一つ上に移動（sort_orderを入れ替え）
    """
    move_hadbit_item_up(db, user.id, id)
    db.commit()

    # 4. 画面全体を再描画
    habits = get_hadbits(db, user)
    return templates.TemplateResponse("hadbit/items.html", {
        "request": request,
        "user": user,
        "habits": habits
    })


@router.post("/hadbit/items/{id}/move_down", response_class=HTMLResponse)
async def move_item_down(
    request: Request,
    id: int,
    user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    指定されたアイテムを一つ下に移動（sort_orderを入れ替え）
    """
    move_hadbit_item_down(db, user.id, id)
    db.commit()

    # 4. 画面全体を再描画
    habits = get_hadbits(db, user)
    return templates.TemplateResponse("hadbit/items.html", {
        "request": request,
        "user": user,
        "habits": habits
    })


@router.get("/hadbit/analytics", response_class=HTMLResponse)
async def hadbit_analytics(request: Request, user = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("hadbit_analytics.html", {"request": request, "user": user})


