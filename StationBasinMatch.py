# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point





basins_path = "./data/hydrobasins/hybas_eu_lev10_v1c.shp"
stations_by_basin = "./data/stations_by_basin.csv"


 
DISCHARGE_CSV = "./data/grdc_discharge_monthly.csv"  
RWE_CSV = "./data/rwe_monthly_by_basin.csv"
x= 0





def cords_of_station(path):
    metadata = {'grdc_no': None,'station': None,'latitude': None,'longitude': None}

    with open(path, 'r', encoding='latin1') as f:
        for line in f:
            if 'GRDC-No.:' in line:
                metadata['grdc_no'] = line.split(':', 1)[1].strip()
            elif 'Station:' in line:
                metadata['station'] = line.split(':', 1)[1].strip()
            elif 'Latitude (DD):' in line:
                metadata['latitude'] = float(line.split(':', 1)[1].strip())
            elif 'Longitude (DD):' in line:
                metadata['longitude'] = float(line.split(':', 1)[1].strip())
            elif 'Flag' in line:
                break       
    return metadata

def match_station_to_basins(path):
    metadata = cords_of_station(path)
    basins = gpd.read_file(basins_path)
    basins = basins[["PFAF_ID", "geometry"]]
    basins = basins.set_crs("EPSG:4326")
    lat, lon = metadata['latitude'], metadata['longitude']
    point = Point(lon, lat)
    print(point)
    matched_basin = basins[basins.contains(point)]
    print(matched_basin)
    if not matched_basin.empty:
        pfaf_id = matched_basin['PFAF_ID'].values[0]
        print(matched_basin['PFAF_ID'].values[0])
        print({'grdc_no': metadata['grdc_no'], 'PFAF_ID': pfaf_id})
    else:
        nearest_idx = basins.geometry.distance(point).idxmin()   
        pfaf_id = basins.loc[nearest_idx, 'PFAF_ID']

    return {'grdc_no': metadata['grdc_no'], 'PFAF_ID': pfaf_id, 'Longitude': lon, 'Latitude': lat}

all_matches = []
for e in os.scandir(r"./data/grdc"):
    if e.is_file() and e.name.endswith('.txt'):
        print(e.name)
        result = match_station_to_basins("./data/grdc/" + str(e.name))
        if result is not None:
            all_matches.append(result)

print(all_matches)
df = pd.DataFrame(all_matches)
counts = (
    df.groupby("PFAF_ID")["grdc_no"]
      .count()
      .reset_index(name="num_grdc")
)

print(counts)
counts.to_csv("./data/pfaf_counts.csv", index=False)

if not df.empty:
    df[['grdc_no', 'PFAF_ID', "Longitude", "Latitude"]].drop_duplicates().to_csv("./data/stations_by_basin.csv", index=False)
    print("Matching finished")
else:
    print("No stations were successfully matched to any basins.")   
print(x)
    