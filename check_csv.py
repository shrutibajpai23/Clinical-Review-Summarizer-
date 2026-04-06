import pandas as pd

df = pd.read_csv('Data/mtsamples.csv')
print('COLUMNS:', df.columns.tolist())
print('SHAPE:', df.shape)
print()
print(df.head(2))