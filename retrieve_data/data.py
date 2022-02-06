class company:
    def __init__(self, href, name, isin=None):
        self.href  = href
        self.name  = name
        self.isin = isin
    def __hash__(self):
        return hash(self.href)
    def __repr__(self):
        return f"[{self.href} - {self.name} - {self.isin}]"

class ext_company:
    def __init__(self, href, sales, profit_loss, sum_assets, sum_liabilities, number_of_shares):
        self.href = href
        self.sales = sales
        self.profit_loss = profit_loss
        self.sum_assets = sum_assets
        self.sum_liabilities = sum_liabilities
        self.number_of_shares = number_of_shares
        self.data1 = False
        self.data2 = False

    def set_data_1(self, href, sales, earnings_per_share, dividend_per_share, number_of_employees):
        self.data1 = True
        self.earnings_per_share = earnings_per_share
        self.dividend_per_share = dividend_per_share
        self.number_of_employees = number_of_employees

    def set_data_2(self, href, sales, kgv, kuv, kbv):
        self.data2 = True
        self.kgv = kgv
        self.kuv = kuv
        self.kbv = kbv

    def __repr__(self):
        if self.data1:
            data1 = f"{self.earnings_per_share, self.dividend_per_share, self.number_of_employees}]"
        else:
            data1 = ""
        if self.data2:
            data2 = f"{self.kgv}, {self.kuv}, {self.kbv}"
        else:
            data2 = ""
        return (f"{self.href}: [{self.sales}, {self.profit_loss},"
            f" {self.sum_assets}, {self.sum_liabilities}, {self.number_of_shares}, {data1}, {data2}")
