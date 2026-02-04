from sqlalchemy.orm import Session
from sqlalchemy import text

class ConvertService:
    @staticmethod
    def get_preview_data(db: Session, user):
        """
        移行前のプレビュー情報を取得する
        """
        # 1. Old User ID の取得 (mail_to_id テーブル)
        query = text("SELECT id FROM mail_to_id WHERE mail = :email")
        result = db.execute(query, {"email": user.email}).fetchone()
        
        if not result:
            return {"error": f"旧ユーザーIDが見つかりません: {user.email}"}
        
        old_user_id = result.id
        new_user_uuid = user.id

        # 2. 旧データの件数取得
        old_items_count = db.execute(text("SELECT COUNT(*) FROM habit_items WHERE user_id = :uid"), {"uid": old_user_id}).scalar()
        old_logs_count = db.execute(text("SELECT COUNT(*) FROM habit_logs WHERE user_id = :uid"), {"uid": old_user_id}).scalar()

        # 3. 新データの件数取得 (削除対象となる現在のデータ)
        new_items_count = db.execute(text("SELECT COUNT(*) FROM hadbit_items WHERE user_id = :uid"), {"uid": new_user_uuid}).scalar()
        new_logs_count = db.execute(text("SELECT COUNT(*) FROM hadbit_logs WHERE user_id = :uid"), {"uid": new_user_uuid}).scalar()

        return {
            "target_email": user.email,
            "old_user_id": old_user_id,
            "new_user_uuid": new_user_uuid,
            "old_data": {
                "items_count": old_items_count,
                "logs_count": old_logs_count
            },
            "new_data": {
                "items_count": new_items_count,
                "logs_count": new_logs_count
            }
        }

    @staticmethod
    def execute_conversion(db: Session, user):
        """
        データ移行を実行する
        """
        # ID再取得
        query = text("SELECT id FROM mail_to_id WHERE mail = :email")
        result = db.execute(query, {"email": user.email}).fetchone()
        
        if not result:
            raise Exception(f"旧ユーザーIDが見つかりません: {user.email}")
            
        old_user_id = result.id
        new_user_uuid = user.id

        try:
            # 1. 新テーブルから対象ユーザーの既存データを削除
            db.execute(text("DELETE FROM hadbit_logs WHERE user_id = :uid"), {"uid": new_user_uuid})
            db.execute(text("DELETE FROM hadbit_items WHERE user_id = :uid"), {"uid": new_user_uuid})
            
            # 2. hadbit_items への移行
            insert_items_sql = text("""
                INSERT INTO hadbit_items (
                    user_id, name, short_name, description, 
                    parent_flag, public_flag, visible_flag, delete_flag, 
                    updated_at, created_at, item_style, is_deleted
                )
                SELECT 
                    :new_uuid, name, short_name, description, 
                    parent_flag, public_flag, visible_flag, delete_flag, 
                    updated_at, created_at, item_style, delete_flag
                FROM habit_items
                WHERE user_id = :old_uid
                ORDER BY id ASC
            """)
            db.execute(insert_items_sql, {"new_uuid": new_user_uuid, "old_uid": old_user_id})
            
            # 3. hadbit_trees への移行
            insert_trees_sql = text("""
                INSERT INTO hadbit_trees (item_id, user_id, parent_id, order_no)
                SELECT 
                    new_item.id,
                    :new_uuid,
                    parent_item.id,
                    tree.order_no
                FROM habit_item_tree tree
                JOIN habit_items old_item ON tree.item_id = old_item.id
                JOIN hadbit_items new_item ON new_item.name = old_item.name AND new_item.user_id = :new_uuid
                LEFT JOIN habit_items old_parent ON tree.parent_id = old_parent.id
                LEFT JOIN hadbit_items parent_item ON parent_item.name = old_parent.name AND parent_item.user_id = :new_uuid
                WHERE old_item.user_id = :old_uid
            """)
            db.execute(insert_trees_sql, {"new_uuid": new_user_uuid, "old_uid": old_user_id})

            # 4. hadbit_logs への移行
            insert_logs_sql = text("""
                INSERT INTO hadbit_logs (
                    user_id, item_id, done_at, updated_at, created_at, comment
                )
                SELECT 
                    :new_uuid,
                    new_item.id,
                    logs.done_at,
                    logs.updated_at,
                    logs.created_at,
                    logs.comment
                FROM habit_logs logs
                JOIN habit_items old_item ON logs.item_id = old_item.id
                JOIN hadbit_items new_item ON new_item.name = old_item.name AND new_item.user_id = :new_uuid
                WHERE logs.user_id = :old_uid
            """)
            db.execute(insert_logs_sql, {"new_uuid": new_user_uuid, "old_uid": old_user_id})
            
            # 5. parent_id の補正 (NULL -> 0)
            update_trees_sql = text("""
                UPDATE hadbit_trees
                SET parent_id = 0
                WHERE user_id = :new_uuid
                AND parent_id IS NULL
            """)
            db.execute(update_trees_sql, {"new_uuid": new_user_uuid})

            db.commit()
            
            # 実行後の件数確認
            final_items = db.execute(text("SELECT COUNT(*) FROM hadbit_items WHERE user_id = :uid"), {"uid": new_user_uuid}).scalar()
            final_logs = db.execute(text("SELECT COUNT(*) FROM hadbit_logs WHERE user_id = :uid"), {"uid": new_user_uuid}).scalar()
            
            return {
                "status": "success",
                "items_count": final_items,
                "logs_count": final_logs
            }
            
        except Exception as e:
            db.rollback()
            raise e