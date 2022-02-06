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

def save_quotes(conn, year, companies):
    records = []
    for c in companies.values():
        if c.data1 and c.data2:
            market_cap = int( c.sales * c.kuv )
            records.append((year, c.href, market_cap, c.dividend_per_share * c.number_of_shares))
    conn.executemany('INSERT INTO QUOTES VALUES(?,?,?,?);',records);

def save_balance_sheet(conn, year, companies):
    records = []
    for c in companies.values():
        if c.data1:
            records.append((year, c.href, c.number_of_shares, c.sum_assets, c.sum_liabilities, c.number_of_employees))
    print(records[:10])
    conn.executemany('INSERT INTO BALANCE_SHEET VALUES(?,?,?,?,?,?);',records);

def save_income_statement(conn, year, companies):
    records = [(year, c.href, c.sales, c.profit_loss) for c in companies.values()]
    conn.executemany('INSERT INTO INCOME_STATEMENT VALUES(?,?,?,?);',records);


def save_company_infos(year, companies):
    conn = sqlite3.connect('companies.db')

    print('store income')
    save_income_statement(conn, year, companies)
    print('store quotes')
    save_quotes(conn, year, companies)
    print('store balance')
    save_balance_sheet(conn, year, companies)

    conn.commit()
    conn.close()
    

#generate_db(create=True)