class Storage :

    def __init__(self, df):
        self.df = df

    def update(self, df):
        self.df = df

    def get(self):
        return self.df