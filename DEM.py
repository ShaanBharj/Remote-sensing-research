import rasterio
from rasterio.windows import from_bounds
import geopandas as gpd
import pandas as pd
import numpy as np
from rasterstats import zonal_stats

 
basins = gpd.read_file("data/hydrobasins/hybas_eu_lev10_v1c.shp")
stations_by_basin = "./data/stations_by_basin.csv"
dem = "./data/DEM/GB_DEM_27700.tif"
 
df = pd.read_csv(stations_by_basin)
print(df)
 
pfaf_list = df['PFAF_ID'].tolist()
 
with rasterio.open(dem) as src:
    basins = basins.to_crs(src.crs)
    dem_crs = src.crs
    print(src.name)
    print(src.crs)
    print(src.bounds)
    print(src.res)
 
basins = basins[basins["PFAF_ID"].isin(pfaf_list)].copy()
print(len(basins))
 
basins_area = basins.to_crs(3035)
basins["Area_km2"] = basins_area.area / 1e6
print(basins)
 

 

stats = zonal_stats(
    basins,
    dem,
    stats=["mean", "min", "max"]
)
basins["MeanElevation"] = [s["mean"] for s in stats]
basins["AltRange"] = [
    (s["max"] - s["min"]) if (s["max"] is not None and s["min"] is not None) else np.nan
    for s in stats
]
 

if not dem_crs.is_projected:
    raise ValueError(
        f"DEM CRS is {dem_crs}, which is geographic — slope would be wrong. "
        "Reproject GB_DEM.tif to a metres-based CRS (e.g. EPSG:27700) first."
    )
 

mean_slopes = []
 
with rasterio.open(dem) as src:
    buf = src.res[0]  
    for geom in basins.geometry:
        minx, miny, maxx, maxy = geom.bounds
        window = from_bounds(minx - buf, miny - buf, maxx + buf, maxy + buf, transform=src.transform)
 
        elevation = src.read(1, window=window).astype(np.float32)
        if src.nodata is not None:
            elevation[elevation == src.nodata] = np.nan
        transform = src.window_transform(window)
 
        px_x = transform.a
        px_y = -transform.e
 
        dzdy, dzdx = np.gradient(elevation, px_y, px_x)
        slope = np.sqrt(dzdx**2 + dzdy**2) * 100
 
        stat = zonal_stats([geom], slope, affine=transform, nodata=np.nan, stats=["mean"])[0]
        mean_slopes.append(stat["mean"])
 
basins["MeanSlope"] = mean_slopes
 
print(f"Processed {len(basins)} basins, one window at a time")
print(basins.drop(columns="geometry"))
 
basins.drop(columns="geometry").to_csv("./data/terrain_predictors.csv", index=False)