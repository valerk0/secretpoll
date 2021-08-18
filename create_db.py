import psycopg2
from urllib.parse import urlparse
import os

class DB:

    def __init__(self):
        db_config = urlparse(os.environ['DATABASE_URL'])
        self.conn=psycopg2.connect(user=db_config.username,
                                     password=db_config.password,
                                     database=db_config.path[1:],
                                     host=db_config.hostname)

    def __del__(self):
        self.conn.close()

    def create_poll_tbl(self):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                    create table poll (
                    pollid varchar(40) primary key,
                    question text,
                    creator bigint,
                    isactive boolean
                    );
                ''')

    def set_null_poll(self):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             insert into poll (pollid, question, creator, isactive) 
                             values ('{0}', '{1}', {2}, {3});
                             '''.format('', '', 0, False))

    def drop_poll_tbl(self):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                    drop table poll cascade;
                ''')

    def create_answer_tbl(self):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                    create table answer (
                    answerid varchar(40) primary key,
                    pollid varchar(40) references poll on delete cascade,
                    answer text
                    );
                ''')

    def drop_answer_tbl(self):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                    drop table answer cascade;
                ''')

    def create_user_answer_tbl(self):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                    create table user_answer (
                    uid bigint,
                    pollid varchar(40) references poll on delete cascade,
                    answerid varchar(40) references answer on delete cascade,
                    primary key (uid, answerid)
                    );
                ''')

    def drop_user_answer_tbl(self):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                    drop table user_answer cascade;
                ''')

    def create_user_mode_tbl(self):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                    create table user_mode (
                    uid bigint primary key,
                    umode varchar(8),
                    pollid varchar(40) references poll on delete set null
                    );
                ''')

    def drop_user_mode_tbl(self):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                    drop table user_mode cascade;
                ''')

    def create_tbls(self):
        self.create_poll_tbl()
        self.create_answer_tbl()
        self.create_user_answer_tbl()
        self.create_user_mode_tbl()

if __name__ == '__main__':
    db = DB()
    #db.drop_user_mode_tbl()
    #db.create_tbls()
    db.set_null_poll()
