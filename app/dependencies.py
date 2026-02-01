from pathlib import Path
from fastapi import Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text
from .services.supabase_client import supabase
from .database import get_db

# テンプレートの設定 (app/templates を指すように調整)
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# グローバルなナビゲーションリンク定義
# templates.env.globals に追加することで、全てのテンプレートで {{ nav_links }} が利用可能になります
NAV_LINKS = [
    {'href': '/dashboard', 'icon': 'fas fa-tachometer-alt', 'label': 'ダッシュボード'},
    {'href': '/hadbit/records', 'icon': 'fas fa-edit', 'label': '習慣ログ'},
    {'href': '/hadbit/items', 'icon': 'fas fa-list', 'label': '習慣マスタ'},
    {'href': '/settings', 'icon': 'fas fa-cog', 'label': '設定'}
]
templates.env.globals["nav_links"] = NAV_LINKS

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Cookieからアクセストークンを取得し、Supabaseでユーザー情報を取得する。
    認証失敗時は None を返す。
    """
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    try:
        user_response = supabase.auth.get_user(token)
        user = user_response.user
        if user and user.email:
            # mail_to_id テーブルから ID を取得して user オブジェクトに付与
            # SupabaseのUUIDと区別するため db_id としています
            query = text("SELECT id FROM mail_to_id WHERE mail = :mail")
            result = db.execute(query, {"mail": user.email}).fetchone()
            if result:
                user.user_metadata["db_id"] = result.id
            else:
                # データがない場合は新規追加してIDを取得
                insert_query = text("INSERT INTO mail_to_id (mail) VALUES (:mail) RETURNING id")
                result = db.execute(insert_query, {"mail": user.email}).fetchone()
                db.commit()
                if result:
                    user.user_metadata["db_id"] = result.id
        # print(
        #     f"Authenticated user: {user.email} "
        #     f"with user.user_metadata.get('db_id'): {user.user_metadata.get('db_id')}"
        # )
        return user
    except Exception as e:
        print(f"Error in get_current_user: {e}")
        return None