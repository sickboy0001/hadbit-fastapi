from sqlalchemy.orm import Session
from sqlalchemy import text

def get_hadbits(db: Session, user) :
    """
    hadbits テーブルからユーザーの習慣を取得する (親子関係・順序考慮)
    """
    # print(f"get_hadbits called for User(id={user.id}, email={user.email}, metadata={getattr(user, 'user_metadata', {})}) ")
    db_id = user.id
    # print(f"user db_id: " + str(db_id))

    if db_id is None:
        return []

    # 再帰的CTEを使用して、habit_item_treeに基づく順序で取得
    query = text("""
        SELECT 
        -- 親アイテムの情報
        parent_item.user_id,
        parent_item.id           AS parent_id,
        parent_tree.order_no     AS parent_sort_order,
        parent_item.name         AS parent_name, 
        parent_item.short_name   AS parent_short_name,
        parent_item.description  AS parent_description,

        -- 子アイテムの情報
        child_tree.item_id       AS child_id,
        child_tree.order_no      AS child_sort_order,
        child_item.name          AS child_name,
        child_item.short_name    AS child_short_name,
        child_item.description   AS child_description 
        FROM hadbit_trees AS parent_tree
        INNER JOIN hadbit_items AS parent_item
        ON parent_tree.item_id = parent_item.id
        AND parent_item.user_id = :user_id
        AND parent_item.is_deleted = false
        INNER JOIN hadbit_trees AS child_tree
        ON child_tree.parent_id = parent_tree.item_id
        INNER JOIN hadbit_items AS child_item
        ON child_tree.item_id = child_item.id
        AND child_item.user_id = :user_id
        AND child_item.is_deleted = false
        WHERE parent_tree.parent_id = 0
        ORDER BY 
        parent_sort_order, 
        child_sort_order;
    """)
    result = db.execute(query, {"user_id": db_id})
    return [dict(row._mapping) for row in result]

def get_parent_hadbit_items(db: Session, user_id: str):
    """
    親項目（種別）の一覧を取得する
    """
    query = text("""
        SELECT i.id, i.name 
        FROM hadbit_items i
        JOIN hadbit_trees t ON i.id = t.item_id
        WHERE t.parent_id = 0 AND i.user_id = :user_id AND i.is_deleted = false
        ORDER BY t.order_no
    """)
    result = db.execute(query, {"user_id": user_id}).fetchall()
    return [dict(row._mapping) for row in result]

def get_hadbit_tree_max_sort_order(db: Session, user_id: str, parent_id: int = 0) -> int:
    """
    hadbit_trees テーブルから、指定ユーザー・指定親ID配下の最大order_noを取得する
    """
    query = text("""
SELECT MAX(order_no) 
FROM hadbit_trees 
WHERE user_id = :user_id AND parent_id = :parent_id""")
    result = db.execute(query, {"user_id": user_id, "parent_id": parent_id}).scalar()
    return result if result is not None else 0

def create_hadbit_tree(
        db: Session, 
        item_id: int, 
        user_id: str, 
        parent_id: int, 
        order_no: int
        ):
    """
    hadbit_trees テーブルに新しいレコードを作成する
    """
    query = text("""
INSERT INTO hadbit_trees (item_id, user_id, parent_id, order_no)
VALUES (:item_id, :user_id, :parent_id, :order_no)
    """)
    db.execute(query, {
        "item_id": item_id,
        "user_id": user_id,
        "parent_id": parent_id,
        "order_no": order_no
    })

def create_hadbit_item(db: Session, user_id: str, name: str, short_name: str = "", description: str = "") -> int:
    """
    hadbit_items テーブルに新しいレコードを作成し、IDを返す
    """
    query = text("""
INSERT INTO hadbit_items (user_id, name, short_name, description)
VALUES (:user_id, :name, :short_name, :description)
RETURNING id
    """)
    result = db.execute(query, {
        "user_id": user_id,
        "name": name,
        "short_name": short_name,
        "description": description
    }).scalar()
    return result

def get_hadbit_item(db: Session, item_id: int, user_id: str):
    """
    IDを指定してhadbit_itemsのレコードを取得する
    """
    query = text("""
        SELECT i.*, p.name as parent_name, t.parent_id
        FROM hadbit_items i
        LEFT JOIN hadbit_trees t ON i.id = t.item_id
        LEFT JOIN hadbit_items p ON t.parent_id = p.id
        WHERE i.id = :id AND i.user_id = :user_id
    """)
    result = db.execute(query, {"id": item_id, "user_id": user_id}).fetchone()
    return dict(result._mapping) if result else None

