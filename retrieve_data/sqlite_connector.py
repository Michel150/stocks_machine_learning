import sqlite3

def get_line(file):
    l = file.readline()
    empty = False
    while l is not None and len(l) > 2:
        if not empty:
            yield l
        try: 
            l = file.readline()
            empty = False
        except UnicodeDecodeError as e:
            empty = True

def generate_db(create = False, companies = []):
    conn = sqlite3.connect('companies.db')
    if create:
        conn.execute('''CREATE TABLE COMPANY
                (href TEXT PRIMARY KEY     NOT NULL,
                isin           INT,
                name           TEXT    NOT NULL);''')
    if len(companies) > 0:
        records = [(c.href, c.isin, c.name) for c in companies]
        conn.executemany('INSERT INTO COMPANY VALUES(?,?,?);',records);

    print('start commit')
    conn.commit()
    print('end commit')

    conn.close()

#generate_db(create=True)