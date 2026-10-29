# -*- coding: utf-8 -*-
import rasterio
import geopandas as gpd
import pandas as pd
import numpy as np
from rasterio.windows import from_bounds
from rasterstats import zonal_stats
 
basins = gpd.read_file("data/hydrobasins/hybas_eu_lev10_v1c.shp")
stations_by_basin = "./data/stations_by_basin.csv"
lcm = "./data/landcover/LCM2000_GB_25m.tif"   
 
df = pd.read_csv(stations_by_basin)
pfaf_list = df['PFAF_ID'].tolist()
 
with rasterio.open(lcm) as src:
    basins = basins.to_crs(src.crs)
    lcm_nodata = src.nodata
 
basins = basins[basins["PFAF_ID"].isin(pfaf_list)].copy()
 
CLASS_NAMES = {
    0: "Unclassified",
    11: "Broad-leaved/mixed woodland",
    21: "Coniferous woodland",
    41: "Arable cereals",
    42: "Arable horticulture",
    43: "Arable non-rotational",
    51: "Improved grassland",
    52: "Setaside grassland",
    61: "Neutral grassland",
    71: "Calcareous grassland",
    81: "Acid grassland",
    91: "Bracken",
    101: "Dense dwarf shrub heath",
    102: "Open dwarf shrub heath",
    111: "Fen, marsh, swamp",
    121: "Bog (deep peat)",
    131: "Water (inland)",
    151: "Montane habitats",
    161: "Inland bare ground",
    171: "Suburband/rural developed",
    172: "Continuous urban",
    181: "Supra-littoral rock",
    191: "Supra-littoral sediment",
    201: "Littoral rock",
    211: "Littoral sediment",
    212: "Saltmarsh",
    221: "Sea/Estuary",
    
}
 
records = []
 
with rasterio.open(lcm) as src:
    buf = src.res[0]
    for _, row in basins.iterrows():
        geom = row.geometry
        minx, miny, maxx, maxy = geom.bounds
        window = from_bounds(minx - buf, miny - buf, maxx + buf, maxy + buf, transform=src.transform)
 
        band = src.read(1, window=window)
        transform = src.window_transform(window)
 
        result = zonal_stats(
            [geom], band, affine=transform, nodata=lcm_nodata,
            categorical=True,
        )[0]
        print(result)
 
        total_px = sum(result.values())
        pct_row = {"PFAF_ID": row["PFAF_ID"]}
        total = 0
        for num in CLASS_NAMES:
            name = CLASS_NAMES.get(num)
            print(num)
            print(CLASS_NAMES.values())
            count = result.get(num, 0)
            print(count)
            pct_row[f"pct_{name}"] = 100 * count / total_px if total_px else np.nan
            total = total + pct_row[f"pct_{name}"]
        pct_row["total"] = total
        records.append(pct_row)
 
landcover_df = pd.DataFrame(records)
print(landcover_df)
 
landcover_df.to_csv("./data/landcover_predictors.csv", index=False)
print("done")