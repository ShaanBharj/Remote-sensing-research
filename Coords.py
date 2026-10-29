    # -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 16:42:26 2026

@author: shaan
"""
import pandas as pd

df_stations = pd.read_csv("./data/stations_by_basin.csv")
df_lin = pd.read_csv("./data/Linear.csv")
Lin = df_lin["path"].unique().tolist()
df_quad = pd.read_csv("./data/Quadratic.csv")
Quad = df_quad["path"].unique().tolist()
df_ins = pd.read_csv("./data/Insignificant.csv")
Ins = df_ins["path"].unique().tolist()
print(Lin)
NewLin = []
NewQuad = []
NewIns = []

for index, row in df_stations.iterrows():
    if row["grdc_no"] in Lin:
        NewLin.append(row)
    if row["grdc_no"] in Quad:
        NewQuad.append(row)
    if row["grdc_no"] in Ins:
        NewIns.append(row)
      
df = pd.DataFrame(NewLin)
df.drop_duplicates().to_csv("./data/Linear.csv",index=False)
df = pd.DataFrame(NewQuad)
df.drop_duplicates().to_csv("./data/Quadratic.csv",index=False)
df = pd.DataFrame(NewIns)
df.drop_duplicates().to_csv("./data/Insignificant.csv",index=False)
        
        