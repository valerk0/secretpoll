import psycopg2
from urllib.parse import urlparse
from uuid import uuid4
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

    def get_user_mode(self, uid):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             select umode, pollid from user_mode where uid='{}';
                             '''.format(uid))
                mode_data = curs.fetchall()
                data_row = mode_data[0] if mode_data else None
                umode = data_row[0] if data_row else 'Ready'
                pollid = data_row[1] if data_row else None
        return umode, pollid

    def set_user_mode(self, uid, umode, pollid=None):
        # Modes: 'Ready', 'Question', 'Answer'
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             insert into user_mode (uid, umode, pollid) 
                             values ('{0}', '{1}', '{2}')
                             on conflict (uid) do update set umode='{1}', pollid='{2}';
                             '''.format(uid, umode, (pollid or '')))

    def create_poll(self, question, author):
        pollid = str(uuid4())
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             insert into poll (pollid, question, creator, isactive) 
                             values ('{0}', '{1}', {2}, {3});
                             '''.format(pollid, question, author, False))
        return pollid
    
    def set_poll_active(self, pollid, isactive=True):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             update poll set isactive={0} where pollid='{1}';
                             '''.format(isactive, pollid))

    def is_poll_active(self, pollid):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             select isactive from poll where pollid='{0}';
                             '''.format(pollid))
                result = curs.fetchall()
                isactive = result[0][0] if result and result[0] else False
        return isactive

    def poll_exists(self, pollid):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             select pollid from poll where pollid='{0}';
                             '''.format(pollid))
                result = curs.fetchall()
                exists = result and result[0] and result[0][0]
        return exists

    def get_creator(self, pollid):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             select creator from poll where pollid='{0}';
                             '''.format(pollid))
                result = curs.fetchall()
                creator = result and result[0] and result[0][0]
        return creator

    def delete_poll(self, pollid):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             delete from poll where pollid='{}';
                             '''.format(pollid))

    def add_answer(self, pollid, answer):
        answerid = str(uuid4())
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             insert into answer (answerid, pollid, answer) 
                             values ('{0}', '{1}', '{2}');
                             '''.format(answerid, pollid, answer))
        return answerid
    
    def add_user_answer(self, uid, pollid, answerid):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             insert into user_answer (uid, pollid, answerid) 
                             values ('{0}', '{1}', '{2}');
                             '''.format(uid, pollid, answerid))

    def get_user_poll_list(self, uid):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             select question, pollid from poll where creator={0};
                             '''.format(uid))
                polls = curs.fetchall()
        return polls

    def get_poll_question(self, pollid):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             select question from poll where pollid='{0}';
                             '''.format(pollid))
                result = curs.fetchall()
                question = result and result[0] and result[0][0]
        return question

    def get_answer_list(self, pollid):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             select answer, answerid from answer where pollid='{0}';
                             '''.format(pollid))
                answers = curs.fetchall()
        return answers

    def get_answer_count_list(self, pollid):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             select a.answer, max(ac.acount) from answer a
                             left join
                             (select answerid, 
                             count (answerid) over (partition by answerid) as acount
                             from user_answer 
                             where pollid='{0}') ac
                             on a.answerid=ac.answerid
                             where a.pollid='{0}'
                             group by a.answer;
                             '''.format(pollid))
                answers = curs.fetchall()
        return answers
    
    def get_user_answer(self, pollid, uid):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             select answer from answer a
                             inner join user_answer ua 
                             on a.answerid=ua.answerid
                             where ua.uid='{0}' and ua.pollid='{1}';
                             '''.format(uid, pollid))
                answers = curs.fetchall()
        return answers

    def get_pollid_from_aid(self, aid):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute('''
                             select pollid from answer 
                             where answerid='{0}';
                             '''.format(aid))
                result = curs.fetchall()
                pollid = result[0][0] if result and result[0] else None
        return pollid
