from sqlalchemy.orm import Session
from sqlalchemy import text

def get_habits(db: Session, user) :
    """
    habits テーブルからユーザーの習慣を取得する (親子関係・順序考慮)
    """
    print(f"get_habits called for User(id={user.id}, email={user.email}, metadata={getattr(user, 'user_metadata', {})}) ")
    db_id = user.user_metadata.get('db_id')
    print(f"user db_id: " + str(db_id))

    if db_id is None:
        return []

    # 再帰的CTEを使用して、habit_item_treeに基づく順序で取得
    query = text("""
        WITH RECURSIVE item_tree AS (
            -- Root items (parent_id is NULL)
            SELECT 
                hi.*,
                hit.parent_id,
                hit.order_no,
                ARRAY[COALESCE(hit.order_no, 0)] AS path
            FROM habit_items hi
            JOIN habit_item_tree hit ON hi.id = hit.item_id
            WHERE hi.user_id = :user_id 
              AND hit.parent_id IS NULL
              AND (hi.delete_flag IS FALSE OR hi.delete_flag IS NULL)
            
            UNION ALL
            
            -- Child items
            SELECT 
                hi.*,
                hit.parent_id,
                hit.order_no,
                it.path || COALESCE(hit.order_no, 0)
            FROM habit_items hi
            JOIN habit_item_tree hit ON hi.id = hit.item_id
            JOIN item_tree it ON hit.parent_id = it.id
            WHERE hi.user_id = :user_id
              AND (hi.delete_flag IS FALSE OR hi.delete_flag IS NULL)
        )
        SELECT * FROM item_tree ORDER BY path
    """)
    result = db.execute(query, {"user_id": db_id})
    return [dict(row._mapping) for row in result]