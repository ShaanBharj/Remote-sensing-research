# -*- coding: utf-8 -*-


import os
import pandas as pd


stations_by_basin = "./data/stations_by_basin.csv"
df_read = pd.read_csv(stations_by_basin)
lookup = dict(zip(df_read["grdc_no"], df_read["PFAF_ID"]))


def getGRDCData(path, name):
    name = int(name[:7])
    PFAF_ID = lookup[name]
    
    df = pd.read_csv(
    path,
    sep=";",
    comment="#",
    skipinitialspace=True,
    encoding="latin-1"
    )
    df["YYYY-MM-DD"] = pd.to_datetime(df["YYYY-MM-DD"])

    df = df[
        (df["YYYY-MM-DD"] >= "1984-03-01") &
        (df["YYYY-MM-DD"] <= "2021-12-31")
    ]
    for i in range(1,len(df.index)):
        metadata = {'grdc_no': None,'year': None,'month': None,'discharge': None, 'PFAF_ID': None}
        row = df.iloc[i-1]
        date = row["YYYY-MM-DD"]
        metadata['year'] = date.year
        metadata['month'] = date.month
        metadata['discharge'] = row["Calculated"]
        metadata['grdc_no'] = name
        metadata['PFAF_ID'] = PFAF_ID
        if metadata['discharge'] > 0:
            all_results.append(metadata)
    print(df)
    
            
            
            
    return None
    

for e in os.scandir(r"./data/grdc"):
    all_results = []
    if e.is_file() and e.name.endswith('.txt'):
        getGRDCData("./data/grdc/" + str(e.name), str(e.name))
    df_results = pd.DataFrame(all_results)
    if not df_results.empty:
        df_results[['grdc_no', 'year','month','discharge','PFAF_ID']].drop_duplicates().to_csv("./data/MonthlyDischarge/" + str(e.name[:7]) + ".csv", index=False)
        print("Matching finished")

