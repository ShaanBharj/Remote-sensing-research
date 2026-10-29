# -*- coding: utf-8 -*-

import ee
import pandas as pd
import geopandas as gpd
import geemap

print("1")

basins_path = "./data/hydrobasins/hybas_eu_lev10_v1c.shp"
RWE_CSV = "./data/rwe_monthly_by_basin.csv"
stations_by_basin = "./data/stations_by_basin.csv"

START_MONTH = "1984-03"
END_MONTH = "2021-12"

ee.Authenticate()
ee.Initialize(project='model-obelisk-502714-r8')
print("2")
#basins_gdf = gpd.read_file(basins_path)
#basins_gdf = basins_gdf.to_crs(4326)
#basins_gdf = basins_gdf[["PFAF_ID", "geometry"]]

print("3")
#basin_fc = geemap.geopandas_to_ee(basins_gdf[["PFAF_ID", "geometry"]])


df = pd.read_csv(stations_by_basin)
pfafs = df["PFAF_ID"].unique().tolist()

basins_gdf = gpd.read_file(basins_path)
basins_gdf = basins_gdf.to_crs(4326)

# Keep only the basins you need
basins_gdf = basins_gdf[
    basins_gdf["PFAF_ID"].isin(pfafs)
][["PFAF_ID", "geometry"]]

basin_fc = geemap.geopandas_to_ee(basins_gdf)
target_basins = basin_fc
print(len(basins_gdf))

GSW = ee.Image("JRC/GSW1_1/GlobalSurfaceWater")

max_extent = GSW.select("max_extent")

def MWE(feature):

        
    basin_geometry = feature.geometry()
    
    water_pixels_img = max_extent.gt(0)

    stats = water_pixels_img.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=basin_geometry,
        scale=30,
        maxPixels=1e13
    )

    max_water_m2 = ee.Number(stats.get("max_extent")).multiply(900)
    print("hi")
    return feature.set('water_area_km2', max_water_m2)

gsw_monthly = ee.ImageCollection("JRC/GSW1_4/MonthlyHistory")
water = gsw_monthly.select("water")

def WE(feature):
    basin_geometry = feature.geometry()
    
    counts = ee.Image.cat([
    img.eq(0).rename("NA"),
    img.eq(1).rename("land"),
    img.eq(2).rename("water")
    ])

    stats = counts.reduceRegion(
    reducer=ee.Reducer.sum(),
    geometry=basin_geometry,
    scale=30,
    maxPixels=1e13
    )

    NA_pixels = ee.Number(stats.get("NA"))
    land_pixels = ee.Number(stats.get("land"))


    water_pixels = ee.Number(stats.get("water"))
    
    
        
    #valid_pixels = img.gt(0).rename("total").reduceRegion(
    #reducer=ee.Reducer.sum(),
    #geometry=basin_geometry,
    #scale=30,
    #maxPixels=1e13
    #).get("total")
    
    #water_area = img.eq(2).rename("total").reduceRegion(
    #reducer=ee.Reducer.sum(),
    #geometry=basin_geometry,
    #scale=30,
    #maxPixels=1e13
    #).get("total")
    
    
    water_area = water_pixels.multiply(900)
    monthly_extent = water_area
    basin_total_pixels = ee.Number(NA_pixels).add(land_pixels).add(water_pixels)
    #monthly_extent = monthly_extent.divide(1e6)
    return feature.set({
    #'debug' : monthly,
    'Monthly_extent': monthly_extent,
    'water_area': water_area,
    'valid_pixels': ee.Number(land_pixels).add(water_pixels),
    'basin_total_pixels': basin_total_pixels,
    });




    
processed_fc = target_basins.map(MWE)

firstresults = processed_fc.select(["PFAF_ID", "water_area_km2"]).getInfo()

MWE = []

for feat in firstresults['features']:
    props = feat['properties']
    MWE.append({'PFAF_ID': props.get('PFAF_ID'), 'MWE': props.get('water_area_km2')})
    print(f"PFAF_ID: {props.get('PFAF_ID')}, MWE: {props.get('water_area_km2')}")

df = pd.DataFrame(MWE)
df[['PFAF_ID', 'MWE']].drop_duplicates().to_csv("./data/MaxWE_by_PFAF.csv", index=False)
print("MAXWE calculated and exported")
mwe_lookup = {item['PFAF_ID']: item['MWE'] for item in MWE}
months = pd.date_range(start=START_MONTH,end=END_MONTH,freq="ME")
i=0
for dt in months:
    i = i+1
    year = dt.year
    month = dt.month
    img = (
    gsw_monthly
    .filter(ee.Filter.calendarRange(year, year, "year"))
    .filter(ee.Filter.calendarRange(month, month, "month"))
    .first()
    ).select('water')


    MonthlyWE_fc = target_basins.map(WE)
    print(MonthlyWE_fc.first().getInfo())
    secondresults = MonthlyWE_fc.select(["year","month", "PFAF_ID","Monthly_extent","water_area","valid_pixels","basin_total_pixels"]).getInfo()

    MonthWE = []
    for res in secondresults['features']:
        props = res['properties']
        mwe_value = mwe_lookup.get(props.get('PFAF_ID'))
        print(mwe_value)
        if mwe_value != 0:
            RWE = props.get("Monthly_extent")/mwe_value
            print(RWE)
        else:
            RWE = None
            
        MonthWE.append({'YEAR': year, 'MONTH': month,'PFAF_ID': props.get('PFAF_ID'), "MonthlyWE": props.get('Monthly_extent'), "RWE":RWE,"water_pixels": props.get("water_area"),
                "valid_pixels": props.get("valid_pixels"), "basin_total_pixels": props.get("basin_total_pixels")})
        #print(props.get)
    df = pd.DataFrame(MonthWE)
    df['valid_pixels'] = pd.to_numeric(df['valid_pixels'], errors='coerce').fillna(0)
    df['basin_total_pixels'] = pd.to_numeric(df['basin_total_pixels'], errors='coerce').fillna(1)  
    print(df["basin_total_pixels"])
    print(df["valid_pixels"])
    #df["basin_total_pixels"] = df.groupby("PFAF_ID")["valid_pixels"].transform("max")
    df["pct_missing"] = 1 - (df["valid_pixels"] / df["basin_total_pixels"])
    print(df["pct_missing"])
    df = df[df["pct_missing"] <= 0.1].copy()
    print(df)
    if year == 1984 and month == 3:
            df[['YEAR', 'MONTH','PFAF_ID', 'MonthlyWE', 'RWE']].drop_duplicates().to_csv("./data/MonthlyWE_by_PFAF.csv", index=False)
    else:           
        df[['YEAR', 'MONTH','PFAF_ID', 'MonthlyWE', 'RWE']].drop_duplicates().to_csv("./data/MonthlyWE_by_PFAF.csv", mode='a', index=False, header=False)
    print(i)


print("MONTHLYWE calculated and exported")
