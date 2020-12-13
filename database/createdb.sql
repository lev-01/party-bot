create table if not exists user(
    user_id INTEGER PRIMARY KEY autoincrement,
    full_name varchar(100)
);

create table if not exists food(
    id integer primary key autoincrement,
    user_id integer,
    chosen_food varchar(100),
    amount varchar(100),
    other varchar(100),
    wishing_time datetime,
    FOREIGN KEY(user_id) REFERENCES user(user_id)
);

create table if not exists alcohol(
    id integer primary key AUTOINCREMENT,
    user_id integer,
    chosen_alcohol varchar(100),
    amount varchar(100),
    other varchar(100),
    wishing_time datetime,
    FOREIGN KEY(user_id) REFERENCES user(user_id)
);