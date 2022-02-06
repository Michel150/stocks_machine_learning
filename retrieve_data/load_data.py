# https://www.sec.gov/edgar/sec-api-documentation
# https://www.sec.gov/os/accessing-edgar-data
import requests
from lxml import etree
import data
import locale

locale.setlocale(locale.LC_ALL, 'de_DE.utf-8')
s = requests.Session()

def get_float(float_str):
    return locale.atof(float_str)

def get_val(num_str):
    parts = num_str.split()
    if len(parts) == 1:
        return int(locale.atof(parts[0]))
    if parts[1] == 'Mio.':
        return int(1e6 * locale.atof(parts[0]))
    return 0

def get_cur_val(num_str):
    parts = num_str.split()
    print(parts)
    if parts[1] == 'M€':
        return int(1e6 * locale.atof(parts[0][:-2]))
    if parts[1] == '€':
        return locale.atof(parts[0][:-2])
    print(f'unknown currency {parts[0]}-{parts[1]}, return 0 as conversion')
    return 0

def load_0(year, params, converters):
    data = {
        "page":"0",
        "page_size": 100,
        "year": f"_year_{year}",
        "sales": "50000_",
    }
    data.update(params)
    r = s.post('https://www.ariva.de/aktiensuche/_result_table.m',
        data=data)
    if r.status_code != 200:
        return []

    root = etree.HTML(r.content.decode('utf-8'))
    tables = root.xpath('//table')
    table = tables[0]
    rows = table.xpath('./tbody/tr')
    for row in rows:
        columns = row.xpath('./td')
        href = columns[1].xpath('./a/@href')[0][1:-6]
        sales = get_cur_val(columns[4].text)

        vals = []
        for i, converter in enumerate(converters):
            vals.append(converter(columns[5 + i].text))
        yield (href, sales, *vals)

def load_data(year):
    companies = dict()

    params_0 = {
        "profit_loss": "-50000_",
        "sum_assets": "-2_",
        "sum_liabilities": "-1_",
        "number_of_shares": "-1_"
    }
    converters_0 = [get_cur_val, get_cur_val, get_cur_val, get_val]
    for entry in load_0(year, params=params_0, converters=converters_0):
        ext = data.ext_company(*entry)
        companies[entry[0]] = ext

    params_1 = {
        "earnings_per_share": "-10000_",
        "dividend_per_share": "-1_",
        "number_of_employees": "-1_"
    }
    converters_1 = [get_cur_val, get_cur_val, get_val]
    for entry in load_0(year, params=params_1, converters=converters_1):
        companies[entry[0]].set_data_1(*entry)

    params_2 = {
        "kgv": "-1000_",
        "kuv": "-1_",
        "kbv": "-1_"
    }
    converters_2 = [get_float, get_float, get_float]
    for entry in load_0(year, params=params_2, converters=converters_2):
        companies[entry[0]].set_data_2(*entry)

    print(companies)
#    companies = load_1(year)
#    print(companies)

load_data(2016)