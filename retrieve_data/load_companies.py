import requests
from lxml import etree

def load_wiki_html():
    ret = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    if ret.status_code == 200:
        return ret.content
    return ''

class company:
    def __init__(self, symbol, cik, year_added, year_removed = -1):
        self.symbol  = symbol
        self.cik  = cik
        self.year_added = year_added
        self.year_removed = year_removed

    def __eq__(self, other):
        return self.symbol == other.symbol

    def __hash__(self):
        return hash(self.symbol)

    def __repr__(self):
        return f"[{self.symbol} - {self.cik} - {self.year_added}]"


def select_list(html_string):
    root = etree.HTML(html_string)

    constituents = root.xpath('//table[@id="constituents"]')[0]
    rows_consts = constituents.xpath('./tbody/tr')
    companies = dict()
    for rows in rows_consts:
        cols = rows.xpath('./td')
        if len(cols) >= 8:
            symbol = cols[0].xpath('./a')[0].text.strip()
            year_entry = cols[6].text
            if year_entry is None or len(year_entry) < 4:
                year_added = 1957
            else:
                year_added = int(year_entry[:4])
            cik = cols[7].text.strip()
            companies[symbol] = company(symbol, cik, year_added)


    changes = root.xpath('//table[@id="changes"]')[0]
    rows_change = changes.xpath('./tbody/tr')
    for change in rows_change:
        cols = change.xpath('./td')
        if len(cols) >= 6:
            date = int(cols[0].text.strip()[-4:])
            if cols[1].text is not None:
                symbol_add = cols[1].text.strip()
                if symbol_add in companies:
                    companies[symbol_add].year_added = date
            if cols[3].text is not None:
                symbol_remove = cols[3].text.strip()
                if symbol_remove not in companies:
                    companies[symbol_remove] = company(symbol_remove, None, None, date)
                else:
                    print(f"remove was in {symbol_remove}")
    
    for c in companies.values():
        if c.year_added is None:
            c.year_added = 1957

    return companies

wiki_page = load_wiki_html()
companies = select_list(wiki_page)
print(len(companies))
print(companies)