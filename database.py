import sqlite3

DB_NAME = 'models.db'


def connect_db():
    return sqlite3.connect(DB_NAME)


def create_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS models(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_id TEXT NOT NULL UNIQUE,
        task TEXT NOT NULL,
        downloads INTEGER NOT NULL DEFAULT 0,
        license TEXT NOT NULL,
        safetensors INTEGER NOT NULL DEFAULT 0,
        trust INTEGER NOT NULL DEFAULT 0,
        reviewed INTEGER NOT NULL DEFAULT 0,
        memo TEXT NOT NULL DEFAULT '')""")

    conn.commit()
    conn.close()


def add_model(model_id, task, downloads=0, license_name='정보 없음', safetensors=0, memo=''):
    """저장에 성공하면 True, 이미 있는 모델이면 False."""
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""INSERT INTO models(model_id, task, downloads, license, safetensors, memo)
                          VALUES (?, ?, ?, ?, ?, ?)""",
                       (model_id, task, downloads, license_name, safetensors, memo))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_all_models():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""SELECT id, model_id, task, downloads, license, safetensors,
                             trust, reviewed, memo
                      FROM models
                      ORDER BY id DESC""")
    rows = cursor.fetchall()

    conn.close()
    return rows


def search_models(keyword, safetensors_filter='전체'):
    """모델 이름 검색 + safetensors 필터를 함께 적용한다."""
    conn = connect_db()
    cursor = conn.cursor()

    query = """SELECT id, model_id, task, downloads, license, safetensors,
                      trust, reviewed, memo
               FROM models
               WHERE model_id LIKE ? ESCAPE '\\'"""
    # 검색어의 %, _ 는 와일드카드가 아니라 글자 그대로 찾는다.
    escaped = keyword.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
    params = [f"%{escaped}%"]

    if safetensors_filter == '있음':
        query += " AND safetensors = 1"
    elif safetensors_filter == '없음':
        query += " AND safetensors = 0"

    query += " ORDER BY id DESC"

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()

    conn.close()
    return rows


def toggle_reviewed(model_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT reviewed FROM models WHERE id = ?", (model_id,))
    row = cursor.fetchone()

    if row is None:
        conn.close()
        return False

    new_value = 0 if row[0] == 1 else 1
    cursor.execute("UPDATE models SET reviewed = ? WHERE id = ?", (new_value, model_id))
    conn.commit()
    conn.close()
    return True


def update_trust(model_id, trust):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE models SET trust = ? WHERE id = ?", (trust, model_id))
    conn.commit()
    changed = cursor.rowcount

    conn.close()
    return changed


def update_memo(model_id, memo):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE models SET memo = ? WHERE id = ?", (memo, model_id))
    conn.commit()
    changed = cursor.rowcount

    conn.close()
    return changed


def delete_model(model_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM models WHERE id = ?", (model_id,))
    conn.commit()
    changed = cursor.rowcount

    conn.close()
    return changed


def get_summary():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*), SUM(safetensors), SUM(reviewed) FROM models")
    total, safe_count, reviewed_count = cursor.fetchone()

    cursor.execute("""SELECT task, COUNT(*)
                      FROM models
                      GROUP BY task
                      ORDER BY COUNT(*) DESC, task""")
    by_task = cursor.fetchall()

    conn.close()
    return {
        'total': total or 0,
        'safetensors': safe_count or 0,
        'reviewed': reviewed_count or 0,
        'by_task': by_task,
    }


# create_table()
# print(add_model('google-bert/bert-base-uncased', 'fill-mask', 29311111, 'apache-2.0', 1))
# print(get_all_models())
# print(get_summary())
