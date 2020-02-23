# -*- coding: utf-8 -*-
"""CISC 372 given file.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1t7oUy9H4sXD6EyKcS9ddG9d6-hROoo4W
"""

# download data (-q is the quiet mode)
! wget -q https://www.dropbox.com/s/lhb1awpi769bfdr/test.csv?dl=1 -O test.csv
! wget -q https://www.dropbox.com/s/gudb5eunj700s7j/train.csv?dl=1 -O train.csv

# downloading the data as testing and training data sets

import pandas as pd
# imports a module / library called panda and name is as pd in the following code

Xy_train = pd.read_csv('train.csv', engine='python')
# read the train.csv file to get comma-seperated values using python
X_train = Xy_train.drop(columns=['price_rating'])
# drop the column "price-rating" since it is the class label
y_train = Xy_train[['price_rating']]
# put the value in variable "y_train"

print('traning', len(X_train))
Xy_train.price_rating.hist()
# get a histogram by price_rating values for the training data

X_test = pd.read_csv('test.csv', engine='python')
testing_ids = X_test.Id
print('testing', len(X_test))
# get testing values

# model training and tuning
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.datasets import fetch_openml
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
from xgboost.sklearn import XGBClassifier

np.random.seed(0)
# make the random numbers predictable

numeric_features = ['bedrooms', 'review_scores_location', 'accommodates', 'beds']
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())])
# selects numeric features to be considered in the XGBclassifier
categorical_features = [
  'property_type', 'is_business_travel_ready', 'room_type', ]
categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))])
# transforms the original value to evlauable values by computer
# including the strategy of dealing with missing values (preprocessing)

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)])

regr = Pipeline(steps=[('preprocessor', preprocessor),
                      ('regressor', XGBClassifier(
                          objective='multi:softmax', seed=1))])
# concatenates the columns and respective transformer into one transformer as preprocessor
# prepare to do a regression prediction by XGB classifier, name it by regressor

X_train = X_train[[*numeric_features, *categorical_features]]
X_test = X_test[[*numeric_features, *categorical_features]]

# `__` denotes attribute 
# (e.g. regressor__n_estimators means the `n_estimators` param for `regressor`
#  which is our xgb)
param_grid = {
    'preprocessor__num__imputer__strategy': ['mean'],
    'regressor__n_estimators': [50, 100],
    'regressor__max_depth':[10, 20]
}

# configures the XGBclassifier, number of trees, max depth...

grid_search = GridSearchCV(
    regr, param_grid, cv=10, verbose=3, n_jobs=2, 
    scoring='accuracy')
grid_search.fit(X_train, y_train)
# configures the grid_search_cross_validation settings
print('best score {}'.format(grid_search.best_score_))
# prints out the best score found by grid_search

# Prediction & generating the submission file
y_pred = grid_search.predict(X_test)
pd.DataFrame({'Id': testing_ids, 'price_rating':y_pred}).to_csv('sample_submission.csv', index=False)

# constructs the sample_submission.csv