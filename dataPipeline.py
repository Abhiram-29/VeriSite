#!/usr/bin/env python
# coding: utf-8

# In[11]:


from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
import numpy as np
import pandas as pd
import joblib
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split


# <h1> Retraining the model and integrating it into a pipeline for easy deployment</h1>

# In[80]:


goodFeat = pd.read_csv("good_website_featues18000.csv")
badFeat = pd.read_csv("bad_website_features15000.csv")
badFeat['TargetScore'] = 0
goodFeat['TargetScore'] = 1
X = pd.concat([badFeat,goodFeat],ignore_index=True)
X = X.sample(frac=1).reset_index(drop = True)
y = X['TargetScore']


# In[55]:


X.head()


# In[81]:


X.drop(['Unnamed: 0','URL','TargetScore','isShort','hasIP','hasEmail','misleadingChars','//present','@present'],axis=1,inplace=True)


# In[82]:


X_train,X_test,y_train,y_test = train_test_split(X,y)


# In[84]:


from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OrdinalEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import pandas as pd
import numpy as np

# Custom transformer to fill missing values
class FillMissingValues(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.sslMean = 95.42572488662911 # SSL age mean from the training dataset
        self.domainAgeMean = 4768.3417287504235 # Domain Age mean from the training dataset

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

# Custom transformer for domain extraction
class ExtractDomain(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        X['domain'] = X['domain'].apply(lambda url: url.split('.')[-1] if len(url.split('.')) > 2 else 'None')
        return X

# Custom transformer to encode categorical features using the fitted OrdinalEncoder
class OrdinalEncoderWrapper(BaseEstimator, TransformerMixin):
    def __init__(self, encoded_columns):
        self.encoded_columns = encoded_columns
        self.encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)  # Create a new encoder instance

    def fit(self, X, y=None):
        self.encoder.fit(X[self.encoded_columns])  # Fit the encoder on specific columns
        return self

    def transform(self, X):
        X = X.copy()
        X[self.encoded_columns] = self.encoder.transform(X[self.encoded_columns])  # Transform specific columns
        return X

# Define the columns to be preprocessed
encoded_columns = ['registrar', 'domain', 'protocol']

# Preprocessing pipeline
preprocessing_pipeline = Pipeline(steps=[
    ('fill_missing', FillMissingValues()),
    ('extract_domain', ExtractDomain()),
    ('encode', OrdinalEncoderWrapper(encoded_columns=encoded_columns))
])




# In[85]:


preprocessing_pipeline.fit(X_train)


# In[69]:


X_train = preprocessing_pipeline.transform(X_train)


# <h1>Using Isolation forest to remove outliers from the training data</h1>

# In[70]:


# Outlier detection using IQR
from sklearn.ensemble import IsolationForest
X_train_IF = X_train.copy()
model = IsolationForest() 
model.fit(X_train_IF)


# In[71]:


scores=model.decision_function(X_train_IF)
anomaly=model.predict(X_train_IF)

X_train_IF['scores']=scores
X_train_IF['anomaly']=anomaly

anomaly = X_train_IF.loc[X_train_IF['anomaly']==-1]
anomaly_index = list(anomaly.index)
print('Total number of outliers is:', len(anomaly))


# In[72]:


X_train = X_train_IF.drop(anomaly_index, axis = 0).reset_index(drop=True)
y_train = y_train.drop(anomaly_index,axis = 0).reset_index(drop=True)


# In[73]:


X_train.drop(['scores','anomaly'],axis=1,inplace=True)
X_train.head()


# In[74]:


X_train.to_csv("X_train.csv")
y_train.to_csv("y_train.csv")


# In[75]:


xgb = joblib.load("./XGBModel.pkl")


# In[87]:


# Full pipeline including the pre-trained model (assuming xgb is defined)
full_pipeline = Pipeline(steps=[
    ('preprocessing', preprocessing_pipeline),
    ('model', xgb)
])
# Save the complete pipeline to a file
joblib.dump(full_pipeline, 'full_model_pipeline.pkl')


# In[88]:


predictions = full_pipeline.pre(X_test)


# In[91]:


from sklearn.metrics import accuracy_score
accuracy_score(predictions,y_test)


# In[90]:


# Load and use the complete pipeline for predictions
loaded_pipeline = joblib.load('full_model_pipeline.pkl')
predictions = loaded_pipeline.predict(X_test)


# In[ ]:




