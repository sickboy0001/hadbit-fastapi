import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from datetime import datetime

# アプリケーションのインポート（パスは環境に合わせて調整してください）
from app.main import app
from app.database import get_db
from app.dependencies import get_current_user

# テスト用クライアントの作成
client = TestClient(app)

# ダミーユーザーの定義
class MockUser:
    id = "test_user_id_123"
    email = "test@example.com"
    user_metadata = {}

# 認証依存関係のオーバーライド（ログイン済みとして振る舞う）
def mock_get_current_user():
    return MockUser()

app.dependency_overrides[get_current_user] = mock_get_current_user

def test_update_record_endpoint():
    """
    記録の更新処理（PUT /api/records/regist/{log_id}）のテスト
    1. テスト用の項目と記録を作成
    2. API経由で更新を実行
    3. レスポンスとDBの値を確認
    4. テストデータを削除
    """
    # DBセッションを取得
    db = next(get_db())
    
    item_id = None
    log_id = None

    try:
        # --- 1. 準備: テストデータの作成 (INSERT) ---
        # 親アイテム（項目）を作成
        item_id = db.execute(text("""
            INSERT INTO hadbit_items (user_id, name, short_name, description)
            VALUES (:uid, 'Test Item', 'Test', 'Desc') RETURNING id
        """), {"uid": MockUser.id}).scalar()
        
        # ログ（記録）を作成
        original_date = datetime(2025, 1, 1, 10, 0, 0)
        log_id = db.execute(text("""
            INSERT INTO hadbit_logs (user_id, item_id, done_at, comment)
            VALUES (:uid, :iid, :date, 'Original Memo') RETURNING id
        """), {"uid": MockUser.id, "iid": item_id, "date": original_date}).scalar()
        
        # ツリー構造の整合性が必要な場合は hadbit_trees にもINSERTが必要ですが、
        # 更新API自体は logs テーブルのみを操作するため、ここでは省略可能です。
        # ただし、get_log で JOIN しているため、表示確認まで含めるなら必要になります。
        # 今回は更新処理(UPDATE)の動作確認に絞ります。
        
        db.commit()

        # --- 2. 実行: 更新APIの呼び出し ---
        new_date_str = "2025-12-31T23:59"
        new_memo = "Updated Memo Content"
        
        response = client.put(
            f"/api/records/regist/{log_id}",
            data={
                "record_date": new_date_str,
                "memo": new_memo
            }
        )

        # --- 3. 検証 ---
        # ステータスコードの確認
        assert response.status_code == 200
        # レスポンスHTMLにトーストメッセージが含まれているか
        assert "保存しました。" in response.text
        
        # DBの値が更新されているか確認
        row = db.execute(text("SELECT comment, done_at FROM hadbit_logs WHERE id = :id"), {"id": log_id}).fetchone()
        assert row.comment == new_memo
        assert row.done_at.strftime('%Y-%m-%dT%H:%M') == new_date_str

    finally:
        # --- 4. クリーンアップ ---
        if log_id:
            db.execute(text("DELETE FROM hadbit_logs WHERE id = :id"), {"id": log_id})
        if item_id:
            db.execute(text("DELETE FROM hadbit_items WHERE id = :id"), {"id": item_id})
        db.commit()
        db.close()
