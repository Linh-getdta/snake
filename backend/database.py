import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path


DATABASE_NAME = Path(__file__).resolve().with_name("snake.db")


def get_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_connetion():
    return get_connection()


@contextmanager
def _database():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def creat_player_table():
    with _database() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS NGUOI_CHOI (
                PLAYER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                NAME_PLAYER TEXT NOT NULL
            )
        """)


def creat_result_table():
    with _database() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS KET_QUA (
                KETQUA_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                PLAYER_ID INTEGER NOT NULL,
                DIEM INTEGER NOT NULL,
                PLAYED_AT TEXT NOT NULL,
                FOREIGN KEY (PLAYER_ID) REFERENCES NGUOI_CHOI(PLAYER_ID)
            )
        """)


def create_player_table():
    creat_player_table()


def create_result_table():
    creat_result_table()


def check_table_player():
    with _database() as conn:
        columns = conn.execute("PRAGMA table_info(NGUOI_CHOI)").fetchall()
    for column in columns:
        print(column)
    return columns


def check_table_result():
    with _database() as conn:
        columns = conn.execute("PRAGMA table_info(KET_QUA)").fetchall()
    for column in columns:
        print(column)
    return columns


def add_players(name):
    with _database() as conn:
        cursor = conn.execute(
            "INSERT INTO NGUOI_CHOI(NAME_PLAYER) VALUES (?)",
            (name,),
        )
        return cursor.lastrowid


def get_players():
    with _database() as conn:
        players = conn.execute(
            "SELECT PLAYER_ID, NAME_PLAYER FROM NGUOI_CHOI"
        ).fetchall()
    for player in players:
        print(player)
    return players


def add_result(player_id, diem, played_at):
    with _database() as conn:
        cursor = conn.execute(
            """
            INSERT INTO KET_QUA(PLAYER_ID, DIEM, PLAYED_AT)
            VALUES (?, ?, ?)
            """,
            (player_id, diem, played_at),
        )
        return cursor.lastrowid


def save_game(player_name, score):
    with _database() as conn:
        cursor = conn.execute(
            "SELECT PLAYER_ID FROM NGUOI_CHOI WHERE NAME_PLAYER = ?",
            (player_name,),
        )
        player = cursor.fetchone()

        if player is None:
            cursor = conn.execute(
                "INSERT INTO NGUOI_CHOI(NAME_PLAYER) VALUES (?)",
                (player_name,),
            )
            player_id = cursor.lastrowid
        else:
            player_id = player[0]

        played_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            """
            INSERT INTO KET_QUA(PLAYER_ID, DIEM, PLAYED_AT)
            VALUES (?, ?, ?)
            """,
            (player_id, score, played_at),
        )


def get_results():
    with _database() as conn:
        results = conn.execute("""
            SELECT KET_QUA.KETQUA_ID,
                   NGUOI_CHOI.NAME_PLAYER,
                   KET_QUA.DIEM,
                   KET_QUA.PLAYED_AT
            FROM KET_QUA
            JOIN NGUOI_CHOI
                ON KET_QUA.PLAYER_ID = NGUOI_CHOI.PLAYER_ID
        """).fetchall()
    for result in results:
        print(result)
    return results


def delete_player(player_id):
    with _database() as conn:
        cursor = conn.execute(
            "DELETE FROM NGUOI_CHOI WHERE PLAYER_ID = ?",
            (player_id,),
        )
        return cursor.rowcount


def get_play_count(player_id):
    with _database() as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM KET_QUA WHERE PLAYER_ID = ?",
            (player_id,),
        ).fetchone()
    return row[0]


def get_leaderboard(limit=10):
    with _database() as conn:
        leaderboard = conn.execute(
            """
            SELECT NGUOI_CHOI.NAME_PLAYER, KET_QUA.DIEM
            FROM KET_QUA
            JOIN NGUOI_CHOI
                ON KET_QUA.PLAYER_ID = NGUOI_CHOI.PLAYER_ID
            ORDER BY KET_QUA.DIEM DESC,
                     KET_QUA.PLAYED_AT ASC,
                     KET_QUA.KETQUA_ID ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return leaderboard


if __name__ == "__main__":
    creat_player_table()
    creat_result_table()
    get_results()
