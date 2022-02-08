import sqlite_connector as sc
import numpy as np

class data_loader:
    def __init__(self, yearS = 2016, yearE = 2021):
        self.conn = sc.get_db('../')
        self.yearS = yearS
        self.hrefs = sc.load_hrefs(self.conn)
        self.year_data = []
        for year in range(yearS, yearE + 1):
            self.year_data.append(sc.load_year_data(self.conn, year, self.hrefs))

    def PER(self, year):
        d = self.year_data[year - self.yearS]
        ret = np.zeros(len(d))
        idxs = d[:,sc.INCOME] != 0
        ret[idxs] = d[idxs,sc.MARKET_CAP] / d[idxs, sc.INCOME]
        return ret

    def PER_H(self, year, yearS):
        if yearS < self.yearS:
            return None
        d = self.year_data[year - yearS]
        income = np.zeros(len(d))
        for i in range(yearS - self.yearS, year - self.yearS + 1):
            income += self.year_data[i][:, sc.INCOME]
        idxs = income != 0
        return (year - yearS + 1) * (d[idxs, sc.MARKET_CAP] / income[idxs])

    def PRR(self, year):
        d = self.year_data[year - self.yearS]
        ret = np.zeros(len(d))
        idxs = d[:,sc.RETURN] != 0
        ret[idxs] = d[idxs,sc.MARKET_CAP] / d[idxs, sc.RETURN]
        return ret

    def PBR(self, year):
        d = self.year_data[year - self.yearS]
        ret = d[:,sc.AKTIVA] - d[:,sc.PASSIVA]
        idxs = ret != 0
        ret[idxs] = d[idxs,sc.MARKET_CAP] / ret[idxs]
        return ret

    def DIV_Y(self, year):
        d = self.year_data[year - self.yearS]
        ret = np.copy(d[:, sc.MARKET_CAP])
        idxs = ret != 0
        ret[idxs] = d[idxs,sc.DIVIDENDS] / ret[idxs]
        return ret

    def ACT_Y(self, year):
        d = self.year_data[year - self.yearS]
        ret = d[:,sc.AKTIVA] - d[:,sc.PASSIVA]
        idxs = ret != 0
        ret[idxs] = d[idxs,sc.INCOME] / ret[idxs]
        return ret

    def RET_Y(self, year):
        d = self.year_data[year - self.yearS]
        ret = np.copy(d[:,sc.RETURN])
        idxs = ret != 0
        ret[idxs] = d[idxs,sc.INCOME] / ret[idxs]
        return ret

    def CAP_Y(self, year):
        d = self.year_data[year - self.yearS]
        ret = np.copy(d[:,sc.AKTIVA])
        idxs = ret != 0
        ret[idxs] = d[idxs,sc.INCOME] / ret[idxs]
        return ret

    def DEBT(self, year):
        d = self.year_data[year - self.yearS]
        ret = np.copy(d[:,sc.AKTIVA])
        idxs = ret != 0
        ret[idxs] = d[idxs,sc.PASSIVA] / ret[idxs]
        return ret

    def RET_PE(self, year):
        d = self.year_data[year - self.yearS]
        ret = np.copy(d[:,sc.EMPLOYEES])
        idxs = ret != 0
        ret[idxs] = d[idxs,sc.RETURN] / ret[idxs]
        return ret

    def INC_PE(self, year):
        d = self.year_data[year - self.yearS]
        ret = np.copy(d[:,sc.EMPLOYEES])
        idxs = ret != 0
        ret[idxs] = d[idxs,sc.INCOME] / ret[idxs]
        return ret

    def YR_change(self, year, years=1):
        off = year - self.yearS
        d = self.year_data[off][:, sc.MARKET_CAP]
        idxs = d != 0
        divs = np.zeros(len(d))
        for i in range(off + 1, off + years + 1):
            divs[idxs] += self.year_data[i][idxs, sc.DIVIDENDS]
        divs = (self.year_data[off + years][idxs, sc.MARKET_CAP] + divs[idxs]) / d[idxs]
        return divs


