# -*- coding: utf-8 -*-

import pandas as pd



df_lin = pd.read_csv("./data/Linear.csv")
df_lin["Sig"] = 1

df_quad = pd.read_csv("./data/Quadratic.csv")
df_quad["Sig"] = 1

df_ins = pd.read_csv("./data/Insignificant.csv")
df_ins["Sig"] = 0

dem = pd.read_csv("./data/terrain_predictors.csv")
dem = dem.drop(["HYBAS_ID",	"NEXT_DOWN",	"NEXT_SINK",	"MAIN_BAS",	"DIST_SINK",	"DIST_MAIN",	"SUB_AREA",	"UP_AREA",	"ENDO",	"COAST",	"ORDER",	"SORT"],axis = "columns")
print(dem)

landcover = pd.read_csv("./data/landcover_predictors.csv")
landcover["pct_Littoral rock and sediment"] = landcover["pct_Littoral rock"] + landcover["pct_Littoral sediment"] + landcover["pct_Saltmarsh"]
landcover["pct_Supralittoral rock and sediment"] = landcover["pct_Supra-littoral rock"] + landcover["pct_Supra-littoral sediment"]
landcover["pct_Dwarf shrub heath"] = landcover["pct_Dense dwarf shrub heath"] + landcover["pct_Open dwarf shrub heath"]
landcover["pct_Arable and horticultural"] = landcover["pct_Arable cereals"] + landcover["pct_Arable horticulture"] + landcover["pct_Arable non-rotational"]
landcover["pct_Grassland"] = landcover["pct_Setaside grassland"] + landcover["pct_Neutral grassland"] + landcover["pct_Calcareous grassland"]
landcover["pct_Acid grass and bracken"] = landcover["pct_Acid grassland"] + landcover["pct_Bracken"]
landcover["pct_Suburban and urban"] = landcover["pct_Suburband/rural developed"] + landcover["pct_Continuous urban"]
landcover = landcover.drop(["pct_Unclassified","total","pct_Littoral rock","pct_Littoral sediment", "pct_Saltmarsh","pct_Supra-littoral rock", "pct_Supra-littoral sediment", "pct_Dense dwarf shrub heath", "pct_Open dwarf shrub heath","pct_Arable cereals","pct_Arable horticulture", "pct_Arable non-rotational", "pct_Setaside grassland", "pct_Neutral grassland", "pct_Calcareous grassland","pct_Acid grassland", "pct_Bracken", "pct_Suburband/rural developed", "pct_Continuous urban"],axis="columns")
print(landcover)

res = pd.concat([df_lin, df_quad,df_ins], axis=0, ignore_index=True)
res = res.drop(["Longitude", "Latitude"],axis = "columns")
print(res)

df = pd.merge(res, dem, on="PFAF_ID")
df = pd.merge(df,landcover, on="PFAF_ID")
for i, row in df.iterrows():
    grdc = str(row["grdc_no"])
    grdc = grdc[:7]
    print(grdc)
    lines = pd.read_csv("./data/FinalData/" + grdc + ".csv")
    linenum = len(lines)
    print(linenum)
    df.at[i, "Months"] = linenum


df = df.astype(float)
print(df)

df.to_csv("./data/RegressionData.csv", index=False)