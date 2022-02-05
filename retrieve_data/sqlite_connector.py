#!/usr/bin/python

import sqlite3

def generate_db(create = False, write = False):
    conn = sqlite3.connect('cik-lookup.db')
    if create:
        conn.execute('''CREATE TABLE COMPANY
                (cik INT PRIMARY KEY     NOT NULL,
                NAME           TEXT    NOT NULL);''')

    if write:
        with open('cik-lookup-data.txt', 'r') as f:
            cps = []
            l = f.readline()
            empty = False
            while l is not None:
                if not empty:
                    try:
                        line_split = l.split(":")
                        N = len(line_split)
                        name = "".join(line_split[:N - 2])
                        cik = int(line_split[N - 2])
                        cps.append((cik, name))
                    except:
                        pass
                try:
                    l = f.readline()
                    empty = False
                except:
                    empty = True

            print(len(cps))
            conn.executemany("INSERT INTO COMPANY ('cik', 'NAME') VALUES (?, ?)", cps)
            conn.commit()


    conn.close()

generate_db(write=True)