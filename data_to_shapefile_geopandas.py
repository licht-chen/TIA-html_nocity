# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 15:58:50 2021

@author: licht0104
"""

import pandas as pd
import geopandas as gpd
from shapely import geometry
from shapely.geometry import Point
from shapely.geometry import LineString
import shapefile as shp
from datetime import date
# data = pd.read_csv("G:\\共用雲端硬碟\\台北鼎漢(C_Public)\\Public\\014程式開發 TIA\\Output Data\\Gis\\C000_府中美學\\gis_sidewalk.csv", encoding='ANSI')
# output_path = "G:\\共用雲端硬碟\\台北鼎漢(C_Public)\\Public\\014程式開發 TIA\\Output Data\\Gis\\C000_府中美學"

def sidewalk_shp(data, output_path):
    df = data
    for i in range(df.shape[0]):       
        lon = data.loc[i,'PositionLon'].split('[')[1].split(']')[0].split(', ')
        lat = data.loc[i,'PositionLat'].split('[')[1].split(']')[0].split(', ')
        geo = []
        for j in range(len(lon) ):
            geo.append(Point( (float(lon[j]), float(lat[j])) ) )
        df.loc[i,'geometry'] = LineString(geo)
        # df.loc[i,'geometry'] = geometry.LinearRing(geo)
        df.loc[i, 'Number'] = str(df.loc[i, 'Number'])
        df.loc[i, 'id'] = str(df.loc[i, 'id'])
        df.loc[i, 'direction'] = str(df.loc[i, 'direction'])
        df.loc[i, 'totalwidth'] = str(df.loc[i, 'totalwidth'])
        df.loc[i, 'walkwidth'] = str(df.loc[i, 'walkwidth'])
        df.loc[i, 'ramp'] = str(df.loc[i, 'ramp'])
    df = gpd.GeoDataFrame(df, geometry='geometry')
    df.to_file(output_path + '\\gid_new_sidewalk2.shp', driver='ESRI Shapefile', encoding='utf-8', index=None)
