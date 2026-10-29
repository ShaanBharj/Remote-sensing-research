# -*- coding: utf-8 -*-



import os
import pandas as pd

def get_rwe(year, month, pfaf_id):
    result = df_RWE.loc[
        (df_RWE["YEAR"] == year) &
        (df_RWE["MONTH"] == month) &
        (df_RWE["PFAF_ID"] == pfaf_id),
        "RWE"
    ]

    if result.empty or pd.isna(result.iloc[0]) :
        return None
    return result.iloc[0]


def FilterMatching(path):
    
    df = pd.read_csv(path)
    x = 0
    temp_results = []
    all_results = []
    for i in range(len(df.index)):
        metadata = {'GRDC_NO': None,'YEAR': None,'MONTH': None,'PFAF_ID': None, 'Discharge': None, 'RWE': None}
        row = df.iloc[i]
        year = row[1]
        metadata['YEAR'] = year
        month = row[2]
        metadata['MONTH'] = month
        PFAF_ID = row[4]
        metadata['PFAF_ID'] = PFAF_ID
        metadata['Discharge'] = row[3]
        metadata['GRDC_NO'] = row[0]
        metadata['RWE'] = get_rwe(year,month, PFAF_ID)
        print(metadata['RWE'])
        if (pd.isna(metadata['RWE']) == False and float(metadata['RWE']) > 0):
            temp_results.append(metadata)
            x = x +1
    if x > 2:
        all_results = temp_results

    return all_results
    

df_RWE = df = pd.read_csv(r"./data/MonthlyWE_by_PFAF.csv")
for e in os.scandir(r"./data/MonthlyDischarge"):
    all_results = []
    if e.is_file():
        all_results = FilterMatching("./data/MonthlyDischarge/" + str(e.name))
    df_results = pd.DataFrame(all_results)
    if not df_results.empty:
        df_results[['GRDC_NO', 'YEAR','MONTH','PFAF_ID','Discharge', 'RWE']].drop_duplicates().to_csv("./data/FinalData/" + str(e.name[:7]) + ".csv", index=False)
        print("Matching finished")
    else:
        print("No stations were successfully matched discharge")  