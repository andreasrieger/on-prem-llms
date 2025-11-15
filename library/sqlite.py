import sqlite3

def create_table():

    '''Function to create the database table if it does not exist'''

    db = sqlite3.connect('db.sqlite')
    c = db.cursor()
    c.execute('''
              CREATE TABLE if not exists recordings (
                  id INTEGER PRIMARY KEY,
                  url VARCHAR(30),
                  filename VARCHAR(30),
                  duration INTEGER,
                  blocksize INTEGER,
                  startdatetime TEXT
              );
    ''')
    db.commit()


def write_db(db, url, filename, duration, blocksize, startdatetime):

    '''Function to write data to database'''

    c = db.cursor()
    sql = '''
        INSERT INTO recordings(url, filename, duration, blocksize, startdatetime)
        VALUES (?,?,?,?,?)
    '''
    c.execute(sql, (url, filename, duration, blocksize, startdatetime))
    db.commit()


def read_db(db):

    '''Function to read the database'''

    c = db.cursor()
    sql = '''
        SELECT * FROM recordings
    '''
    c.execute(sql)
    print_db_entries(c.fetchall())