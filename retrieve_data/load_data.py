# https://www.sec.gov/edgar/sec-api-documentation
# https://www.sec.gov/os/accessing-edgar-data
import requests
from lxml import etree
import data
import locale
import sqlite_connector

locale.setlocale(locale.LC_ALL, 'de_DE.utf-8')
s = requests.Session()

def get_float(float_str):
    return locale.atof(float_str)

def get_val(num_str):
    parts = num_str.split()
    if len(parts) == 1:
        return int(locale.atof(parts[0]))
    if parts[1] == 'Mio.'or 'M':
        return int(1e6 * locale.atof(parts[0]))
    return 0

def get_cur_val(num_str):
    parts = num_str.split()
    if parts[1] == 'M€':
        return int(1e6 * locale.atof(parts[0]))
    if parts[1] == '€':
        return locale.atof(parts[0])
    print(f'unknown currency {parts[0]}-{parts[1]}, return 0 as conversion')
    return 0

def load_0(year, params, converters):
    wanted_ps = 100
    actual_ps = wanted_ps
    p = 0

    data = {
        "page":f"{p}",
        "page_size": wanted_ps,
        "year": f"_year_{year}",
        "sales": "10000_",
    }
    data.update(params)

    while p < 10 and actual_ps == wanted_ps:
        actual_ps = 0
        data["page"] = f"{p}"
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
            actual_ps += 1

        p += 1

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
        if entry[0] in companies:
            companies[entry[0]].set_data_1(*entry)

    params_2 = {
        "kgv": "-1000_",
        "kuv": "-1_",
        "kbv": "-1_"
    }
    converters_2 = [get_float, get_float, get_float]
    for entry in load_0(year, params=params_2, converters=converters_2):
        if entry[0] in companies:
            companies[entry[0]].set_data_2(*entry)

    return companies

def _load_cmp_pages(href):
    url = f"https://www.ariva.de/{href}-aktie/bilanz-guv?page=0"
    r = s.get(url)
    if r.status_code == 200:
        # f = open('./idx.html')
        #  text = f.read()
        root = etree.HTML(r.content.decode('utf-8'))
        select = root.xpath('//select[@name="page"]')
        if len(select) != 1:
            return None
        options = select[0].xpath('./option/text()')
        last_year = int(options[0].split('-')[-1])
        first_year = int(options[-1].split('-')[0])
        yield (last_year - 5, root)

        num_pages = min( int((last_year - first_year) / 6), 5)
        last_page = last_year - first_year - 5
        for i in range(num_pages):
            c_page = last_page - 6 * i
            print(f"c_page {c_page}")
            url = f"https://www.ariva.de/{href}-aktie/bilanz-guv?page={c_page}"
            r = s.get(url)
            if r.status_code == 200:
                yield (first_year + 6 * i, etree.HTML(r.content.decode('utf-8')))



def _get_multiplier(val):
    if val == 'Mio.':
        return 1e6
    print(f'unknown multiplier {val}')
    return 0

def _get_currency(currency):
    if currency == 'EUR':
        return 1
    elif currency == 'USD':
        return 0.876
    elif currency == 'CNY':
        return 0.1376
    elif currency == 'HKD':
        return 0.1124
    print(f'unknown currency {currency}')
    return 0

def collect_table(root, name):
    rows = root.xpath(f'//div[@class="{name}"]'
        '/div[@class="column twothirds table"]/table/tbody/tr')
    result = dict()
    for row in rows[1:]:
        if len(row.keys()) == 0:
            columns = row.xpath('./td/text()')
            if columns[0] == ' ':
                result[" ".join(columns[1].split())] = columns[2:]
            else:
                result[" ".join(columns[0].split())] = columns[1:]
    return result

def load_company_history(href):
    year_company_dict = dict()
    for year_off, page in _load_cmp_pages(href):
        print(year_off)
        top_div = page.xpath('//div[@class="tabelleUndDiagramm guv new abstand"]')
        if len(top_div) != 1:
            print('could not find valid guv div')
            continue
        title = top_div[0].xpath('./div[@class="arheadgl new "]/h3[@class="arhead undef"]/text()')
        if len(title) != 1:
            print('could not find valid title currency conversion')
            continue
        split_t = title[0].split()
        mult = _get_multiplier(split_t[2])
        curren = _get_currency( split_t[3])
        print(mult)
        print(curren)
        
        guv_dict = collect_table(page, "tabelleUndDiagramm guv new abstand")
        print(guv_dict)
        stock_dict = collect_table(page, "tabelleUndDiagramm aktie new abstand")
        personal_dict = collect_table(page, "tabelleUndDiagramm personal new abstand")
        eval_dict = collect_table(page, "tabelleUndDiagramm bewertung new abstand")

        for i in range(6):
            year = year_off + i
            mult_cur = mult * curren
            if 'Umsatz' in guv_dict and guv_dict['Umsatz'][i] != '- \xa0 ':
                try:
                    sales = int(mult_cur * get_float(guv_dict['Umsatz'][i]))
                    profit = int(mult_cur * get_float(guv_dict['Jahresüberschuss/-fehlbetrag'][i]))
                    aktiva = int(mult_cur * get_float(guv_dict['Summe Aktiva'][i]))
                    passiva = int(mult_cur * get_float(guv_dict['Summe Fremdkapital'][i]))
                    num_stocks = int(mult_cur * get_float(stock_dict['Mio. Aktien im Umlauf (splitbereinigt)'][i]))
                    year_entry = data.ext_company(href, sales=sales, profit_loss=profit, 
                        sum_assets=aktiva, sum_liabilities=passiva, number_of_shares=num_stocks)

                    eps = curren * get_float(stock_dict['Ergebnis je Aktie (unverwässert)'][i])
                    dps = curren * get_float(stock_dict['Dividende je Aktie'][i])
                    ne = get_val(personal_dict['Personal am Ende des Jahres'][i])
                    year_entry.set_data_1(href=href, sales=sales, earnings_per_share=eps,
                        dividend_per_share=dps, number_of_employees=ne)

                    # kgv = curren * get_float(eval_dict[' KGV (Kurs/Gewinn) '][i])
                    kuv = curren * get_float(eval_dict['KUV (Kurs/Umsatz)'][i])
                    # kbv = curren * get_float(eval_dict[' KBV (Kurs/Buchwert) '][i])
                    year_entry.set_data_2(href, sales, kgv=0, kuv=kuv, kbv=0)

                    year_company_dict[year] = year_entry
                except Exception as e:
                    print(f'error while parsing data >>>{e}<<<')
    return year_company_dict
