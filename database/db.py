import os
import sqlite3
from datetime import datetime

conn = sqlite3.connect(os.path.join('database', 'party.db'))
cursor = conn.cursor()

def _init_db():
    with open('database/createdb.sql', 'r') as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()

def check_db_exists():
    cursor.execute("select name from sqlite_master where type='table' and name='expense'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()

def insert(table: str, column_values: dict):
    columns = ', '.join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ', '.join('?' * len(column_values.keys()))
    cursor.executemany(f'insert into {table} ({columns}) values ({placeholders})', values)
    conn.commit()

def fetchall(table: str, columns: list[str]) -> list[tuple]:
    cursor.execute(f"select {', '.join(columns)} from {table}")
    rows = cursor.fetchall()
    return [{column: row[index] for index, column in enumerate(columns)} for row in rows]

def delete(table: str, row_id: int) -> None:
    row_id = int(row_id)
    cursor.execute(f'delete from {table} where id={row_id}')
    conn.commit()

def get_cursor():
    return cursor

async def touch(user_data: dict):
    # insert info about user himself
    for item in fetchall('user', ['full_name', 'user_id']):
        if user_data['name'] in item.values():
            user_id = item['user_id']
            break
    else:   
        insert('user', {'full_name': user_data['name']})
        user_id, = get_cursor().execute("select user_id from user where full_name = ?", [user_data['name']]).fetchone()
    
    # insert info about user's choice
    if 'other' in user_data.keys():
        try:
            chosen_food = user_data['chosen_food']
        except KeyError:
            insert(
                'alcohol', 
                {
                    'user_id': user_id, 
                    'chosen_alcohol': user_data['chosen_alcohol'], 
                    'amount': user_data['amount'],
                    'other': user_data['other'],
                    'wishing_time': datetime.now()
                }
            )
        else:
            insert(
                'food', 
                {
                    'user_id': user_id, 
                    'chosen_food': user_data['chosen_food'], 
                    'amount': user_data['amount'],
                    'other': user_data['other'],
                    'wishing_time': datetime.now()
                }
            )
    else:
        try:
            chosen_food = user_data['chosen_food']
        except KeyError:
            insert(
                'alcohol', 
                {
                    'user_id': user_id, 
                    'chosen_alcohol': user_data['chosen_alcohol'], 
                    'amount': user_data['amount'],
                    'wishing_time': datetime.now()
                }
            )
        else:
            insert(
                'food',
                {
                    'user_id': user_id, 
                    'chosen_food': user_data['chosen_food'], 
                    'amount': user_data['amount'],
                    'wishing_time': datetime.now()
                }
            )

async def get_list(full_name: str):
    cursor.execute('''with tab as (
        select t2.id, t2.chosen_food choice, t2.amount, t2.other
        from user t1
        join food t2 on t1.user_id = t2.user_id
        where t1.full_name = ?
        UNION
        select t2.id, t2.chosen_alcohol, t2.amount, t2.other 
        from user t1
        join alcohol t2 on t1.user_id = t2.user_id
        where t1.full_name = ?
    )
    select row_number() over() item_id, * 
    from tab''', (full_name,full_name))
    return cursor.fetchall()

check_db_exists()