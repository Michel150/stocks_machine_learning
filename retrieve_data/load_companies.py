import requests
from lxml import etree
import sqlite_connector
import data


def load_year(year):
    s = requests.Session()
    r = s.post('https://www.ariva.de/aktiensuche/_result_table.m',
        data={
            "page":"0",
            "page_size": 100,
            "sort": "sales",
            "sort_d": "desc",
            "year": f"_year_{year}",
            "sales": "50000_"
        })
    if r.status_code != 200:
        return []
    root = etree.HTML(r.content.decode('utf-8'))
    companies = []
    tables = root.xpath('//table')
    table = tables[0]
    rows = table.xpath('./tbody/tr')
    for row in rows:
        columns = row.xpath('./td')
        href = columns[1].xpath('./a/@href')[0][1:-6]
        name = columns[1].xpath('./a/text()')[0]
        companies.append(data.company(href, name))
    return companies

companies = load_year(2016)
print(companies)
#sqlite_connector.generate_db(companies=companies)