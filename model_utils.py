# model_utils.py
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OrdinalEncoder

class FillMissingValues(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.sslMean = 95.42572488662911
        self.domainAgeMean = 4768.3417287504235

    def fit(self, X, y=None):
        self.sslMean = X['sslAge'].mean() if 'sslAge' in X else self.sslMean
        self.domainAgeMean = X['domainAge'].mean() if 'domainAge' in X else self.domainAgeMean
        return self

    def transform(self, X):
        X = X.copy()
        X['PageRank'].fillna(10000000, inplace=True)
        X['registrar'].fillna("", inplace=True)
        X['sslAge'].fillna(self.sslMean, inplace=True)
        X['domainAge'].fillna(self.domainAgeMean, inplace=True)
        X['domain'].fillna("", inplace=True)
        return X

class ExtractDomain(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        X['domain'] = X['domain'].apply(lambda url: url.split('.')[-1] if len(url.split('.')) > 2 else 'None')
        return X

class OrdinalEncoderWrapper(BaseEstimator, TransformerMixin):
    def __init__(self, encoded_columns):
        self.encoded_columns = encoded_columns
        self.encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)

    def fit(self, X, y=None):
        self.encoder.fit(X[self.encoded_columns])
        return self

    def transform(self, X):
        X = X.copy()
        X[self.encoded_columns] = self.encoder.transform(X[self.encoded_columns])
        return X
