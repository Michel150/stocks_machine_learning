import sqlite_connector
import numpy as np
import itertools

HREF = 1
CAP = 2
DIV = 3

def create_hrefs(href_to_idx, fh):
    hrefs_uf = [''] * len(href_to_idx)
    for href, idx in href_to_idx.items():
        hrefs_uf[idx] = href
    hrefs = []
    for filter, href in zip(fh, hrefs_uf):
        if filter:
            hrefs.append(href)
    return hrefs

def two_yr_change(conn, year):
    res = []
    for i in range(3):
        res.append(sqlite_connector.load_quotes_for_years(conn, year + i))

    c = 0
    href_to_idx = dict()
    for e in itertools.chain(*res):
        if e[HREF] not in href_to_idx:
            href_to_idx[e[HREF]] = c
            c += 1

    caps = np.zeros((c, 3))
    divs = np.zeros((c, 3))
    for i in range(3):
        for e in res[i]:
            idx = href_to_idx[e[HREF]]
            caps[idx, i] = e[CAP]
            divs[idx, i] = e[DIV]

    fh = (caps[:,0] * caps[:,1] * caps[:, 2]) != 0

    new_val = caps[fh, 2] + np.sum(divs[fh, 1:], axis=1)
    change = (new_val / caps[fh,0]) - 1

    return (create_hrefs(href_to_idx, fh), change)

def one_yr_change(conn, year, hrefs):
    res = []
    for i in range(2):
        res.append(sqlite_connector.load_quotes_for_years(conn, year + i))

    href_to_idx = dict()
    for i, href in enumerate(hrefs):
        href_to_idx[href] = i

    caps = np.zeros((len(hrefs), 2))
    divs = np.zeros((len(hrefs), 2))
    for i in range(2):
        for e in res[i]:
            if e[HREF] in href_to_idx:
                idx = href_to_idx[e[HREF]]
                caps[idx, i] = e[CAP]
                divs[idx, i] = e[DIV]


    fh = (caps[:,0] * caps[:,1]) != 0

    change  = np.zeros(len(hrefs))
    change[fh] = (caps[fh, 1] + divs[fh, 1]) / caps[fh,0] - 1

    return change

def kgv(conn, year, hrefs):
    kgvs = np.zeros(len(hrefs))
    for i, href in enumerate(hrefs):
        r = sqlite_connector.load_kgv_data(conn, year, href)
        if len(r) == 1:
            kgvs[i] = r[0][1] / r[0][0]
    return kgvs

def kuv(conn, year, hrefs):
    kuvs = np.zeros(len(hrefs))
    for i, href in enumerate(hrefs):
        r = sqlite_connector.load_kuv_data(conn, year, href)
        if len(r) == 1:
            kuvs[i] = r[0][1] / r[0][0]
    return kuvs

def kbv(conn, year, hrefs):
    kbvs = np.zeros(len(hrefs))
    for i, href in enumerate(hrefs):
        r = sqlite_connector.load_kbv_data(conn, year, href)
        if len(r) == 1:
            kbvs[i] = r[0][2] / (r[0][0] - r[0][1])
    return kbvs

def div_rend(conn, year, hrefs):
    kbvs = np.zeros(len(hrefs))
    for i, href in enumerate(hrefs):
        r = sqlite_connector.load_quotes(conn, year, href)
        if len(r) == 1:
            kbvs[i] = r[0][1] / r[0][0]
    return kbvs




