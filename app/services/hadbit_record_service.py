from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

def create_hadbit_record(db: Session, user_id: str, hadbit_item_id: int, record_date: datetime, memo: str = ""):
    """
    習慣の記録を新規作成（INSERT）する
    hadbit_logs テーブルを使用。
    一日に複数回の登録を許容するため、重複チェックは行わず常にINSERTする。
    """
    insert_query = text("INSERT INTO hadbit_logs (user_id, item_id, done_at, comment) VALUES (:user_id, :item_id, :done_at, :comment) RETURNING id")
    result = db.execute(insert_query, {"user_id": user_id, "item_id": hadbit_item_id, "done_at": record_date, "comment": memo}).fetchone()
    return result

def delete_hadbit_record(db: Session, user_id: str, log_id: int):
    """
    指定されたIDの記録を削除する
    ユーザーIDの一致を確認して、他人の記録を削除できないようにする
    """
    # 削除した行のデータを返すようにRETURNING句を追加
    query = text("DELETE FROM hadbit_logs WHERE id = :log_id AND user_id = :user_id RETURNING item_id, done_at, comment")
    result = db.execute(query, {"log_id": log_id, "user_id": user_id}).fetchone()
    return result

def get_log(db: Session, user_id: str, log_id: int):
    """
    指定されたIDの記録を取得する（表示・編集用）
    """
    query = text("""
        SELECT 
            logs.id AS log_id,
            logs.done_at AS done_at,
            logs.item_id AS item_id,
            logs.comment,
            pitem.id AS parent_item_id, 
            pitem.name AS parent_name, 
            pitem.short_name AS parent_short_name,
            citem.id AS child_item_id,
            citem.name AS child_name, 
            citem.short_name AS child_short_name
        FROM hadbit_logs logs
        INNER JOIN hadbit_items citem ON citem.id = logs.item_id
        INNER JOIN hadbit_trees tree ON tree.item_id = logs.item_id
        INNER JOIN hadbit_items pitem ON pitem.id = tree.parent_id
        WHERE logs.id = :log_id AND logs.user_id = :user_id
    """)
    return db.execute(query, {"log_id": log_id, "user_id": user_id}).fetchone()

def update_hadbit_record_memo(db: Session, user_id: str, log_id: int, memo: str):
    """
    指定されたIDの記録のメモを更新する
    """
    query = text("UPDATE hadbit_logs SET comment = :memo WHERE id = :log_id AND user_id = :user_id")
    db.execute(query, {"memo": memo, "log_id": log_id, "user_id": user_id})

def update_hadbit_record(db: Session, user_id: str, log_id: int, record_date: datetime, memo: str):
    """
    指定されたIDの記録の日時とメモを更新する
    """
    query = text("UPDATE hadbit_logs SET done_at = :done_at, comment = :comment WHERE id = :log_id AND user_id = :user_id")
    db.execute(query, {"done_at": record_date, "comment": memo, "log_id": log_id, "user_id": user_id})

def get_logs(db: Session, user_id: str, start_date: str = None, end_date: str = None):
    # 1. デフォルト期間の設定（指定がない場合は直近1年）
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    if not end_date:
        # 時刻を含まない日付比較の場合、その日の終わりまで含める工夫が必要な場合があります
        end_date = datetime.now().strftime('%Y-%m-%d 23:59:59')

    # 2. SQLクエリの定義（:user_id を追加）
    sql = text("""
        SELECT 
            logs.id AS log_id,
            logs.done_at AS done_at,
            logs.item_id AS item_id,
            logs.comment,
            pitem.id AS parent_item_id, 
            pitem.name AS parent_name, 
            pitem.short_name AS parent_short_name,
            citem.id AS child_item_id,
            citem.name AS child_name, 
            citem.short_name AS child_short_name
        FROM hadbit_logs logs
        INNER JOIN hadbit_items citem ON citem.id = logs.item_id
        INNER JOIN hadbit_trees tree ON tree.item_id = logs.item_id
        INNER JOIN hadbit_items pitem ON pitem.id = tree.parent_id
        WHERE logs.user_id = :user_id
          AND logs.done_at BETWEEN :start_date AND :end_date
        ORDER BY logs.done_at DESC
    """)

    # 3. パラメータを辞書で渡して実行
    params = {
        "user_id": user_id,
        "start_date": start_date,
        "end_date": end_date
    }
    
    result = db.execute(sql, params)
    return result.fetchall()