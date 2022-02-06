# https://www.sec.gov/edgar/sec-api-documentation
# https://www.sec.gov/os/accessing-edgar-data
import requests
from lxml import etree

s = requests.Session()

def load_0(year):
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
    print(r.content.decode('utf-8'))
    root = etree.HTML(r.content.decode('utf-8'))
    companies = []
    tables = root.xpath('//table')
    table = tables[0]
    rows = table.xpath('./tbody/tr')
    for row in rows:
        columns = row.xpath('./td')
        href = columns[1].xpath('./a/@href')[0][1:-6]
        name = columns[1].xpath('./a/text()')[0]
        companies.append(company(href, name))
    return companies

def load_data(year):