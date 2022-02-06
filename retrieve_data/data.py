class company:
    def __init__(self, href, name, isin=None):
        self.href  = href
        self.name  = name
        self.isin = isin
    def __hash__(self):
        return hash(self.href)
    def __repr__(self):
        return f"[{self.href} - {self.name} - {self.isin}]"