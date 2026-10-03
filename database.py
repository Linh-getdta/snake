import sqlite3

DATABASE_NAME = "snake.db" 

def get_connetion(): # kết nối đến database
    
    return sqlite3.connect(DATABASE_NAME) #nếu file chưa tồn tại thì tạo file, nếu tồn tại thì mở file đó

def creat_player_table():
    conn = get_connetion()
    
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS NGUOI_CHOI (
            PLAYER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME_PLAYER TEXT NOT NULL
        )
    """)
    conn.commit()
    
    conn.close()

def creat_result_table():
    conn = get_connetion()
    cursor = conn.cursor()
    
    cursor.execute(
        """
             CREATE TABLE IF NOT EXISTS KET_QUA (
            KETQUA_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            PLAYER_ID INTEGER NOT NULL,
            DIEM INTEGER NOT NULL,
            PLAYED_AT TEXT NOT NULL,

            FOREIGN KEY (PLAYER_ID)
                REFERENCES NGUOI_CHOI(PLAYER_ID)
        
        )"""
    )
    conn.commit
    conn.close
    
def check_table_player():
    conn = get_connetion()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(NGUOI_CHOI)")
    columns = cursor.fetchall()
    for colum in columns:
        print(colum)
        
    conn.close
    
def check_table_result():
    conn = get_connetion()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(KET_QUA)")
    columns = cursor.fetchall()
    for colum in columns:
        print(colum)
        
    conn.close()
    
def add_players(name):
    conn = get_connetion()
    cursor = conn.cursor()
    cursor.execute("""
                   INSERT  INTO NGUOI_CHOI(NAME_PLAYER)
                   VALUES(?)
                   """,(name,))
    
    conn.commit()
    conn.close()
def get_players():
    conn = get_connetion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT PLAYER_ID, NAME_PLAYER
        FROM NGUOI_CHOI
    """)
    players = cursor.fetchall()
    for player in players :
        print(player)

    conn.close()
    
def add_result(player_id, diem, played_at):
    conn = get_connetion()
    cursor = conn.cursor()
    cursor.execute("""
                   INSERT INTO KET_QUA(PLAYER_ID, DIEM, PLAYED_AT)
                   VALUES(?,?,?)""", (player_id, diem, played_at)
                   )
    conn.commit()
    conn.close()

def get_results():
    conn = get_connetion()
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT KET_QUA.KETQUA_ID,
                        NGUOI_CHOI.NAME_PLAYER,
                        KET_QUA.DIEM,
                        KET_QUA.PLAYED_AT
                    FROM KET_QUA
                    JOIN NGUOI_CHOI
                    ON KET_QUA.PLAYER_ID = NGUOI_CHOI.PLAYER_ID
                    """)      
    results = cursor.fetchall()
    for result in results:
        print(result)
    conn.close
def delete_player(player_id):

    conn = get_connetion()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM NGUOI_CHOI
        WHERE PLAYER_ID = ?
    """, (player_id,))

    conn.commit()
    conn.close()  
    
def get_play_count(player_id):
    conn = get_connetion()
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT COUNT(*)
                   FROM KET_QUA
                   WHERE PLAYER_ID = ?
                   """
                ,(player_id,)
                )  
    count = cursor.fetchone()[0]
    cursor.close()
    return count 

def get_leaderboard():
    conn = get_connetion()
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT NGUOI_CHOI.NAME_PLAYER,
                        KET_QUA.DIEM
                    FROM KET_QUA
                    JOIN NGUOI_CHOI
                    ON KET_QUA.PLAYER_ID = NGUOI_CHOI.PLAYER_ID
                    ORDER BY KET_QUA.DIEM DESC""")
    
    leaderboard = cursor.fetchall()
    cursor.close()
    return leaderboard

if __name__ == "__main__":
    
    
    creat_player_table()
    creat_result_table()
    get_results()
    

   
    