def update_hadbit_item(db: Session, item_id: int, user_id: str, name: str, short_name: str, description: str, new_parent_id: int = None):
    """
    hadbit_items テーブルのレコードを更新する
    """
    query = text("""
UPDATE hadbit_items
SET name = :name, short_name = :short_name, description = :description
WHERE id = :id AND user_id = :user_id
    """)
    db.execute(query, {
        "id": item_id,
        "user_id": user_id,
        "name": name,
        "short_name": short_name,
        "description": description
    })

    # 親IDが指定されており、かつ変更がある場合は移動処理を行う
    if new_parent_id is not None:
        # 現在の親IDを取得
        curr_query = text("SELECT parent_id FROM hadbit_trees WHERE item_id = :item_id AND user_id = :user_id")
        curr = db.execute(curr_query, {"item_id": item_id, "user_id": user_id}).fetchone()
        
        if curr and curr.parent_id != new_parent_id:
            # 移動先の親における最大order_noを取得して+1する
            max_order = get_hadbit_tree_max_sort_order(db, user_id, new_parent_id)
            new_order = (max_order or 0) + 1
            
            # ツリー情報を更新
            update_tree = text("""
                UPDATE hadbit_trees 
                SET parent_id = :pid, order_no = :ord 
                WHERE item_id = :iid AND user_id = :uid
            """)
            db.execute(update_tree, {
                "pid": new_parent_id,
                "ord": new_order,
                "iid": item_id,
                "uid": user_id
            })

def delete_hadbit_item(db: Session, item_id: int, user_id: str):
    """
    論理削除を行う（is_deletedフラグを立てる）
    """
    query = text("UPDATE hadbit_items SET is_deleted = true WHERE id = :id AND user_id = :user_id")
    db.execute(query, {"id": item_id, "user_id": user_id})

def restore_hadbit_item(db: Session, item_id: int, user_id: str):
    """
    削除を取り消す（is_deletedフラグを下ろす）
    """
    query = text("UPDATE hadbit_items SET is_deleted = false WHERE id = :id AND user_id = :user_id")
    db.execute(query, {"id": item_id, "user_id": user_id})

def update_hadbit_tree_order(db: Session, user_id: str, item_ids: list[int]):
    """
    渡されたitem_idのリスト順にorder_noを更新する
    """
    for index, item_id in enumerate(item_ids):
        query = text("""
            UPDATE hadbit_trees 
            SET order_no = :order_no 
            WHERE item_id = :item_id AND user_id = :user_id
        """)
        db.execute(query, {"order_no": index + 1, "item_id": item_id, "user_id": user_id})



def move_hadbit_item_up(db: Session, user_id: int, child_id: int):
    """
    指定されたアイテムを一つ上に移動（sort_orderを入れ替え）
    """
    # 1. 対象アイテムを取得
    query_curr = text("SELECT item_id, parent_id, order_no FROM hadbit_trees WHERE user_id = :uid AND item_id = :cid")
    curr = db.execute(query_curr, {"uid": user_id, "cid": child_id}).fetchone()

    if curr:
        # 2. 一つ上のアイテム（交換対象）を探す
        query_prev = text("""
            SELECT item_id, order_no FROM hadbit_trees 
            WHERE user_id = :uid AND parent_id = :pid AND order_no < :so 
            ORDER BY order_no DESC LIMIT 1
        """)
        prev = db.execute(query_prev, {"uid": user_id, "pid": curr.parent_id, "so": curr.order_no}).fetchone()

        # 3. 見つかれば sort_order を入れ替える
        if prev:
            update_sql = text("""
UPDATE 
hadbit_trees SET order_no = :so 
WHERE user_id = :uid AND item_id = :cid""")
            db.execute(update_sql, 
                    {"so": prev.order_no, 
                    "uid": user_id, 
                    "cid": curr.item_id
                    }
                )
            db.execute(update_sql, {"so": curr.order_no, "uid": user_id, "cid": prev.item_id})

def move_hadbit_item_down(db: Session, user_id: int, child_id: int):
    """
    指定されたアイテムを一つ下に移動（sort_orderを入れ替え）
    """
    # 1. 対象アイテムを取得
    query_curr = text("SELECT item_id, parent_id, order_no FROM hadbit_trees WHERE user_id = :uid AND item_id = :cid")
    curr = db.execute(query_curr, {"uid": user_id, "cid": child_id}).fetchone()

    if curr:
        # 2. 一つ下のアイテム（交換対象）を探す
        query_next = text("""
            SELECT item_id, order_no FROM hadbit_trees 
            WHERE user_id = :uid AND parent_id = :pid AND order_no > :so 
            ORDER BY order_no ASC LIMIT 1
        """)
        next_item = db.execute(query_next, {"uid": user_id, "pid": curr.parent_id, "so": curr.order_no}).fetchone()

        # 3. 見つかれば sort_order を入れ替える
        if next_item:
            update_sql = text("UPDATE hadbit_trees SET order_no = :so WHERE user_id = :uid AND item_id = :cid")
            db.execute(update_sql, {"so": next_item.order_no, "uid": user_id, "cid": curr.item_id})
            db.execute(update_sql, {"so": curr.order_no, "uid": user_id, "cid": next_item.item_id})
