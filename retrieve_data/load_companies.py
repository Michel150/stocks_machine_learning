import requests
from lxml import etree
import data


def load_year(year):
    companies = []
    s = requests.Session()
    wanted_ps = 100
    actual_ps = wanted_ps
    p = 0
    while p < 10 and actual_ps == wanted_ps:
        actual_ps = 0
        r = s.post('https://www.ariva.de/aktiensuche/_result_table.m',
            data={
                "page":f"{p}",
                "page_size": wanted_ps,
                "sort": "sales",
                "sort_d": "desc",
                "year": f"_year_{year}",
                "sales": "10000_"
            })
        if r.status_code != 200:
            return []
        root = etree.HTML(r.content.decode('utf-8'))
        tables = root.xpath('//table')
        table = tables[0]
        rows = table.xpath('./tbody/tr')
        for row in rows:
            columns = row.xpath('./td')
            href = columns[1].xpath('./a/@href')[0][1:-6]
            name = columns[1].xpath('./a/text()')[0]
            companies.append(data.company(href, name))
            actual_ps += 1
        print(f'looked at page {p} with {actual_ps} entries')
        p += 1
    return companies
