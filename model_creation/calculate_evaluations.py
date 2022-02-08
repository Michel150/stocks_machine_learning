import sqlite_connector as sc
import numpy as np

FEATURE_NAMES = [
    "PER",
    "PER_H",
    "PRR",
    "PBR",
    "DIV_Y",
    "ACT_Y",
    "RET_Y",
    "CAP_Y",
    "DEBT",
    "INC_PE",
    "RET_PE",
    "YR_change",
    "RET_change"
]

def _get_valid_idxs(X, y):
    tmp = np.ones(len(X))
    for i in range(X.shape[1]):
        tmp *= X[:, i]
    tmp *= y
    return tmp != 0

class data_loader:
    def __init__(self, yearS = 2016, yearE = 2021):
        self.conn = sc.get_db('../')
        self.yearS = yearS
        self.yearE = yearE
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
        income[idxs] = (year - yearS + 1) * (d[idxs, sc.MARKET_CAP] / income[idxs])
        return income

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
        divs[idxs] = (self.year_data[off + years][idxs, sc.MARKET_CAP] + divs[idxs]) / d[idxs]
        return divs

    def RET_change(self, year, years=1):
        d = self.year_data[year - self.yearS][:, sc.RETURN]
        idxs = d != 0
        change = np.zeros(len(d))
        change[idxs] = self.year_data[year + years - self.yearS][idxs, sc.RETURN] / d[idxs]
        return change


    def create_dataset(self, year, past=1, future=2):
        if (year - past) < self.yearS or (year + future) > self.yearE:
            print("invalid time interval with insufficent date selected")
            return None
        N = len(self.year_data[0])
        X = np.empty((N, 13))
        X[:,  0] = self.PER(year)
        X[:,  1] = self.PER_H(year,year - past)
        X[:,  2] = self.PRR(year)
        X[:,  3] = self.PBR(year)
        X[:,  4] = self.DIV_Y(year)
        X[:,  5] = self.ACT_Y(year)
        X[:,  6] = self.RET_Y(year)
        X[:,  7] = self.CAP_Y(year)
        X[:,  8] = self.DEBT(year)
        X[:,  9] = self.INC_PE(year)
        X[:, 10] = self.RET_PE(year)
        X[:, 11] = self.YR_change(year - past, years=past)
        X[:, 12] = self.RET_change(year - past, years=past)

        y = self.RET_change(year, years=future)

        idxs = _get_valid_idxs(X, y)

        hrefs_s = []
        for i, valid in enumerate(idxs):
            if valid:
                hrefs_s.append(self.hrefs[i])

        return hrefs_s, X[idxs],y[idxs]

    def create_datasets(self, yearS, yearE, past=1, future=2):
        hrefs = []
        X = np.empty((0,13))
        y = np.empty((0))
        for year in range(yearS, yearE + 1):
            hrefs_t, X_t, y_t = self.create_dataset(year, past=1, future=2)

            hrefs += hrefs_t
            X = np.vstack((X, X_t))
            y = np.hstack((y, y_t))
            print(X.shape)
            print(y.shape)
        return hrefs, X, y
