import sqlite3

################### write to db #################

def generate_db():
    conn = sqlite3.connect('companies.db')
    conn.execute('''CREATE TABLE COMPANY
            (href TEXT PRIMARY KEY     NOT NULL,
            isin           INT,
            name           TEXT    NOT NULL);''')

    print('start commit')
    conn.commit()
    print('end commit')

    conn.close()

def save_companies(conn, companies):
    records = [(c.href, c.isin, c.name) for c in companies]
    conn.executemany('INSERT or IGNORE INTO COMPANY VALUES(?,?,?);',records);

def save_quotes(conn, year, companies):
    records = []
    for c in companies.values():
        if c.data1 and c.data2:
            market_cap = int( c.sales * c.kuv )
            records.append((year, c.href, market_cap, c.dividend_per_share * c.number_of_shares))
    conn.executemany('INSERT or IGNORE INTO QUOTES VALUES(?,?,?,?)' ,records);

def save_balance_sheet(conn, year, companies):
    records = []
    for c in companies.values():
        if c.data1:
            records.append((year, c.href, c.number_of_shares, c.sum_assets, c.sum_liabilities, c.number_of_employees))
    conn.executemany('INSERT or IGNORE INTO BALANCE_SHEET VALUES(?,?,?,?,?,?);',records);

def save_income_statement(conn, year, companies):
    records = [(year, c.href, c.sales, c.profit_loss) for c in companies.values()]
    conn.executemany('INSERT or IGNORE INTO INCOME_STATEMENT VALUES(?,?,?,?);',records);


def save_company_infos(year, companies):
    conn = get_db()

    print('store income')
    save_income_statement(conn, year, companies)
    print('store quotes')
    save_quotes(conn, year, companies)
    print('store balance')
    save_balance_sheet(conn, year, companies)

    conn.commit()
    conn.close()
    
########### access db ###################
def get_db(off='./'):
    return sqlite3.connect(f'{off}retrieve_data/companies.db')

def entry_exists(conn, year, href, table):
    cur = conn.cursor()
    if table == "QUOTES":
        cur.execute('SELECT href FROM QUOTES WHERE year==? AND href==?;', (year, href))
    if table == "BALANCE_SHEET":
        cur.execute('SELECT href FROM BALANCE_SHEET WHERE year==? AND href==?;', (year, href))
    if table == "INCOME_STATEMENT":
        cur.execute('SELECT href FROM INCOME_STATEMENT WHERE year==? AND href==?;', (year, href))
    r = cur.fetchone()
    return r is not None

def load_quotes_for_years(conn, year):
    cur = conn.cursor()
    cur.execute('SELECT * FROM QUOTES WHERE year==:yp ORDER BY href;', {"yp":year})
    return cur.fetchall()

def load_quotes(conn, year, href):
    sql = 'SELECT Q.marketcap, Q.dividends FROM QUOTES Q WHERE Q.href==? AND Q.year==?;'
    return fetchall(conn, sql, (href, year))

def fetchall(conn, sql, params):
    cur = conn.cursor()
    cur.execute(sql, params)
    return cur.fetchall()

def load_kgv_data(conn, year, href):
    sql = ("SELECT I.income, Q.marketcap FROM INCOME_STATEMENT I INNER JOIN QUOTES Q "
        "ON I.href == Q.href AND I.year == Q.year WHERE I.href==? AND I.year==?;")
    return fetchall(conn, sql, (href, year))

def load_kuv_data(conn, year, href):
    sql = ("SELECT I.return, Q.marketcap FROM INCOME_STATEMENT I INNER JOIN QUOTES Q "
        "ON I.href == Q.href AND I.year == Q.year WHERE I.href==? AND I.year==?;")
    return fetchall(conn, sql, (href, year))

def load_kbv_data(conn, year, href):
    sql = ("SELECT B.aktiva, B.passiva, Q.marketcap FROM BALANCE_SHEET B INNER JOIN QUOTES Q "
         "ON B.href == Q.href AND B.year == Q.year WHERE B.href==? AND B.year==?;")
    return fetchall(conn, sql, (href, year))
