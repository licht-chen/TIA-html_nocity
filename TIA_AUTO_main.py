# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 13:10:46 2020

@author: user
"""
import os
import pandas as pd
import math
import twd97
import numpy as np
import time
import string
from datetime import datetime
import data_to_shapefile_shp

#=========== distance function 經緯度換算距離======== (lat: 緯度；lon: 經度) #
def earth_dist_1( lat1, long1, lat2, long2):
    rad = math.pi/180
    a1 = lat1 * rad
    a2 = long1 * rad
    b1 = lat2 * rad
    b2 = long2 * rad
    dis_lon = b2 - a2
    dis_lat = b1 - a1
    a = pow( (math.sin(dis_lat/2)),2) + math.cos(a1) * math.cos(b1) * pow( (math.sin(dis_lon/2)),2)
    R = 6378.145*1000
    d = 2 * R * math.asin(math.sqrt(a) )
    return(d)
# ============ 基地目標範圍內之物件提取 ============ #
def dist_cal(his_data, obj_coordinate, obj_range, columne_lat_name, column_lon_name):
    # final_data = pd.DataFrame(columns=his_data.columns)
    # for i in range(his_data.shape[0]):
    #     dist = earth_dist_1(float(obj_coordinate[0]), float(obj_coordinate[1]), his_data.iloc[i][columne_lat_name], his_data.iloc[i][column_lon_name])
    #     if dist < float(obj_range): 
    #         # cal_dist.append(dist)
    #         # print(dist)
    #         # print(final_data.empty)
    #         if final_data.empty:
    #             final_data = his_data.loc[i].to_frame().transpose()
    #         else:
    #             final_data = pd.concat([final_data, his_data.loc[i].to_frame().transpose()], axis=0)
    his_data['distance'] = his_data.apply(lambda x: earth_dist_1( obj_coordinate[0], obj_coordinate[1], x[columne_lat_name], x[column_lon_name] ), axis='columns')
    final_data = his_data[ his_data['distance'] <= obj_range].drop(['distance'], axis='columns')
    return final_data
# ============ 基地目標範圍內之物件提取(道路) ============ #
def dist_cal_road(his_data, obj_coordinate, obj_range, columne_lat_name, column_lon_name):
    # his_data = sidewalk
    # his_data = road
    # columne_lat_name = 'PositionLat'
    # column_lon_name = "PositionLon"
    # obj_coordinate = base_coordinate['府中站']
    # obj_range = base_range['府中站']
    final_data = pd.DataFrame()
    # tStart = time.time()
    for item in range(his_data.shape[0]):
        item = his_data.loc[item]
        # item = his_data.loc[0]
        # print(item)
        if str(item[columne_lat_name]) != 'nan':
            # print(item)
            temp_check = pd.DataFrame()
            temp_check['PositionLat'] = item[columne_lat_name].split('[')[1].split(']')[0].split(', ')
            temp_check['PositionLon'] = item[column_lon_name].split('[')[1].split(']')[0].split(', ')
            temp_check['distance'] = temp_check.apply(lambda x: earth_dist_1( obj_coordinate[0], obj_coordinate[1], float(x[columne_lat_name]), float(x[column_lon_name]) ), axis='columns')
            check = temp_check[temp_check['distance'] <= obj_range]
            if check.shape[0] >0:
                if final_data.empty:
                    final_data = item.to_frame().transpose()
                else:
                    final_data = pd.concat([final_data, item.to_frame().transpose()], axis=0)
    # tEnd = time.time()
    # print("It cost %f sec" % (tEnd - tStart))
    return final_data

# ============ TWD97 二度分帶座標 轉換 經緯度座標 ============ #
def twd97_to_wgs84(data, columne_lat_name, columne_lon_name):
    temp_lat = []
    temp_long = []
    for i in range(data.shape[0]):
        aa = twd97.towgs84(data.iloc[i][columne_lat_name], data.iloc[i][columne_lon_name])
        temp_lat.append(aa[0])
        temp_long.append(aa[1])
    data["PositionLat"] = temp_lat
    data["PositionLon"] = temp_long
    return data
# ============ 利用 stop of route 資訊，整併各站牌所經之所有路線名稱 與 總數量，並記錄該站牌的點位ID、經緯度、站牌名稱、站牌地址等資訊 ============ #
# ============ 其中， data station 主要提供公車站牌 經緯度資訊、站牌中文地址 兩資訊============ #
def cal_number(base_stopofroute,data_station,lat, lon, station_id,station_address):
    # base_stopofroute = base_inner_stopofroute
    # data_station = innercity_station
    # station_id = "StationID"
    # station_id = "StopName_Zh_tw"
    # station_address = "StationAddress"
    # lat = "PositionLat"
    # lon = "PositionLon"
    #  base_stopofroute  = base1_inter_stopofroute
    # data_station = intercity_stop
    temp_data = pd.DataFrame()
    temp_cal = {}
    ## 於 stop of route 當中，站牌的經緯度資訊會因為各家業者所提供的不同而不同，因此會先以 Station (公車站牌) 所提供的為主
    ## 如若無該Station 資訊，則以 stop of route 之平均作為經緯度資訊
    if data_station.empty != True:
        station_id_list = list(base_stopofroute[station_id].unique())
        for i in station_id_list:
            # i = station_id_list[0]
            # i = 2613
            # station_id = "StationID"
            temp_stopofroute = base_stopofroute[base_stopofroute[station_id] == i]
            # j[lat]
            # list(data2[ data2[station_id] ==i][lat])[0]
            ### station_inf = ["PositionLat", "PositionLon", "StationID", "StationAddress"]
            temp_cal["StationID"] = i
            if len(list(temp_stopofroute["StopName_Zh_tw"])[0]) != 0:
                temp_cal["StopName_Zh_tw"] =  list(temp_stopofroute["StopName_Zh_tw"])[0]
            else:
                temp_cal["StopName_Zh_tw"] = "-"
            if len(list(data_station[data_station[station_id] == i][station_address])) != 0:
                temp_cal["StationAddress"] = list(data_station[data_station[station_id] == i][station_address])[0]
            else:
                temp_cal["StationAddress"] = "-"
            if len(list(temp_stopofroute["SubRouteName_Zh_tw"].value_counts().keys())) != 0:
                temp_cal["SubRouteName_Zh_tw"] = list(temp_stopofroute["SubRouteName_Zh_tw"].value_counts().keys())
            else:
                temp_cal["SubRouteName_Zh_tw"] = "-"
            temp_cal["PositionLat"] = round( list(data_station[ data_station[station_id] ==i][lat])[0] ,6)
            temp_cal["PositionLon"] = round( list(data_station[ data_station[station_id] ==i][lon])[0] ,6)
            temp_cal["SubRouteNumber"] = len(temp_cal["SubRouteName_Zh_tw"])
            cityname = list(temp_stopofroute['City'].unique())
            temp_cal["CityName"] = ''
            if len(cityname) > 1:
                for city in cityname:
                    if temp_cal["CityName"] == '':
                        temp_cal["CityName"] =  city
                    else:
                        temp_cal["CityName"] =  temp_cal["CityName"] + ", " + city
            else:
                temp_cal["CityName"] =  cityname[0]
            
            if temp_data.empty == True:
                temp_data = pd.DataFrame.from_dict(temp_cal,orient="index").transpose()
            else:
                temp_data = pd.concat([pd.DataFrame.from_dict(temp_cal,orient="index").transpose(),temp_data],axis=0)
    else:
        ## 透過 stationid 以及 去返程(0:去; 1:返) ，以區分對向兩車站別
        station_id_list = list(base_stopofroute[station_id].unique())
        for i in station_id_list:
            temp_stopofroute = base_stopofroute[base_stopofroute[station_id] == i]
            temp_cal["StationID"] = str(i)
            if len(list(temp_stopofroute["StopName_Zh_tw"])[0]) != 0:
                temp_cal["StopName_Zh_tw"] =  list(temp_stopofroute["StopName_Zh_tw"])[0]
            else:
                temp_cal["StopName_Zh_tw"] = "-"
            temp_cal["StationAddress"] = "-"
            if len(list(temp_stopofroute["SubRouteName_Zh_tw"].value_counts().keys())) != 0:
                temp_cal["SubRouteName_Zh_tw"] = list(temp_stopofroute["SubRouteName_Zh_tw"].value_counts().keys())
            else:
                temp_cal["SubRouteName_Zh_tw"] = "-"
            temp_cal["PositionLat"] = round( np.mean(list(temp_stopofroute[lat])) ,6)
            temp_cal["PositionLon"] = round( np.mean(list(temp_stopofroute[lon])) ,6)
            temp_cal["SubRouteNumber"] = len(temp_cal["SubRouteName_Zh_tw"])
            cityname = list(temp_stopofroute['City'].unique())
            temp_cal["CityName"] = ''
            if len(cityname) > 1:
                for city in cityname:
                    if temp_cal["CityName"] == '':
                        temp_cal["CityName"] =  city
                    else:
                        temp_cal["CityName"] =  temp_cal["CityName"] + ", " + city
            else:
                temp_cal["CityName"] =  cityname[0]
            if temp_data.empty == True:
                temp_data = pd.DataFrame.from_dict(temp_cal,orient="index").transpose()
            else:
                temp_data = pd.concat([pd.DataFrame.from_dict(temp_cal,orient="index").transpose(),temp_data],axis=0)
            # i = list( group_data.size().keys() )[1]
            # i = 2613
            # station_id = "StationID"
            # j = base_stopofroute[base_stopofroute[station_id] == i].groupby("Direction")
            # j[lat]
            # list(data2[ data2[station_id] ==i][lat])[0]
            ### station_inf = ["PositionLat", "PositionLon", "StationID", "StationAddress"]
            # for k in j.size().keys():
            #     # k=0
            #     a = j.get_group(k)
            #     temp_cal["StationID"] = str(i)+"_"+str(k)
            #     temp_cal["StopName_Zh_tw"] =  list(a["StopName_Zh_tw"])[0]
            #     temp_cal["StationAddress"] = "-"
            #     temp_cal["SubRouteName_Zh_tw"] = list(a["SubRouteName_Zh_tw"].value_counts().keys())
            #     temp_cal["PositionLat"] = round( np.mean(list(a[lat])) ,6)
            #     temp_cal["PositionLon"] = round( np.mean(list(a[lon])) ,6)
            #     temp_cal["SubRouteNumber"] = len(temp_cal["SubRouteName_Zh_tw"])
            #     if temp_data.empty == True:
            #         temp_data = pd.DataFrame.from_dict(temp_cal,orient="index").transpose()
            #     else:
            #         temp_data = pd.concat([pd.DataFrame.from_dict(temp_cal,orient="index").transpose(),temp_data],axis=0)
    temp_data = temp_data.reset_index().drop(["index"],axis=1)
    # temp_data["Number"] = temp_data.index + 1
    return temp_data

# ============ 市區公車路線班次時間整理 ============ #
def time_set(time):
    if len(time) and (time[0] != ' ') == True:
        time = str( int(list(time)[0]) )
        if len(time) <4:
            time = "0" + time[0:1] + ":" + time[1:3]
            # print("yeeeeeeeeee")
        else:
            time = time[0:2] + ":" + time[2:4]
    else:
        time = "-"
    return time
# ============ 公路與市區公車「路線資訊」整理 ============ #
def route_information(his_data, base_stopofroute, subrouteid, route_col_inf, inner_or_intercity):
    # inner_route_inf = ["RouteID","SubRouteName_Zh_tw","FirstBusTime","LastBusTime","HolidayFirstBusTime","HolidayLastBusTime","DepartureStopNameZh","DestinationStopNameZh","CityName"]
    # intercity_route_inf = ["RouteID","SubRouteName_Zh_tw","DepartureStopNameZh","DestinationStopNameZh", "Headsign", "CityName"]
    # subrouteid = "SubRouteID"
    # his_data = innercity_route
    # base_stopofroute = base_inner_stopofroute
    # route_col_inf = inner_route_inf
    # inner_or_intercity = 1
    # aa= len(list(data[subrouteid].value_counts().keys()))
    # bb = len(list(data["RouteID"].value_counts().keys()))
    temp_data = pd.DataFrame()
    temp_route = {}
    """透過 各路線唯一代碼 : SubRouteID 進行 路線資訊整理"""
    for i in list(base_stopofroute[subrouteid].unique()):
        # print(len(list(j[route_col_inf[2] ].value_counts().keys())))
        # i = list(base_stopofroute[subrouteid].unique())[0]
        # i = 157770
        # print(i)
        ## 因各縣市資料合併後，會有不同縣市 但 公車路線 ID (SubRouteID) 相同之情況，因此需先額外從 stopofroute 提取cityname，已能拿到正確縣市的公車路線資訊
        temp_base_stopofroute = base_stopofroute[ base_stopofroute[subrouteid] == i]
        cityname = list(temp_base_stopofroute['City'].unique())[0]
        temp_route_information = his_data[ his_data[subrouteid]==i ]
        # print(list(temp_route_information['City'].unique()))
        temp_route_information = temp_route_information[ temp_route_information['City'] == cityname]
        # print(len(list(j[route_col_inf[2] ].value_counts().keys())))
        if len(list(temp_route_information[route_col_inf[2] ].unique())) == 1:
            # print(j)
            temp_route[route_col_inf[0]] = i
            if inner_or_intercity == 1:
                if len(list(temp_route_information[route_col_inf[1]].value_counts().keys())) != 0:
                    temp_route["RouteName_Zh_tw"] = list(temp_route_information[route_col_inf[1]].value_counts().keys())[0]
                else:
                    temp_route["RouteName_Zh_tw"] = "-"
                time = temp_route_information[route_col_inf[2] ].value_counts().keys()
                temp_route[route_col_inf[2]] = time_set(time)
                time = temp_route_information[route_col_inf[3] ].value_counts().keys()
                temp_route[route_col_inf[3]] = time_set(time)
                time = temp_route_information[route_col_inf[4] ].value_counts().keys()
                temp_route[route_col_inf[4]] = time_set(time)
                time = temp_route_information[route_col_inf[5] ].value_counts().keys()
                temp_route[route_col_inf[5]] = time_set(time)
                if len(temp_route_information[route_col_inf[6]].value_counts().keys()) != 0:
                    temp_route[route_col_inf[6]] = list(temp_route_information[route_col_inf[6]].value_counts().keys())[0]
                else:
                    temp_route[route_col_inf[6]] = "-"
                if len(temp_route_information[route_col_inf[7]].value_counts().keys()) != 0:
                    temp_route[route_col_inf[7]] = list(temp_route_information[route_col_inf[7]].value_counts().keys())[0]
                else:
                    temp_route[route_col_inf[6]] = "-"
                temp_route[route_col_inf[8]] = cityname
            else:
                route_name = list(temp_route_information[route_col_inf[1]])[0]
                route_name = list(route_name)
                temp_route[route_col_inf[1]] = ''
                for j in range(len(route_name) ):
                    if j == 0 or j == len(route_name)-1:
                        if route_name[j] != str(0):
                            temp_route[route_col_inf[1]] = temp_route[route_col_inf[1]] + route_name[j]
                    else:
                        temp_route[route_col_inf[1]] = temp_route[route_col_inf[1]] + route_name[j]
                if len(list(temp_route_information[route_col_inf[2]].value_counts().keys())) != 0:
                    temp_route[route_col_inf[2]] = list(temp_route_information[route_col_inf[2]].value_counts().keys())[0]
                else:
                    temp_route[route_col_inf[2]] = "-"
                if len(list(temp_route_information[route_col_inf[3]].value_counts().keys())) != 0:
                    temp_route[route_col_inf[3]] = list(temp_route_information[route_col_inf[3]].value_counts().keys())[0]
                else:
                    temp_route[route_col_inf[3]] = "-"
                if len(list(temp_route_information[route_col_inf[4]].value_counts().keys())) != 0:
                    temp_route[route_col_inf[4]] = list(temp_route_information[route_col_inf[4]].value_counts().keys())[0]
                else:
                    temp_route[route_col_inf[4]] = "-"
                temp_route[route_col_inf[5]] = cityname
        elif len(list(temp_route_information[route_col_inf[2]].unique())) > 1:
            for k in list(temp_route_information[route_col_inf[2]].unique()):
                # k = list(j[route_col_inf[2]].value_counts().keys() )[0]
                a = temp_route_information[ temp_route_information[route_col_inf[2]]==k ]
                temp_route[route_col_inf[0]] = i
                if inner_or_intercity == 1:
                    if len(list(temp_route_information[route_col_inf[1]].value_counts().keys())) != 0:
                        temp_route["RouteName_Zh_tw"] = list(temp_route_information[route_col_inf[1]].value_counts().keys())[0]
                    else:
                        temp_route["RouteName_Zh_tw"] = "-"
                    time = a[route_col_inf[2] ].value_counts().keys()
                    temp_route[route_col_inf[2]] = time_set(time)
                    time = a[route_col_inf[3] ].value_counts().keys()
                    temp_route[route_col_inf[3]] = time_set(time)
                    time = a[route_col_inf[4] ].value_counts().keys()
                    temp_route[route_col_inf[4]] = time_set(time)
                    time = a[route_col_inf[5] ].value_counts().keys()
                    temp_route[route_col_inf[5]] = time_set(time)
                    if len(a[route_col_inf[6]].value_counts().keys()) != 0:
                        temp_route[route_col_inf[6]] = list(a[route_col_inf[6]].value_counts().keys())[0]
                    else:
                        temp_route[route_col_inf[6]] = " "
                    if len(a[route_col_inf[7]].value_counts().keys()) != 0:
                        temp_route[route_col_inf[7]] = list(a[route_col_inf[7]].value_counts().keys())[0]
                    else:
                        temp_route[route_col_inf[6]] = "-"
                    temp_route[route_col_inf[8]] = cityname
                else:
                    route_name = list(temp_route_information[route_col_inf[1]])[0]
                    route_name = list(route_name)
                    temp_route[route_col_inf[1]] = ''
                    for j in range(len(route_name) ):
                        if j == 0 or j == len(route_name)-1:
                            if route_name[j] != str(0):
                                temp_route[route_col_inf[1]] = temp_route[route_col_inf[1]] + route_name[j]
                        else:
                            temp_route[route_col_inf[1]] = temp_route[route_col_inf[1]] + route_name[j]
                    temp_route[route_col_inf[2]] = list(a[route_col_inf[2]].value_counts().keys())[0]
                    temp_route[route_col_inf[3]] = list(a[route_col_inf[3]].value_counts().keys())[0]
                    temp_route[route_col_inf[4]] = list(a[route_col_inf[4]].value_counts().keys())[0]
                    temp_route[route_col_inf[5]] = cityname
        else:
            # print(j[route_col_inf[6]])
            # print(j[route_col_inf[6]].value_counts().keys())
            temp_route[route_col_inf[0]] = i
            if inner_or_intercity == 1:
                if len(list(temp_route_information[route_col_inf[1]].value_counts().keys())) != 0:
                    temp_route["RouteName_Zh_tw"] = list(temp_route_information[route_col_inf[1]].value_counts().keys())[0]
                else:
                    temp_route["RouteName_Zh_tw"] = "-"
                temp_route[route_col_inf[2]] = "-"
                temp_route[route_col_inf[3]] = "-"
                temp_route[route_col_inf[4]] = "-"
                temp_route[route_col_inf[5]] = "-"
                if len(temp_route_information[route_col_inf[6]].value_counts().keys()) != 0:
                    temp_route[route_col_inf[6]] = list(temp_route_information[route_col_inf[6]].value_counts().keys())[0]
                else:
                    temp_route[route_col_inf[6]] = " "
                if len(temp_route_information[route_col_inf[7]].value_counts().keys()) != 0:
                    temp_route[route_col_inf[7]] = list(temp_route_information[route_col_inf[7]].value_counts().keys())[0]
                else:
                    temp_route[route_col_inf[6]] = "-"
                temp_route[route_col_inf[8]] = cityname
            else:
                route_name = list(temp_route_information[route_col_inf[1]])[0]
                route_name = list(route_name)
                if len(route_name) > 1:
                    route_name = route_name[0]
                temp_route[route_col_inf[1]] = ''
                for j in range(len(route_name) ):
                    if j == 0 or j == len(route_name)-1:
                        if route_name[j] != str(0):
                            temp_route[route_col_inf[1]] = temp_route[route_col_inf[1]] + route_name[j]
                    else:
                        temp_route[route_col_inf[1]] = temp_route[route_col_inf[1]] + route_name[j]
                if len(list(temp_route_information[route_col_inf[2]].value_counts().keys())) != 0:
                    temp_route[route_col_inf[2]] = list(temp_route_information[route_col_inf[2]].value_counts().keys())[0]
                else:
                    temp_route[route_col_inf[2]] = "-"
                if len(list(temp_route_information[route_col_inf[3]].value_counts().keys())) != 0:
                    temp_route[route_col_inf[3]] = list(temp_route_information[route_col_inf[3]].value_counts().keys())[0]
                else:
                    temp_route[route_col_inf[3]] = 0
                if len(list(temp_route_information[route_col_inf[4]].value_counts().keys())) != 0:
                    temp_route[route_col_inf[4]] = list(temp_route_information[route_col_inf[4]].value_counts().keys())[0]
                else:
                    temp_route[route_col_inf[4]] = "-"
                temp_route[route_col_inf[5]] = cityname
                # temp_route[route_col_inf[8]] = list(j[route_col_inf[8]].value_counts().keys())[0]
        if temp_data.empty == True:
            temp_data = pd.DataFrame.from_dict(temp_route,orient="index").transpose()
        else:
            temp_data = pd.concat([pd.DataFrame.from_dict(temp_route,orient="index").transpose(),temp_data],axis=0)
    return temp_data

# ============ 篩選兩個(含)以上基地的重複資訊，利用 key columns ============ #
def Comparison_data(data1, data2, key_id):
    # i = 25.01097
    # j = 121.02545
    # data1 = final_bus_cal_data
    # data2 = final_bus_cal_data2
    # i = list(data1["PositionLat"])
    # temp_data = data2[data2["PositionLat"]==i]
    for i in list(data2[key_id]):
        if i in list(data1[key_id]):
            # print( data2[data2["StationID"] == i] ["StopName_Zh_tw"])
            continue
        else:
            temp_data = data2[data2[key_id] == i] 
            data1 = pd.concat([data1, temp_data],axis=0)
    return data1
# ============ 站牌、路線 文字符號清理 ============ #
def Data_clear(data, col_name):
    # data = temp_inner_station
    # col_name = "SubRouteName_Zh_tw"
    # data[col_name]
    data = data.reset_index().rename(columns = {"index":"Number"})
    data['Number'] = data.index +1
    for i in range(data.shape[0]):
        # print(i)
        temp = str(data[col_name].loc[i])
        temp = temp.replace("['","").replace("['","").replace("']","").replace("', '","、")
        data[col_name].loc[i] = temp
    return data

# ========== 判斷原始資料是否需更新重新下載 ==========#
# def Data_time_check(filename, bat_name):
#     if os.path.exists(filename):
#         datatime = time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(filename) ) )
#         datatime = datetime.strptime(datatime, "%Y-%m-%d")
#         now_time = time.strftime("%Y-%m-%d", time.localtime() )
#         now_time = datetime.strptime(now_time, "%Y-%m-%d")
#         if (now_time - datatime).days > 3:
#             print(" ~~~~ 重新下載資料 ~~~~ ")
#             os.startfile(bat_name)
#         else:
#             print(" ~~~~ 資料仍在時效範圍內，無須下載 ~~~~ ")
#     else:
#         os.startfile(bat_name)
        
# ========== 基地範圍圓圈計算 (已知座標、距離、方位夾角 -> 換算 另一點座標)  ========== 
def coordinate(Position, Radius, brng):
    R = 6378.145 #Radius of the Earth
    # brng = Bearing(A, B) # Bearing is 90 degrees converted to radians.
    # brng = dirangel
    # brng = angle
    d = float(Radius)/1000 #Distance in km
    # d = earth_dist_1(A[0],A[1],B[0],B[1])/1000
    # d = geopy.distance.geodesic(A,B).kilometers
    # d = geopy.distance.distance(A,B).kilometers
    # conver lat and lon to radians
    lat1 = math.radians(float(Position[0]) ) #Current lat point converted to radians
    lon1 = math.radians(float(Position[1]) ) #Current long point converted to radians
    
    lat2 = math.asin( math.sin(lat1)*math.cos(d/R) + math.cos(lat1)*math.sin(d/R)*math.cos(brng))
    lon2 = lon1 + math.atan2( math.sin(brng)*math.sin(d/R)*math.cos(lat1), math.cos(d/R)-math.sin(lat1)*math.sin(lat2) )
    
    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)
    point = [lat2, lon2]
    return point


def TIA(project_name, base_name, base_coordinate, base_range, modal, road_type_choice, output_bool):  
    # print(project_name)
    # print(base_name)
    # print(base_coordinate)
    # print(base_range)
    # print(modal)
    # print(road_type_choice)
    # project_name = 'C000_府中美學'
    # base_name = ['府中站', '市民廣場']
    # base_coordinate = {'府中站': [25.00853207650213, 121.45942177851646],
    #                     '市民廣場': [25.01234076405166, 121.46571388726626]}
    # base_range = {'府中站': 500, '市民廣場': 500}
    # city['主縣市'] = '新北市'
    # city['跨縣市'] = ''
    # other_city = []
    # base_across_city = {'府中站': 'N', '市民廣場': 'N'}
    # project_name = 'test_parking_C840_台北市政府'
    # base_name = ['台北市政府']
    # base_coordinate = {'台北市政府': [25.035384299711488, 121.56442710383658]}
    # base_range = {'台北市政府': 800}
    # city['主縣市'] = '臺北市'
    # city['跨縣市'] = ''
    # other_city = []
    # base_across_city = {'台北市政府': 'N'}
    # output_bool = True
    # project_name = 'C000_府中美學_2'
    # base_name = ['府中站', '市民廣場']
    # base_coordinate = {'府中站': [25.00853207650213, 121.45942177851646],
    #                     '市民廣場': [25.01234076405166, 121.46571388726626]}
    # base_range = {'府中站': 500, '市民廣場': 500}
    # modal_choice = []
    # modal_choice.append("Y")
    # modal_choice.append("Y")
    # modal_choice.append("Y")
    # modal_choice.append("Y")
    # modal_choice.append("Y")
    # modal_choice.append("Y")
    # modal_choice.append("Y")
    # modal_choice.append("Y")
    # modal_choice.append("N")
    # modal_choice.append("N")
    # modal_choice.append("N")
    # modal_choice.append("N")
    # modal_choice.append("N")
    # modal = {}
    # modal_category = ['InnerCity_Bus', 'InterCity_Bus', 'Bike', 'Parking_Outside', 'Parking_Roadside', 'THSR', 'TRA',
    #                   'TRTC','KRTC', 'TYMC', 'KLRT', 'NTDLRT', 'TRTCMG']    
    # for i in range(len(modal_category) ):
    #     modal[modal_category[i]] = modal_choice[i]
    # road_choice = []
    # road_choice.append("N")
    # road_choice.append("N")
    # road_category = ['Road','SideWalk']
    # road_type_choice = {}
    # for i in range(len(road_category)):
    #     road_type_choice[road_category[i]] = road_choice[i]
    
    # print(city)
    # print(ptx_innercity_bus_stopofroute_cityname)
    input_path = "G:\\共用雲端硬碟\\台北鼎漢(C_Public)\\Public\\014程式開發 TIA\\Public Transportation Data\\"
    input_path_sidewalk = "G:\\共用雲端硬碟\\台北鼎漢(C_Public)\\Public\\014程式開發 TIA\\GIS\\Shapefile\\人行道\\"
    input_path_road = "G:\\共用雲端硬碟\\台北鼎漢(C_Public)\\Public\\014程式開發 TIA\\GIS\\Shapefile\\縣市道路資訊\\"
    # bat_path = path
    # input_path = "G:\\共用雲端硬碟\\台北鼎漢(C_Public)\\Public\\014程式開發 TIA\\Public Transportation Data\\"
    for i in modal.keys():
        # ========= 市區公車 ========== #
        if ("InnerCity" in i and modal[i] == 'Y'):
            # ========== Intercity StopOfRoute ========== #
            filename = input_path + "City_bus_StopOfRoute.csv"
            # bat_name = bat_path + "Run_intercity_bus_stopofroute.bat"
            # Data_time_check(filename, bat_name)
            try:
                innercity_stopofroute = pd.read_csv(filename , encoding = "utf8", low_memory=False)
            except:
                innercity_stopofroute = pd.read_csv(filename, encoding = "ANSI", low_memory=False)
            # ========== Intercity Stop ========== #
            filename = input_path + "City_bus_Station.csv"
            # bat_name = bat_path + "Run_intercity_bus_stop.bat"
            # Data_time_check(filename, bat_name)
            try:
                innercity_station = pd.read_csv(filename, encoding = "utf8", low_memory=False)
            except:
                innercity_station = pd.read_csv(filename, encoding = "ANSI", low_memory=False)
            # ========== Intercity Route ========== #
            filename = input_path + "City_bus_Route.csv"
            # bat_name = bat_path + "Run_intercity_bus_route.bat"
            # Data_time_check(filename, bat_name)
            try:
                innercity_route = pd.read_csv(filename, encoding = "utf8", low_memory=False)
            except:
                innercity_route = pd.read_csv(filename, encoding = "ANSI", low_memory=False)
        # ========= 公路客運 ========== #
        if ("InterCity" in i and modal[i] == 'Y'):
            # ========== Intercity StopOfRoute ========== #
            filename = input_path + "InterCity_bus_StopOfRoute.csv"
            # bat_name = bat_path + "Run_intercity_bus_stopofroute.bat"
            # Data_time_check(filename, bat_name)
            try:
                intercity_stopofroute = pd.read_csv(filename , encoding = "utf8", low_memory=False)
            except:
                intercity_stopofroute = pd.read_csv(filename, encoding = "ANSI", low_memory=False)
            # ========== Intercity Stop ========== #
            filename = input_path + "InterCity_bus_Stop.csv"
            # bat_name = bat_path + "Run_intercity_bus_stop.bat"
            # Data_time_check(filename, bat_name)
            try:
                intercity_stop = pd.read_csv(filename, encoding = "utf8", low_memory=False)
            except:
                intercity_stop = pd.read_csv(filename, encoding = "ANSI", low_memory=False)
            # ========== Intercity Route ========== #
            filename = input_path + "InterCity_bus_Route.csv"
            # bat_name = bat_path + "Run_intercity_bus_route.bat"
            # Data_time_check(filename, bat_name)
            try:
                intercity_route = pd.read_csv(filename, encoding = "utf8", low_memory=False)
            except:
                intercity_route = pd.read_csv(filename, encoding = "ANSI", low_memory=False)
        # ========= 高鐵 ========== #
        if ("THSR" in i and modal[i] =='Y'):
            filename = input_path + "THSR_Station.csv"
            # bat_name = bat_path + "Run_thsr.bat"
            # Data_time_check(filename, bat_name)
            try:
                thsr = pd.read_csv(filename , encoding = "utf8", low_memory=False)
            except:
                thsr = pd.read_csv(filename, encoding = "ANSI", low_memory=False)
        # ========= 台北捷運 ========== #
        if ("TRTC" in i and modal[i] == 'Y'):
            filename = input_path + "TRTC_Station.csv"
            # bat_name = bat_path + "Run_mrt.bat"
            # Data_time_check(filename, bat_name)
            try:
                trtc = pd.read_csv(input_path+ "TRTC_Station.csv", encoding = "utf8", low_memory=False)
            except:
                trtc = pd.read_csv(input_path+ "TRTC_Station.csv", encoding = "ANSI", low_memory=False)
        # ========= 桃園捷運 ========== #
        if ("TYMC" in i and modal[i] == 'Y'):
            filename = input_path + "TYMC_Station.csv"
            try:
                tymc = pd.read_csv(input_path+ "TYMC_Station.csv", encoding = "utf8", low_memory=False)
            except:
                tymc = pd.read_csv(input_path+ "TYMC_Station.csv", encoding = "ANSI", low_memory=False)
        # ========= 高雄捷運 ========== #
        if ("KRTC" in i and modal[i] == 'Y'):
            filename = input_path + "KRTC_Station.csv"
            try:
                krtc = pd.read_csv(input_path+ "KRTC_Station.csv", encoding = "utf8", low_memory=False)
            except:
                krtc = pd.read_csv(input_path+ "KRTC_Station.csv", encoding = "ANSI", low_memory=False)
        # ========= 淡海輕軌 ========== #
        if ("NTDLRT" in i and modal[i] == 'Y'):
            filename = input_path + "NTDLRT_Station.csv"
            try:
                ntdlrt = pd.read_csv(input_path+ "NTDLRT_Station.csv", encoding = "utf8", low_memory=False)
            except:
                ntdlrt = pd.read_csv(input_path+ "NTDLRT_Station.csv", encoding = "ANSI", low_memory=False)
        # ========= 高雄輕軌 ========== #
        if ("KLRT" in i and modal[i] == 'Y'):
            filename = input_path + "KLRT_Station.csv"
            try:
                klrt = pd.read_csv(input_path+ "KLRT_Station.csv", encoding = "utf8", low_memory=False)
            except:
                klrt = pd.read_csv(input_path+ "KLRT_Station.csv", encoding = "ANSI", low_memory=False)
        # ========= 貓空纜車 ========== #
        if ("TRTCMG" in i and modal[i] == 'Y'):
            filename = input_path + "TRTCMG_Station.csv"
            try:
                trtcmg = pd.read_csv(input_path+ "TRTCMG_Station.csv", encoding = "utf8", low_memory=False)
            except:
                trtcmg = pd.read_csv(input_path+ "TRTCMG_Station.csv", encoding = "ANSI", low_memory=False)
        # ========= 台鐵 ========== #
        if ("TRA" in i and modal[i] == 'Y'):
            filename = input_path + "TRA_Station.csv"
            # bat_name = bat_path + "Run_tra.bat
            # Data_time_check(filename, bat_name)
            try:
                tra = pd.read_csv(input_path+ "TRA_Station.csv", encoding = "utf8", low_memory=False)
            except:
                tra = pd.read_csv(input_path+ "TRA_Station.csv", encoding = "ANSI", low_memory=False)
        # ======== 路外停車 ======= #
        if ("Outside" in i and modal[i] == 'Y'):
            filename = input_path + "Parking_Outside.csv"
            # if os.path.exists(filename):
            try:
                parking_outside = pd.read_csv(filename, encoding = "utf8", low_memory=False)
            except:
                parking_outside = pd.read_csv(filename, encoding = "ANSI", low_memory=False)
        if ("Roadside" in i and modal[i] == 'Y'):
            filename = input_path + "Parking_Roadside.csv"
            # if os.path.exists(filename):
            try:
                parking_roadside = pd.read_csv(filename, encoding = "utf8", low_memory=False)
            except:
                parking_roadside = pd.read_csv(filename, encoding = "ANSI", low_memory=False)
        if ("Bike" in i and modal[i] == 'Y'):
            filename = input_path+"Ubike.csv"
            # filename = "G:\\共用雲端硬碟\\台北鼎漢(C_Public)\\Public\\014程式開發 TIA\\Public Transportation Data\\NewTaipei\\NewTaipei_Ubike.csv"
            try:
                bike_station = pd.read_csv(filename, encoding = "utf8", low_memory=False)
            except:
                bike_station = pd.read_csv(filename, encoding = "ANSI", low_memory=False)
    
    final_inner_station = pd.DataFrame(columns=['Number','StationID','StopName_Zh_tw','StationAddress','SubRouteName_Zh_tw',
                                                'PositionLat','PositionLon','SubRouteNumber'])
    final_inner_route = pd.DataFrame()
    final_inter_station = pd.DataFrame(columns=['Number','StationID','StopName_Zh_tw','StationAddress','SubRouteName_Zh_tw',
                                                'PositionLat','PositionLon','SubRouteNumber'])
    final_inter_route = pd.DataFrame()
    final_bike_station = pd.DataFrame(columns=['Number','StationUID','StationID','AuthorityID','StationName_Zh_tw','StationName_En',
                                                'PositionLat','PositionLon','GeoHash','StationAddress_Zh_tw','StationAddress_En',
                                                'BikesCapacity','SrcUpdateTime','UpdateTime'])
    final_parking_outside = pd.DataFrame(columns=['Number','id','area','address','name','tel','serviceTime','payex','totalbike','totalbus',
                                                  'totalcar','totallargemotor','totalmotor','PositionLat','PositionLon','summary'])
    final_parking_roadside = pd.DataFrame(columns=['Number','id','roadid','roadname','type','car','moto','total','servicetime','pay',
                                                    'PositionLat','PositionLon'])
    final_thsr_station = pd.DataFrame(columns=['Number','StationUID','StationID','StationCode','StationName_Zh_tw','StationName_En',
                                                'StationAddress','OperatorID','LocationCity','LocationCityCode','LocationTown',
                                                'LocationTownCode','PositionLat','PositionLon','GeoHash','VersionID','UpdateTime'])
    final_trtc_station = pd.DataFrame()
    final_tra_station = pd.DataFrame(columns=['Number','StationUID','StationID','OperatorID','StationName_Zh_tw','StationName_En',
                                              'StationAddress','LocationCity','LocationCityCode','LocationTown','LocationTownCode',
                                              'StationClass','StationPhone','PositionLat','PositionLon','GeoHash','VersionID','UpdateTime'])
    final_tymc_station = pd.DataFrame(columns=['Number','StationUID','StationID','StationName_Zh_tw','StationName_En','StationAddress',
                                                'BikeAllowOnHoliday','LocationCity','LocationCityCode','LocationTown','LocationTownCode',
                                                'PositionLat','PositionLon','GeoHash','VersionID','SrcUpdateTime','UpdateTime'])
    # final_krtc_station = pd.DataFrame(columns=['Number','StationUID','StationID','StationName_Zh_tw','StationName_En','StationAddress',
    #                                            'BikeAllowOnHoliday','LocationCity','LocationCityCode','LocationTown','LocationTownCode',
    #                                            'PositionLat','PositionLon','GeoHash','VersionID','SrcUpdateTime','UpdateTime'])
    # final_klrt_station = pd.DataFrame(columns=['Number','StationUID','StationID','StationName_Zh_tw','StationName_En','StationAddress',
    #                                            'BikeAllowOnHoliday','LocationCity','LocationCityCode','LocationTown','LocationTownCode',
    #                                            'PositionLat','PositionLon','GeoHash','VersionID','SrcUpdateTime','UpdateTime'])
    # final_trtcmg_station = pd.DataFrame(columns=['Number','StationUID','StationID','StationName_Zh_tw','StationName_En','StationAddress',
    #                                            'BikeAllowOnHoliday','LocationCity','LocationCityCode','LocationTown','LocationTownCode',
    #                                            'PositionLat','PositionLon','GeoHash','VersionID','SrcUpdateTime','UpdateTime'])
    temp_inner_station = pd.DataFrame()
    temp_inner_route = pd.DataFrame()
    temp_inter_station = pd.DataFrame()
    temp_inter_route = pd.DataFrame()
    temp_bike_station = pd.DataFrame()
    temp_parking_outside = pd.DataFrame()
    temp_parking_roadside = pd.DataFrame()
    temp_thsr_station = pd.DataFrame()
    temp_trtc_station = pd.DataFrame()
    temp_tra_station = pd.DataFrame()
    temp_tymc_station = pd.DataFrame()
    # final_krtc_station = pd.DataFrame()
    # final_klrt_station = pd.DataFrame()
    # final_trtcmg_station = pd.DataFrame()
    
    ## Road
    for i in road_type_choice.keys():
        # ========= 人行道 ========== #
        if ("SideWalk" in i and road_type_choice[i] == 'Y'):
            # ========== Intercity StopOfRoute ========== #
            filename = input_path_sidewalk + "SideWalk.csv"
            # bat_name = bat_path + "Run_intercity_bus_stopofroute.bat"
            # Data_time_check(filename, bat_name)
            try:
                sidewalk = pd.read_csv(filename , encoding = "utf8", low_memory=False)
            except:
                sidewalk = pd.read_csv(filename, encoding = "ANSI", low_memory=False)
        # ========= 道路 ========== #
        if ("Road" in i and road_type_choice[i] == 'Y'):
            # ========== Intercity StopOfRoute ========== #
            filename = input_path_road + "ROAD.csv"
            # bat_name = bat_path + "Run_intercity_bus_stopofroute.bat"
            # Data_time_check(filename, bat_name)
            try:
                road = pd.read_csv(filename , encoding = "utf8", low_memory=False)
            except:
                road = pd.read_csv(filename, encoding = "ANSI", low_memory=False)
    final_sidewalk = pd.DataFrame(columns=['id','city','area','name','start','end','direction','totalwith','walkwith',
                                            'ramp','geometry'])
    final_road = pd.DataFrame(columns=['id','city','roadclass','name','width','geometry'])
    temp_sidewalk = pd.DataFrame()
    temp_road = pd.DataFrame()
    
    temp_base_name = base_name # 暫存 基地名稱
    """ ========= 資料分析 =========="""
    # 計時開始
    tStart = time.time()
    if len(base_name) == 1 :
        print("========== "+base_name[0]+" ==========")
        for j in modal.keys():
            # print('Key: ', j)
            # print("modal_choice: ",modal[j])
            if ("InnerCity" in j and modal[j] == 'Y' ):
                print("========== InnerCity Bus ==========")
                # ========== Stop of route ========= #
                base_inner_stopofroute = dist_cal(innercity_stopofroute, base_coordinate[ base_name[0] ], base_range[ base_name[0] ], "PositionLat", "PositionLon")
                if base_inner_stopofroute.shape[0] > 0:
                    # ========== Station informaiton ========= #
                    print("Station information")
                    innercity_station = pd.DataFrame()
                    if len(base_inner_stopofroute.groupby("StationID").size()) == 0 :
                        temp_inner_station = cal_number(base_inner_stopofroute, innercity_station, "PositionLat", "PositionLon", "StopName_Zh_tw", "StationAddress")
                    else:
                        temp_inner_station = cal_number(base_inner_stopofroute, innercity_station, "PositionLat", "PositionLon", "StationID", "StationAddress")
                    temp_inner_station = Data_clear(temp_inner_station, "SubRouteName_Zh_tw")
                    # if city_name in list(ptx_innercity_bus_station_cityname.keys()):
                    #     print("Station information")
                    #     filename = input_innercity_path+ "_bus_Station.csv"
                    #     if os.path.exists(filename):
                    #         # bat_name = bat_path + "Run_bus_station.bat"
                    #         # Data_time_check(filename, bat_name)
                    #         try:
                    #             innercity_station = pd.read_csv(filename, encoding = "utf8")
                    #         except:
                    #             innercity_station = pd.read_csv(filename, encoding = "ANSI")
                    #         if len(base_inner_stopofroute.groupby("StationID").size()) == 0 :
                    #             temp_inner_station = cal_number(base_inner_stopofroute, innercity_station, "PositionLat", "PositionLon", "StopName_Zh_tw", "StationAddress", inner_city_name)
                    #         else:
                    #             temp_inner_station = cal_number(base_inner_stopofroute, innercity_station, "PositionLat", "PositionLon", "StationID", "StationAddress", inner_city_name)
                    #         temp_inner_station = Data_clear(temp_inner_station, "SubRouteName_Zh_tw")
                    #     else:
                    #         print(" 至 PTX 下載此縣市市區公車「站牌點位」資料 ")
                    #         # bat_name = bat_path + "Run_bus_station.bat"
                    #         # Data_time_check(filename, bat_name)
                    # else:
                    #     print(" PTX 無此縣市市區公車「站牌點位」資料，無法提供「站點地址資訊」，若有需要請自行搜尋相關資訊並下載相關資料以進行分析")
                    # ========== Route information ========= #
                    print("Route information")
                    inner_route_inf = ["RouteID","SubRouteName_Zh_tw","FirstBusTime","LastBusTime","HolidayFirstBusTime","HolidayLastBusTime","DepartureStopNameZh","DestinationStopNameZh","CityName"]
                    temp_inner_route = route_information(innercity_route, base_inner_stopofroute, "SubRouteID", inner_route_inf, 1)
                    temp_inner_route["平日起迄時間"] = temp_inner_route["FirstBusTime"] +"-" + temp_inner_route["LastBusTime"]
                    temp_inner_route["假日起迄時間"] = temp_inner_route["HolidayFirstBusTime"] +"-" + temp_inner_route["HolidayLastBusTime"]
                    temp_inner_route["起迄站名"] = temp_inner_route["DepartureStopNameZh"] +"-" + temp_inner_route["DestinationStopNameZh"]
                else:
                    temp_inner_station = pd.DataFrame()
                    temp_inner_route = pd.DataFrame()
            if ("InterCity" in j and modal[j] =="Y"):
                print("========== InterCity Bus ==========")
                # ========== Stop of Route ==========#
                print("Stop of route information")
                base_inter_stopofroute = dist_cal(intercity_stopofroute, base_coordinate[ base_name[0] ], base_range[ base_name[0] ], "PositionLat", "PositionLon")
                # ========== Station information ==========#
                print("Station information")
                # station_inf = ["StopPosition_PositionLat", "StopPosition_PositionLon", "StationID", "StationAddress"]
                intercity_stop = pd.DataFrame()
                temp_inter_station = cal_number(base_inter_stopofroute, intercity_stop, "PositionLat","PositionLon","StationID","StopAddress")
                temp_inter_station = Data_clear(temp_inter_station, "SubRouteName_Zh_tw" )
                # ========== Route information ==========#
                print("Route information")
                intercity_route_inf = ["RouteID","SubRouteName_Zh_tw","DepartureStopNameZh","DestinationStopNameZh", "Headsign", "CityName"]
                # intercity_route_inf = ["RouteID","SubRouteName_Zh_tw","FirstBusTime","LastBusTime","HolidayFirstBusTime","HolidayLastBusTime","DepartureStopNameZh","DestinationStopNameZh"]
                temp_inter_route = route_information(intercity_route, base_inter_stopofroute, "SubRouteID", intercity_route_inf, 0)
                # temp_inter_route["平日起迄時間"] = final_inter_route["FirstBusTime"] +"-" + final_inter_route["LastBusTime"]
                # temp_inter_route["假日起迄時間"] = final_inter_route["HolidayFirstBusTime"] +"-" + final_inter_route["HolidayLastBusTime"]
                temp_inter_route["起迄站名"] = temp_inter_route["DepartureStopNameZh"] +"-" + temp_inter_route["DestinationStopNameZh"]
            if ("Bike" in j and modal[j] == 'Y'):
                print("========== Bike station ==========")                    
                temp_bike_station = dist_cal(bike_station, base_coordinate[ base_name[0] ], base_range[ base_name[0] ], "PositionLat", "PositionLon")
                if temp_bike_station.empty:
                    print(" 此基地範圍內無涵蓋任何Ubike站 ")
            if ("Outside" in j and modal[j] == 'Y'):
                print("========== Parking Outside ==========")
                # parking_outside = twd97_to_wgs84(parking_outside, "twd97X", "twd97Y")
                if parking_outside.empty != True:
                    temp_parking_outside = dist_cal(parking_outside, base_coordinate[ base_name[0] ], base_range[ base_name[0] ], "PositionLat", "PositionLon")
                    if temp_parking_outside.empty:
                        print(" 此基地範圍內無涵蓋任何路外停車場 ")
                else:
                    print("路邊停車資料需從新下載")
            if ("Roadside" in j and modal[j] == 'Y'):
                print("========== Parking Roadside ==========")
                if parking_roadside.empty != True:
                    temp_parking_roadside = dist_cal(parking_roadside, base_coordinate[ base_name[0] ], base_range[ base_name[0] ], "PositionLat", "PositionLon")
                    if temp_parking_roadside.empty:
                        print(" 此基地範圍內無涵蓋任何路邊停車格 ")
                else:
                    print("路邊停車資料需從新下載")
            if ("THSR" in j and modal[j] == 'Y'):
                print("========== THSR ==========")
                if thsr.empty != True:
                    temp_thsr_station = dist_cal(thsr, base_coordinate[ base_name[0]], base_range[ base_name[0]], "PositionLat", "PositionLon")
                if temp_thsr_station.empty:
                    # temp_thsr_station = {}
                    # columne = ["PositionLat", "PositionLon", "GeoHash", "LocationCity", "LocationCityCode", "LocationTown",
                    #            "LocationTownCode", "StationUID", "StationID", "StationCode", "Zh_tw", "En", "StationAddress",
                    #            "OperatorID", "UpdateTime", "VersionID"]
                    # for l in columne:
                    #     temp_thsr_station[l] = "-"
                    # temp_thsr_station = pd.DataFrame.from_dict(temp_thsr_station,orient="index").transpose()
                    print(" 此基地範圍內無涵蓋任何高鐵站 ")
            if ("TRTC" in j and modal[j] == 'Y'):
                print("========== TRTC ==========")
                if trtc.empty != True:
                    temp_trtc_station = dist_cal(trtc, base_coordinate[ base_name[0]], base_range[ base_name[0]], "PositionLat", "PositionLon")
                if temp_trtc_station.empty:
                    # temp_trtc_station = {}
                    # columne = ["PositionLat", "PositionLon", "GeoHash", "LocationCity", "LocationCityCode", "LocationTown",
                    #            "LocationTownCode", "StationUID", "StationID", "Zh_tw", "En", "StationAddress", "BikeAllowOnHoliday",
                    #            "SrcUpdateTime", "UpdateTime", "VersionID"]
                    # for l in columne:
                    #     temp_trtc_station[l] = "-"
                    # temp_trtc_station = pd.DataFrame.from_dict(temp_trtc_station,orient="index").transpose()
                    print(" 此基地範圍內無涵蓋任何捷運站 ")
            if ("TRA" in j and modal[j] == 'Y'):
                print("========== TRA ==========")
                if tra.empty != True:
                    temp_tra_station = dist_cal(tra, base_coordinate[ base_name[0]], base_range[ base_name[0]], "PositionLat", "PositionLon")
                if temp_tra_station.empty:
                    # temp_tra_station = {}
                    # columne = ["PositionLat", "PositionLon", "GeoHash", "LocationCity", "LocationCityCode", "LocationTown",
                    #            "LocationTownCode", "StationUID", "StationID", "Zh_tw", "En", "StationAddress", "StationPhone",
                    #            "OperatorID", "StationClass", "UpdateTime", "VersionID"]
                    # for l in columne:
                    #     temp_tra_station[l] = "-"
                    # temp_tra_station = pd.DataFrame.from_dict(temp_tra_station,orient="index").transpose()
                    print(" 此基地範圍內無涵蓋任何台鐵站 ")
            if ("TYMC" in j and modal[j] == 'Y'):
                print("========== TYMC ==========")
                if tymc.empty != True:
                    temp_tymc_station = dist_cal(tymc, base_coordinate[ base_name[0]], base_range[ base_name[0]], "PositionLat", "PositionLon")
                if temp_tymc_station.empty:
                    # temp_tra_station = {}
                    # columne = ["PositionLat", "PositionLon", "GeoHash", "LocationCity", "LocationCityCode", "LocationTown",
                    #            "LocationTownCode", "StationUID", "StationID", "Zh_tw", "En", "StationAddress", "StationPhone",
                    #            "OperatorID", "StationClass", "UpdateTime", "VersionID"]
                    # for l in columne:
                    #     temp_tra_station[l] = "-"
                    # temp_tra_station = pd.DataFrame.from_dict(temp_tra_station,orient="index").transpose()
                    print(" 此基地範圍內無涵蓋任何機場捷運站 ")
        for j in road_type_choice.keys():
            if("SideWalk" in j and road_type_choice[j] == 'Y'):
                print("========== SIDEWALK =========")
                if sidewalk.empty != True:
                    temp_sidewalk = dist_cal_road(sidewalk, base_coordinate[ base_name[0]], base_range[ base_name[0]], "PositionLat", "PositionLon")
                if temp_sidewalk.empty:
                    # temp_tra_station = {}
                    # columne = ["PositionLat", "PositionLon", "GeoHash", "LocationCity", "LocationCityCode", "LocationTown",
                    #            "LocationTownCode", "StationUID", "StationID", "Zh_tw", "En", "StationAddress", "StationPhone",
                    #            "OperatorID", "StationClass", "UpdateTime", "VersionID"]
                    # for l in columne:
                    #     temp_tra_station[l] = "-"
                    # temp_tra_station = pd.DataFrame.from_dict(temp_tra_station,orient="index").transpose()
                    print(" 此基地範圍內無涵蓋任何人行道 ")
            if("Road" in j and road_type_choice[j] == 'Y'):
                print("========== ROAD =========")
                if road.empty != True:
                    # if '縣' in city[i]:
                    #     road_city_name = city[i].split('縣')[0]
                    # elif '市' in city[i]:
                    #     road_city_name = city[i].split('市')[0]
                    temp_road = dist_cal_road(road, base_coordinate[ base_name[0]], base_range[ base_name[0]], "PositionLat", "PositionLon")
                    ## 道路分類對照表
                    # road_class_relation = {'HW':'國道', 'HU': '國道附屬道路', 'OE':'公務專用道路', '1E':'省道快速公路', '1W':'省道', '1U':'省道共線', '2W':'縣道',
                    #    '2U':'縣道共線', '3W':'鄉(鎮)道路', '3U':'鄉道共線', '4W':'產業道路', '4U':'專用公路/產業道路共線', 'RE':'市區快速道路(含匝道)',
                    #    'RD':'市區道路(路、街)(含圓環)', 'AL':'市區道路(巷、弄)', 'BR':'區塊道路', 'OR':'有路名但無法歸類(含林道)', 'OT':'無路名'}
                    # for a in range(temp_road.shape[0]):
                    #     temp_road.loc[a,'ROADCLASS1'] = road_class_relation[temp_road.loc[a,'ROADCLASS1']]
                if temp_road.empty:
                    # temp_tra_station = {}
                    # columne = ["PositionLat", "PositionLon", "GeoHash", "LocationCity", "LocationCityCode", "LocationTown",
                    #            "LocationTownCode", "StationUID", "StationID", "Zh_tw", "En", "StationAddress", "StationPhone",
                    #            "OperatorID", "StationClass", "UpdateTime", "VersionID"]
                    # for l in columne:
                    #     temp_tra_station[l] = "-"
                    # temp_tra_station = pd.DataFrame.from_dict(temp_tra_station,orient="index").transpose()
                    print(" 此基地範圍內無涵蓋任何道路 ")
    # =========== 兩基地 ========== #        
    elif len(base_name) >1 :
        print("========== "+base_name[0]+"、"+base_name[1]+" ==========")
        for j in modal.keys():
            if ("InnerCity" in j and modal[j] == 'Y' ):
                print("========== InnerCity Bus ==========")
                # ========== Stop of route ========= #
                print("Stop of route information")
                base1_inner_stopofroute = dist_cal(innercity_stopofroute, base_coordinate[ base_name[0] ], base_range[ base_name[0] ], "PositionLat", "PositionLon")
                base2_inner_stopofroute = dist_cal(innercity_stopofroute, base_coordinate[ base_name[1] ], base_range[ base_name[1] ], "PositionLat", "PositionLon")
                ## 兩基地皆有包含其他縣市市區公車 路線與站牌資訊
                if base1_inner_stopofroute.shape[0] >0 and base2_inner_stopofroute.shape[0] >0:
                    # ========== Station informaiton ========= #
                    print("Station information")
                    innercity_station = pd.DataFrame()
                    if len(base1_inner_stopofroute.groupby("StationID").size()) == 0 :
                        base1_inner_station = cal_number(base1_inner_stopofroute, innercity_station, "PositionLat", "PositionLon", "StopName_Zh_tw", "StationAddress")
                    else:
                        base1_inner_station = cal_number(base1_inner_stopofroute, innercity_station, "PositionLat", "PositionLon", "StationID", "StationAddress")
                    if len(base2_inner_stopofroute.groupby("StationID").size()) == 0 :
                        base2_inner_station = cal_number(base2_inner_stopofroute,innercity_station, "PositionLat", "PositionLon", "StopName_Zh_tw", "StationAddress")
                    else:
                        base2_inner_station = cal_number(base2_inner_stopofroute,innercity_station, "PositionLat", "PositionLon", "StationID", "StationAddress")
                    temp_inner_station = Comparison_data(base1_inner_station, base2_inner_station,"StationID")
                    temp_inner_station = Data_clear(temp_inner_station, "SubRouteName_Zh_tw")
                    # if city_name in list(ptx_innercity_bus_station_cityname.keys()):
                    #     print("Station information")                                            
                    #     filename = input_inercity_path+ "_bus_Station.csv"
                    #     if os.path.exists(filename):
                    #         # bat_name = bat_path + "Run_bus_station.bat"
                    #         # Data_time_check(filename, bat_name)
                    #         try:
                    #             innercity_station = pd.read_csv(filename, encoding = "utf8")
                    #         except:
                    #             innercity_station = pd.read_csv(filename, encoding = "ANSI")
                    #         # station_inf = ["PositionLat", "PositionLon", "StationID", "StationAddress"]
                    #         if len(base1_inner_stopofroute.groupby("StationID").size()) == 0 :
                    #                 base1_inner_station = cal_number(base1_inner_stopofroute, innercity_station, "PositionLat", "PositionLon", "StopName_Zh_tw", "StationAddress", inner_city_name)
                    #         else:
                    #             base1_inner_station = cal_number(base1_inner_stopofroute, innercity_station, "PositionLat", "PositionLon", "StationID", "StationAddress", inner_city_name)
                    #         if len(base2_inner_stopofroute.groupby("StationID").size()) == 0 :
                    #             base2_inner_station = cal_number(base2_inner_stopofroute,innercity_station, "PositionLat", "PositionLon", "StopName_Zh_tw", "StationAddress", inner_city_name)
                    #         else:
                    #             base2_inner_station = cal_number(base2_inner_stopofroute,innercity_station, "PositionLat", "PositionLon", "StationID", "StationAddress", inner_city_name)
                    #         temp_inner_station = Comparison_data(base1_inner_station, base2_inner_station,"StationID")
                    #         temp_inner_station = Data_clear(temp_inner_station, "SubRouteName_Zh_tw")
                    #     else:
                    #         print(" 至 PTX 下載此縣市市區公車「站牌點位」資料 ")
                    #         # bat_name = bat_path + "Run_bus_station.bat"
                    #         # Data_time_check(filename, bat_name)
                    # else:
                    #     print(" PTX 無此縣市市區公車「站牌點位」資料，無法提供「站點地址資訊」，若有需要請自行搜尋相關資訊並下載相關資料以進行分析")
                    # ========== Route information ========= #
                    print("Route information")
                    inner_route_inf = ["RouteID","SubRouteName_Zh_tw","FirstBusTime","LastBusTime","HolidayFirstBusTime","HolidayLastBusTime","DepartureStopNameZh","DestinationStopNameZh","CityName"]
                    base1_inner_route = route_information(innercity_route, base1_inner_stopofroute, "SubRouteID", inner_route_inf, 1)
                    base2_inner_route = route_information(innercity_route, base2_inner_stopofroute, "SubRouteID", inner_route_inf, 1)         
                    ### 整併路線資訊
                    temp_inner_route = Comparison_data(base1_inner_route, base2_inner_route, "RouteID")
                    ### 路線平假日起迄時間與
                    temp_inner_route["平日起迄時間"] = temp_inner_route["FirstBusTime"] +"-" + temp_inner_route["LastBusTime"]
                    temp_inner_route["假日起迄時間"] = temp_inner_route["HolidayFirstBusTime"] +"-" + temp_inner_route["HolidayLastBusTime"]
                    temp_inner_route["起迄站名"] = temp_inner_route["DepartureStopNameZh"] +"-" + temp_inner_route["DestinationStopNameZh"] 
                ## 基地一包含其他縣市市區公車 路線與站牌資訊
                elif base1_inner_stopofroute.shape[0] >0 and base2_inner_stopofroute.shape[0] == 0:
                    print("Station information")
                    innercity_station = pd.DataFrame()
                    if len(base1_inner_stopofroute.groupby("StationID").size()) == 0 :
                        base1_inner_station = cal_number(base1_inner_stopofroute, innercity_station, "PositionLat", "PositionLon", "StopName_Zh_tw", "StationAddress")
                    else:
                        base1_inner_station = cal_number(base1_inner_stopofroute, innercity_station, "PositionLat", "PositionLon", "StationID", "StationAddress")
                    temp_inner_station = Data_clear(base1_inner_station, "SubRouteName_Zh_tw")
                    # print(" PTX 無此縣市市區公車「站牌點位」資料，無法提供「站點地址資訊」，若有需要請自行搜尋相關資訊並下載相關資料以進行分析")
                    # ========== Route information ========= #
                    print("Route information")
                    inner_route_inf = ["RouteID","SubRouteName_Zh_tw","FirstBusTime","LastBusTime","HolidayFirstBusTime","HolidayLastBusTime","DepartureStopNameZh","DestinationStopNameZh","CityName"]
                    temp_inner_route = route_information(innercity_route, base1_inner_stopofroute, "SubRouteID", inner_route_inf, 1)        
                    ### 整併路線資訊
                    # temp_inner_route = Comparison_data(base1_inner_route, base2_inner_route, "RouteID")
                    ### 路線平假日起迄時間與
                    temp_inner_route["平日起迄時間"] = temp_inner_route["FirstBusTime"] +"-" + temp_inner_route["LastBusTime"]
                    temp_inner_route["假日起迄時間"] = temp_inner_route["HolidayFirstBusTime"] +"-" + temp_inner_route["HolidayLastBusTime"]
                    temp_inner_route["起迄站名"] = temp_inner_route["DepartureStopNameZh"] +"-" + temp_inner_route["DestinationStopNameZh"] 
                ## 基地二包含其他縣市市區公車 路線與站牌資訊
                elif base1_inner_stopofroute.shape[0] == 0 and base2_inner_stopofroute.shape[0] > 0:
                    print("Station information")
                    innercity_station = pd.DataFrame()
                    if len(base2_inner_stopofroute.groupby("StationID").size()) == 0 :
                        base1_inner_station = cal_number(base2_inner_stopofroute, innercity_station, "PositionLat", "PositionLon", "StopName_Zh_tw", "StationAddress")
                    else:
                        base1_inner_station = cal_number(base2_inner_stopofroute, innercity_station, "PositionLat", "PositionLon", "StationID", "StationAddress")
                    temp_inner_station = Data_clear(base1_inner_station, "SubRouteName_Zh_tw")
                    # print(" PTX 無此縣市市區公車「站牌點位」資料，無法提供「站點地址資訊」，若有需要請自行搜尋相關資訊並下載相關資料以進行分析")
                    # ========== Route information ========= #
                    print("Route information")
                    inner_route_inf = ["RouteID","SubRouteName_Zh_tw","FirstBusTime","LastBusTime","HolidayFirstBusTime","HolidayLastBusTime","DepartureStopNameZh","DestinationStopNameZh","CityName"]
                    temp_inner_route = route_information(innercity_route, base2_inner_stopofroute, "SubRouteID", inner_route_inf, 1)        
                    ### 整併路線資訊
                    # temp_inner_route = Comparison_data(base1_inner_route, base2_inner_route, "RouteID")
                    ### 路線平假日起迄時間與
                    temp_inner_route["平日起迄時間"] = temp_inner_route["FirstBusTime"] +"-" + temp_inner_route["LastBusTime"]
                    temp_inner_route["假日起迄時間"] = temp_inner_route["HolidayFirstBusTime"] +"-" + temp_inner_route["HolidayLastBusTime"]
                    temp_inner_route["起迄站名"] = temp_inner_route["DepartureStopNameZh"] +"-" + temp_inner_route["DestinationStopNameZh"] 
                    
                else:
                    temp_inner_station = pd.DataFrame()
                    temp_inner_route = pd.DataFrame()
            if ("InterCity" in j and modal[j] =="Y"):
                print("========== InterCity Bus ==========")
                # ========== stopofroute ========== #
                print("Stop of Route")
                base1_inter_stopofroute = dist_cal(intercity_stopofroute, base_coordinate[ base_name[0] ], base_range[ base_name[0] ], "PositionLat", "PositionLon")
                base2_inter_stopofroute = dist_cal(intercity_stopofroute, base_coordinate[ base_name[1] ], base_range[ base_name[1] ], "PositionLat", "PositionLon")
                # station_inf = ["StopPosition_PositionLat", "StopPosition_PositionLon", "StationID", "StationAddress"]
                # ========== station information ========== #
                print("Station information")
                intercity_stop = pd.DataFrame()
                base1_inter_station = cal_number(base1_inter_stopofroute, intercity_stop, "PositionLat","PositionLon","StationID","StopAddress")
                base2_inter_station = cal_number(base2_inter_stopofroute, intercity_stop, "PositionLat","PositionLon","StationID","StopAddress")
                temp_inter_station = Comparison_data(base1_inter_station, base2_inter_station, "StationID")
                temp_inter_station = Data_clear(temp_inter_station, "SubRouteName_Zh_tw" )
                # ========== route information ========== #
                print("Route information")
                intercity_route_inf = ["RouteID","SubRouteName_Zh_tw","DepartureStopNameZh","DestinationStopNameZh", "Headsign", "CityName"]
                base1_inter_route = route_information(intercity_route, base1_inter_stopofroute, "SubRouteID", intercity_route_inf, 0)
                base2_inter_route = route_information(intercity_route, base2_inter_stopofroute, "SubRouteID", intercity_route_inf, 0)
                temp_inter_route = Comparison_data(base1_inter_route, base2_inter_route, "RouteID")
                # temp_inter_route["平日起迄時間"] = temp_inter_route["FirstBusTime"] +"-" + temp_inter_route["LastBusTime"]
                # temp_inter_route["假日起迄時間"] = temp_inter_route["HolidayFirstBusTime"] +"-" + temp_inter_route["HolidayLastBusTime"]
                temp_inter_route["起迄站名"] = temp_inter_route["DepartureStopNameZh"] +"-" + temp_inter_route["DestinationStopNameZh"]
            if ("Bike" in j and modal[j] == 'Y'):
                print("========== Bike station ==========")
                base1_bike_station = dist_cal(bike_station, base_coordinate[ base_name[0] ], base_range[ base_name[0] ], "PositionLat", "PositionLon")
                base2_bike_station = dist_cal(bike_station, base_coordinate[ base_name[1] ], base_range[ base_name[1] ], "PositionLat", "PositionLon")
                temp_bike_station = Comparison_data(base1_bike_station, base2_bike_station, "StationID")
                if temp_bike_station.empty:
                    print(" 此基地範圍內無涵蓋任何Ubike站 ")
            if ("Outside" in j and modal[j] == 'Y'):
                print("========== Parking Outsdie ==========")
                # parking_outside = twd97_to_wgs84(parking_outside, "twd97X", "twd97Y")
                base1_parinkg_outside = dist_cal(parking_outside, base_coordinate[ base_name[0] ], base_range[ base_name[0] ], "PositionLat", "PositionLon")
                base2_parinkg_outside = dist_cal(parking_outside, base_coordinate[ base_name[1] ], base_range[ base_name[1] ], "PositionLat", "PositionLon")
                temp_parking_outside = Comparison_data(base1_parinkg_outside, base2_parinkg_outside,"id")
                if temp_parking_outside.empty:
                    print(" 此基地範圍內無涵蓋任何路外停車場 ")
            if ("Roadside" in j and modal[j] == 'Y'):
                print("========== Parking Roadside ==========")
                base1_parinkg_roadside = dist_cal(parking_roadside, base_coordinate[ base_name[0] ], base_range[ base_name[0] ], "PositionLat", "PositionLon")
                base2_parinkg_roadside = dist_cal(parking_roadside, base_coordinate[ base_name[1] ], base_range[ base_name[1] ], "PositionLat", "PositionLon")
                temp_parking_roadside = Comparison_data(base1_parinkg_roadside, base2_parinkg_roadside,"id")
                if temp_parking_roadside.empty:
                    print(" 此基地範圍內無涵蓋任何路邊停車格 ")
            if ("THSR" in j and modal[j] == 'Y'):
                print("========== THSR ==========")
                if thsr.empty != True:
                    base1_thsr = dist_cal(thsr, base_coordinate[ base_name[0]], base_range[ base_name[0]], "PositionLat", "PositionLon")
                    base2_thsr = dist_cal(thsr, base_coordinate[ base_name[1]], base_range[ base_name[1]], "PositionLat", "PositionLon")
                    if base1_thsr.empty == False and base2_thsr.empty == False:
                        temp_thsr_station = Comparison_data(base1_thsr, base2_thsr,"StationID") 
                    elif base1_thsr.empty:
                        temp_thsr_station = base2_thsr
                    elif base2_thsr.empty:
                        temp_thsr_station = base1_thsr
                if temp_thsr_station.empty:
                    # temp_thsr_station = {}
                    # columne = ["PositionLat", "PositionLon", "GeoHash", "LocationCity", "LocationCityCode", "LocationTown",
                    #            "LocationTownCode", "StationUID", "StationID", "StationCode", "Zh_tw", "En", "StationAddress",
                    #            "OperatorID", "UpdateTime", "VersionID"]
                    # for l in columne:
                    #     temp_thsr_station[l] = "-"
                    # temp_thsr_station = pd.DataFrame.from_dict(temp_thsr_station,orient="index").transpose()
                    print(" 此基地範圍內無涵蓋任何高鐵站 ")
            if ("TRTC" in j and modal[j] == 'Y'):
                print("========== TRTC ==========")
                if trtc.empty != True:
                    base1_trtc = dist_cal(trtc, base_coordinate[ base_name[0]], base_range[ base_name[0]], "PositionLat", "PositionLon")
                    base2_trtc = dist_cal(trtc, base_coordinate[ base_name[1]], base_range[ base_name[1]], "PositionLat", "PositionLon")
                    if base1_trtc.empty == False and base2_trtc.empty == False:
                        temp_trtc_station = Comparison_data(base1_trtc, base2_trtc,"StationID") 
                    elif base1_trtc.empty:
                        temp_trtc_station = base2_trtc
                    elif base2_trtc.empty:
                        temp_trtc_station = base1_trtc
                if temp_trtc_station.empty:
                    # temp_trtc_station = {}
                    # columne = ["PositionLat", "PositionLon", "GeoHash", "LocationCity", "LocationCityCode", "LocationTown",
                    #            "LocationTownCode", "StationUID", "StationID", "Zh_tw", "En", "StationAddress", "BikeAllowOnHoliday",
                    #            "SrcUpdateTime", "UpdateTime", "VersionID"]
                    # for l in columne:
                    #     temp_trtc_station[l] = "-"
                    # temp_trtc_station = pd.DataFrame.from_dict(temp_trtc_station,orient="index").transpose()
                    print(" 此基地範圍內無涵蓋任何捷運站 ")
            if ("TRA" in j and modal[j] == 'Y'):
                print("========== TRA ==========")
                if tra.empty != True:
                    base1_tra = dist_cal(tra, base_coordinate[ base_name[0]], base_range[ base_name[0]], "PositionLat", "PositionLon")
                    base2_tra = dist_cal(tra, base_coordinate[ base_name[1]], base_range[ base_name[1]], "PositionLat", "PositionLon")
                    if base1_tra.empty == False and base2_tra.empty == False:
                        temp_tra_station = Comparison_data(base1_tra, base2_tra,"StationID") 
                    elif base1_tra.empty:
                        temp_tra_station = base2_tra
                    elif base2_tra.empty:
                        temp_tra_station = base1_tra
                if temp_tra_station.empty:
                    # temp_tra_station = {}
                    # columne = ["PositionLat", "PositionLon", "GeoHash", "LocationCity", "LocationCityCode", "LocationTown",
                    #            "LocationTownCode", "StationUID", "StationID", "Zh_tw", "En", "StationAddress", "StationPhone",
                    #            "OperatorID", "StationClass", "UpdateTime", "VersionID"]
                    # for l in columne:
                    #     temp_tra_station[l] = "-"
                    # temp_tra_station = pd.DataFrame.from_dict(temp_tra_station,orient="index").transpose()
                    print(" 此基地範圍內無涵蓋任何台鐵站 ")
            if ("TYMC" in j and modal[j] == 'Y'):
                print("========== TYMC ==========")
                if tymc.empty != True:
                    base1_tymc = dist_cal(tymc, base_coordinate[ base_name[0]], base_range[ base_name[0]], "PositionLat", "PositionLon")
                    base2_tymc = dist_cal(tymc, base_coordinate[ base_name[1]], base_range[ base_name[1]], "PositionLat", "PositionLon")
                    if base1_tymc.empty == False and base2_tymc.empty == False:
                        temp_tymc_station = Comparison_data(base1_tymc, base2_tymc,"StationID") 
                    elif base1_tymc.empty:
                        temp_tymc_station = base2_tymc
                    elif base2_tymc.empty:
                        temp_tymc_station = base1_tymc
                if temp_tymc_station.empty:
                    # temp_tymc_station = {}
                    # columne = ["PositionLat", "PositionLon", "GeoHash", "LocationCity", "LocationCityCode", "LocationTown",
                    #            "LocationTownCode", "StationUID", "StationID", "Zh_tw", "En", "StationAddress", "StationPhone",
                    #            "OperatorID", "StationClass", "UpdateTime", "VersionID"]
                    # for l in columne:
                    #     temp_tymc_station[l] = "-"
                    # temp_tymc_station = pd.DataFrame.from_dict(temp_tymc_station,orient="index").transpose()
                    print(" 此基地範圍內無涵蓋任何機場捷運站 ")
        for j in road_type_choice.keys():
            if("SideWalk" in j and road_type_choice[j] == 'Y'):
                print("========== SIDEWALK =========")
                if sidewalk.empty != True:
                    base1_sidewalk = dist_cal_road(sidewalk, base_coordinate[ base_name[0]], base_range[ base_name[0]], "PositionLat", "PositionLon")
                    base2_sidewalk = dist_cal_road(sidewalk, base_coordinate[ base_name[1]], base_range[ base_name[1]], "PositionLat", "PositionLon")
                    if base1_sidewalk.empty == False and base2_sidewalk.empty == False:
                        temp_sidewalk = Comparison_data(base1_sidewalk, base2_sidewalk,"id") 
                    elif base1_sidewalk.empty:
                        temp_sidewalk = base2_sidewalk
                    elif base2_sidewalk.empty:
                        temp_sidewalk = base1_sidewalk
                if temp_sidewalk.empty:
                    # temp_tra_station = {}
                    # columne = ["PositionLat", "PositionLon", "GeoHash", "LocationCity", "LocationCityCode", "LocationTown",
                    #            "LocationTownCode", "StationUID", "StationID", "Zh_tw", "En", "StationAddress", "StationPhone",
                    #            "OperatorID", "StationClass", "UpdateTime", "VersionID"]
                    # for l in columne:
                    #     temp_tra_station[l] = "-"
                    # temp_tra_station = pd.DataFrame.from_dict(temp_tra_station,orient="index").transpose()
                    print(" 此基地範圍內無涵蓋任何道路 ")
            if("Road" in j and road_type_choice[j] == 'Y'):
                print("========== ROAD =========")
                if road.empty != True:
                    # if '縣' in city[i]:
                    #     road_city_name = city[i].split('縣')[0]
                    # elif '市' in city[i]:
                    #     road_city_name = city[i].split('市')[0]
                    base1_road = dist_cal_road(road, base_coordinate[ base_name[0]], base_range[ base_name[0]], "PositionLat", "PositionLon")
                    base2_road = dist_cal_road(road, base_coordinate[ base_name[1]], base_range[ base_name[1]], "PositionLat", "PositionLon")
                    if base1_road.empty == False and base2_road.empty == False:
                        temp_road = Comparison_data(base1_road, base2_road,"ID") 
                    elif base1_road.empty:
                        temp_road = base2_road
                    elif base2_road.empty:
                        temp_road = base1_road
                    ## 道路分類對照表
                    # road_class_relation = {'HW':'國道', 'HU': '國道附屬道路', 'OE':'公務專用道路', '1E':'省道快速公路', '1W':'省道', '1U':'省道共線', '2W':'縣道',
                    #    '2U':'縣道共線', '3W':'鄉(鎮)道路', '3U':'鄉道共線', '4W':'產業道路', '4U':'專用公路/產業道路共線', 'RE':'市區快速道路(含匝道)',
                    #    'RD':'市區道路(路、街)(含圓環)', 'AL':'市區道路(巷、弄)', 'BR':'區塊道路', 'OR':'有路名但無法歸類(含林道)', 'OT':'無路名'}
                    # for a in range(temp_road.shape[0]):
                    #     temp_road.loc[a,'ROADCLASS1'] = road_class_relation[temp_road.loc[a,'ROADCLASS1']]
                if temp_road.empty:
                    # temp_tra_station = {}
                    # columne = ["PositionLat", "PositionLon", "GeoHash", "LocationCity", "LocationCityCode", "LocationTown",
                    #            "LocationTownCode", "StationUID", "StationID", "Zh_tw", "En", "StationAddress", "StationPhone",
                    #            "OperatorID", "StationClass", "UpdateTime", "VersionID"]
                    # for l in columne:
                    #     temp_tra_station[l] = "-"
                    # temp_tra_station = pd.DataFrame.from_dict(temp_tra_station,orient="index").transpose()
                    print(" 此基地範圍內無涵蓋任何道路 ")
    
    # =========== 最後資料合併 ========== #
    if len(base_name) != 0:
        for j in modal.keys():
            if ("InnerCity" in j and modal[j] == 'Y' ):
                if final_inner_station.empty:
                    final_inner_station = temp_inner_station
                else:
                    final_inner_station = pd.concat([final_inner_station,temp_inner_station],axis = 0)
                if final_inner_route.empty:
                    final_inner_route = temp_inner_route
                else:
                    final_inner_route = pd.concat([final_inner_route, temp_inner_route], axis=0)
            if ("InterCity" in j and modal[j] =="Y" ):
                if final_inter_station.empty:
                    final_inter_station = temp_inter_station
                else:
                    final_inter_station = pd.concat([final_inter_station, temp_inter_station] , axis =0)
                if final_inter_route.empty:
                    final_inter_route = temp_inter_route
                else:
                    final_inter_route = pd.concat([final_inter_route, temp_inter_route], axis= 0)
            if ("Bike" in j and modal[j] == 'Y' ):
                if final_bike_station.empty:
                    final_bike_station = temp_bike_station
                else:
                    final_bike_station = pd.concat([final_bike_station, temp_bike_station] , axis= 0)
            if ("Outside" in j and modal[j] == 'Y'):
                if final_parking_outside.empty:
                    final_parking_outside = temp_parking_outside
                else:
                    final_parking_outside = pd.concat([final_parking_outside, temp_parking_outside], axis=0)
            if ("Roadside" in j and modal[j] == 'Y'):
                if final_parking_roadside.empty:
                    final_parking_roadside = temp_parking_roadside
                else:
                    final_parking_roadside = pd.concat([final_parking_roadside, temp_parking_roadside], axis= 0)
            if ("THSR" in j and modal[j] == 'Y'):
                if final_thsr_station.empty:
                    final_thsr_station = temp_thsr_station
                else:
                    final_thsr_station = pd.concat([final_thsr_station, temp_thsr_station], axis= 0)
            if ("TRTC" in j and modal[j] == 'Y'):
                if final_trtc_station.empty:
                    final_trtc_station = temp_trtc_station
                else:
                    final_trtc_station = pd.concat([final_trtc_station, temp_trtc_station], axis= 0)
            if ("TRA" in j and modal[j] == 'Y'):
                if final_tra_station.empty:
                    final_tra_station = temp_tra_station
                else:
                    final_tra_station = pd.concat([final_tra_station, temp_tra_station], axis= 0)
            if ("TYMC" in j and modal[j] == 'Y'):
                if final_tymc_station.empty:
                    final_tymc_station = temp_tymc_station
                else:
                    final_tymc_station = pd.concat([final_tymc_station, temp_tymc_station], axis= 0)
        for j in road_type_choice.keys():
            if("SideWalk" in j and road_type_choice[j] == 'Y'):
                if final_sidewalk.empty:
                    final_sidewalk = temp_sidewalk
                else:
                    final_sidewalk = pd.concat([final_sidewalk, temp_sidewalk], axis= 0)
            if("Road" in j and road_type_choice[j] == 'Y'):
                if final_road.empty:
                    final_road = temp_road
                else:
                    final_road = pd.concat([final_road, temp_road], axis= 0)
    " =========== 基地範圍圓圈繪製 =========== "
    print("========== Base Range Circle Calculate ========== ")
    base_name = temp_base_name
    theta = np.arange(0, 2*np.pi, 0.001)
    circle = pd.DataFrame(columns=['Number', 'PositionLat', 'PositionLon'])
    lat = []
    lon = []
    if len(base_name) == 1:
        # print('Base: ', )
        for angel in theta:
            point = coordinate(base_coordinate[base_name[0]], int(base_range[base_name[0]])+ 5, angel)
            lat.append(point[0])
            lon.append(point[1])
    elif len(base_name) >1:
        for angel in theta:
            point1 = coordinate(base_coordinate[base_name[0]], int(base_range[base_name[0]])+ 5, angel)
            point2 = coordinate(base_coordinate[base_name[1]], int(base_range[base_name[1]])+ 5, angel)
            # earth_dist_1( lat1, long1, lat2, long2)
            # lat.append(point1[0])
            # lon.append(point1[1])
            # lat.append(point2[0])
            # lon.append(point2[1])
            dist = earth_dist_1(float(base_coordinate[base_name[0]][0]), float(base_coordinate[base_name[0]][1]), point2[0], point2[1])
            # 如果基地二範圍點位涵蓋在基地一內，即代表聯集部份，則剔除。
            if (dist > float(base_range[base_name[0]])+ 5 ) or (point2 == point1) :
                lat.append(point2[0])
                lon.append(point2[1])
            dist = earth_dist_1(float(base_coordinate[base_name[1]][0]), float(base_coordinate[base_name[1]][1]), point1[0], point1[1])
            # 如果基地二範圍點位涵蓋在基地一內，即代表聯集部份，則剔除。
            if (dist > float(base_range[base_name[0]])+ 5 ) or (point2 == point1) :
                lat.append(point1[0])
                lon.append(point1[1])
    circle['PositionLat'] = lat
    circle['PositionLon'] = lon
    circle['Number'] = circle.index +1
    " =========== 資料整理 =========="
    """ delet """
    # del temp_inner_route
    # del temp_inner_station
    # del temp_inter_route
    # del temp_inter_station
    # del temp_parking_outside
    # del temp_parking_roadside
    # del temp_bike_station
    # del temp_thsr_station
    # del temp_trtc_station
    # del temp_tra_station
    ## 公車路線排序
    for i in range(final_inner_station.shape[0]):
        temp = sorted(final_inner_station.loc[i,'SubRouteName_Zh_tw'].split('、'))
        final_inner_station.loc[i,'SubRouteName_Zh_tw'] =  "、".join(temp)
    for i in range(final_inter_station.shape[0]):
        temp = sorted(final_inter_station.loc[i,'SubRouteName_Zh_tw'].split('、'))
        for j in range(len(temp) ):
            b = ""
            a = temp[j]
            for k in range(len(list(a))):
                if k == 4:
                    if list(a)[k] in string.ascii_uppercase:
                        b = b + list(a)[k]
                    else:
                        continue
                else:
                    b = b + list(a)[k]
            temp[j] = b
        final_inter_station.loc[i,'SubRouteName_Zh_tw'] =  "、".join(temp)
    "========== reset number =========="
    if final_inner_station.empty != True:
        # final_inner_station = final_inner_station.reset_index()
        final_inner_station = final_inner_station.reset_index().drop(['index'], axis=1)
        final_inner_station['Number'] = final_inner_station.index +1
    if final_inner_route.empty != True:
        final_inner_route = final_inner_route.reset_index().rename(columns = {"index":"Number"})
        final_inner_route['Number'] = final_inner_route.index +1 
    if final_inter_route.empty != True:
        final_inter_route = final_inter_route.reset_index().rename(columns = {"index":"Number"})
        final_inter_route['Number'] = final_inter_route.index +1   
    if final_bike_station.empty != True:
        final_bike_station = final_bike_station.reset_index().rename(columns = {"index":"Number"})
        final_bike_station['Number'] = final_bike_station.index +1   
    if final_parking_outside.empty != True:
        final_parking_outside = final_parking_outside.reset_index().rename(columns = {"index":"Number"})
        final_parking_outside['Number'] = final_parking_outside.index +1
    if final_parking_roadside.empty != True:
        final_parking_roadside = final_parking_roadside.reset_index().rename(columns = {"index":"Number"})
        final_parking_roadside['Number'] = final_parking_roadside.index +1
    if final_thsr_station.empty != True:
        final_thsr_station = final_thsr_station.reset_index().rename(columns = {"index":"Number"})
        final_thsr_station['Number'] = final_thsr_station.index +1
    if final_trtc_station.empty != True:
        final_trtc_station = final_trtc_station.reset_index().rename(columns = {"index":"Number"})
        final_trtc_station['Number'] = final_trtc_station.index +1
    if final_tra_station.empty != True:
        final_tra_station = final_tra_station.reset_index().rename(columns = {"index":"Number"})
        final_tra_station['Number'] = final_tra_station.index +1
    if final_tymc_station.empty != True:
        final_tymc_station = final_tymc_station.reset_index().rename(columns = {"index":"Number"})
        final_tymc_station['Number'] = final_tymc_station.index +1
    if final_sidewalk.empty != True:
        final_sidewalk = final_sidewalk.reset_index().rename(columns = {"index":"Number"})
        final_sidewalk['Number'] = final_sidewalk.index +1
    if final_road.empty != True:
        final_road = final_road.reset_index().rename(columns = {"index":"Number"})
        final_road['Number'] = final_road.index +1 
    ### 道路對照表
    road_class_relation = {'HW':'國道', 'HU': '國道附屬道路', 'OE':'公務專用道路', '1E':'省道快速公路', '1W':'省道', '1U':'省道共線', '2W':'縣道',
        '2U':'縣道共線', '3W':'鄉(鎮)道路', '3U':'鄉道共線', '4W':'產業道路', '4U':'專用公路/產業道路共線', 'RE':'市區快速道路(含匝道)',
        'RD':'市區道路(路、街)(含圓環)', 'AL':'市區道路(巷、弄)', 'BR':'區塊道路', 'OR':'有路名但無法歸類(含林道)', 'OT':'無路名'}
    for a in range(final_road.shape[0]):
        final_road.loc[a,'ROADCLASS1'] = road_class_relation[final_road.loc[a,'ROADCLASS1']]
    
    "========== TIA 資料格式 =========="
    TIA_inner_station = pd.DataFrame(columns = ["編號", "站名", "站牌地址", "公車路線"])
    if final_inner_station.empty != True:
        # print(type(final_inner_station["Number"]))
        # print(final_inner_station.columns)
        TIA_inner_station["編號"] = final_inner_station["Number"]
        TIA_inner_station["站名"] = final_inner_station["StopName_Zh_tw"]
        TIA_inner_station["站牌地址"] = final_inner_station["StationAddress"]
        TIA_inner_station["公車路線"] = final_inner_station["SubRouteName_Zh_tw"]
        TIA_inner_station["路線縣市別"] = final_inner_station["CityName"]
    
    TIA_inner_route = pd.DataFrame(columns=["編號", "路線", "起迄站名", "平日起迄時間", "假日起迄時間"])
    if final_inner_route.empty != True:
        TIA_inner_route["編號"] = final_inner_route["Number"]
        TIA_inner_route["路線"] = final_inner_route["RouteName_Zh_tw"]
        TIA_inner_route["起迄站名"] = final_inner_route["起迄站名"]
        TIA_inner_route["平日起迄時間"] = final_inner_route["平日起迄時間"]
        TIA_inner_route["假日起迄時間"] = final_inner_route["假日起迄時間"]
        TIA_inner_route["路線縣市別"] = final_inner_route["CityName"]
    
    TIA_inter_station = pd.DataFrame(columns= ["編號", "站名", "站牌地址", "公車路線"])
    if final_inter_station.empty != True:
        TIA_inter_station["編號"] = final_inter_station["Number"]
        TIA_inter_station["站名"] = final_inter_station["StopName_Zh_tw"]
        TIA_inter_station["站牌地址"] = final_inter_station["StationAddress"]
        TIA_inter_station["公車路線"] = final_inter_station["SubRouteName_Zh_tw"]
    
    TIA_inter_route = pd.DataFrame(columns = ["編號", "路線", "起迄站名"])
    if final_inter_route.empty != True:
        TIA_inter_route["編號"] = final_inter_route["Number"]
        TIA_inter_route["路線"] = final_inter_route["SubRouteName_Zh_tw"]
        TIA_inter_route["起迄站名"] = final_inter_route["起迄站名"]
        # TIA_inter_route["平日起迄時間"] = final_inter_route["平日起迄時間"]
        # TIA_inter_route["假日起迄時間"] = final_inter_route["假日起迄時間"]
    
    TIA_bike_station = pd.DataFrame(columns= ["編號", "站名", "站點位置", "席位"])
    if final_bike_station.empty != True:
        TIA_bike_station["編號"] = final_bike_station["Number"]
        TIA_bike_station["站名"] = final_bike_station["StationName_Zh_tw"]
        TIA_bike_station["站點位置"] = final_bike_station["StationAddress_Zh_tw"]
        TIA_bike_station["席位"] = final_bike_station["BikesCapacity"]
    
    TIA_parking_outside = pd.DataFrame(columns= ["編號", "停車場名稱", "服務時段", "汽車", "機車"])
    if final_parking_outside.empty != True:
        TIA_parking_outside["編號"] = final_parking_outside["Number"]
        TIA_parking_outside["停車場名稱"] = final_parking_outside["name"]
        TIA_parking_outside["服務時段"] = final_parking_outside["serviceTime"]
        TIA_parking_outside["汽車"] = final_parking_outside["totalcar"]
        TIA_parking_outside["機車"] = final_parking_outside["totalmotor"]
    
    TIA_parking_roadside = pd.DataFrame(columns= ["編號", "車位型態", "收費日期與時段", "收費標準與金額"])
    if final_parking_roadside.empty != True:
        TIA_parking_roadside["編號"] = final_parking_roadside["Number"]
        TIA_parking_roadside["車位型態"] = final_parking_roadside["type"]
        TIA_parking_roadside["收費日期與時段"] = final_parking_roadside["servicetime"]
        TIA_parking_roadside["收費標準與金額"] = final_parking_roadside["pay"]
    
    TIA_thsr_station = pd.DataFrame(columns= ["編號", "站名", "站點位置"])
    if final_thsr_station.empty != True:
        TIA_thsr_station["編號"] = final_thsr_station["Number"]
        TIA_thsr_station["站名"] = final_thsr_station["StationName_Zh_tw"]
        TIA_thsr_station["站點位置"] = final_thsr_station["StationAddress"]
    
    TIA_trtc_station = pd.DataFrame(columns= ["編號", "路線站點", "站名", "站點位置"])
    if final_trtc_station.empty != True:
        TIA_trtc_station["編號"] = final_trtc_station["Number"]
        TIA_trtc_station["路線站點"] = final_trtc_station["StationID"]
        TIA_trtc_station["站名"] = final_trtc_station["StationName_Zh_tw"]
        TIA_trtc_station["站點位置"] = final_trtc_station["StationAddress"]
    
    TIA_tra_station = pd.DataFrame(columns= ["編號", "站名", "站點位置"])
    if final_tra_station.empty != True:
        TIA_tra_station["編號"] = final_tra_station["Number"]
        TIA_tra_station["站名"] = final_tra_station["StationName_Zh_tw"]
        TIA_tra_station["站點位置"] = final_tra_station["StationAddress"]
    TIA_tymc_station = pd.DataFrame(columns= ["編號", "站名", "站點位置"])
    if final_tymc_station.empty != True:
        TIA_tymc_station["編號"] = final_tymc_station["Number"]
        TIA_tymc_station["站名"] = final_tymc_station["StationName_Zh_tw"]
        TIA_tymc_station["站點位置"] = final_tymc_station["StationAddress"]
    TIA_sidewalk = pd.DataFrame(columns =["編號", "市區鄉鎮", "路名", "起訖路段", "總寬度", "行人淨寬"])
    if final_sidewalk.empty != True:
        TIA_sidewalk["編號"] = final_sidewalk["Number"]
        TIA_sidewalk["市區鄉鎮"] = final_sidewalk["city"] + final_sidewalk["area"]
        TIA_sidewalk["路名"] = final_sidewalk["name"]
        TIA_sidewalk["起訖路段"] = final_sidewalk['start'] + "-" + final_sidewalk['end']
        TIA_sidewalk["總寬度"] = final_sidewalk['totalwidth']
        TIA_sidewalk["行人淨寬"] = final_sidewalk['walkwidth']
    TIA_road = pd.DataFrame(columns =["編號", "道路分類", "市區鄉鎮", "路名", "總寬度"])
    if final_road.empty != True:
        TIA_road["編號"] = final_road["Number"]
        TIA_road["道路分類"] = final_road["ROADCLASS1"]
        TIA_road["市區鄉鎮"] = final_road["COUNTY"]
        TIA_road["路名"] = final_road["ROADNAME"]
        TIA_road["總寬度"] = final_road['WIDTH']
    """ =============== output =============== """
    if (output_bool == True):
        print("===================== 結果輸出 =====================")
        base_site_gis = pd.DataFrame.from_dict(base_coordinate,orient="index").reset_index().reset_index()
        # base_site_gis.columns
        base_site_gis = base_site_gis.rename(columns = {"level_0":"Number","index":"Base_name",0:"PositionLat",1:"PositionLon"})
        base_site_gis['Number'] = base_site_gis['Number'] +1
        # base_site_gis['Number'] = list(range(1,len(base_name)+1))
        # base_site_gis = pd.concat([pd.DataFrame.from_dict(base_coordinate,orient="index"),base_site_gis],axis=1)
        # base_site_gis['Base_name'] = base_name
        # base_site_gis['PositionLat'] = list(base_coordinate[base_coordinate.keys() == base_name][0])
        output_path = "G:\\共用雲端硬碟\\台北鼎漢(C_Public)\Public\\014程式開發 TIA\Output Data\\"
        # project_name = 'C000_府中美學'
        if os.path.exists(output_path + "Gis") == False:
            os.makedirs(output_path+"Gis")
        project_output_path = output_path+ "Gis\\" + project_name
        if os.path.exists(project_output_path) == False:
            os.makedirs(project_output_path)
        project_output_path = project_output_path+"\\"    
        " ========== 公共運具與停車資訊 輸出 ========== "
        try:
            final_inner_station.to_csv(project_output_path+"gis_city_bus_stops.csv", encoding="ANSI", index=None)
        except:
            final_inner_station.to_csv(project_output_path+"gis_city_bus_stops.csv", encoding="utf_8_sig", index=None)   
        final_inter_station.to_csv(project_output_path+"gis_intercity_bus_stops.csv", encoding="ANSI", index=None)
        final_bike_station.to_csv(project_output_path+"gis_Ubike_station.csv", encoding="ANSI", index=None)
        final_parking_outside.to_csv(project_output_path+"gis_parking_losts.csv", encoding="ANSI", index=None)
        final_parking_roadside.to_csv(project_output_path+"gis_parking_roadside.csv", encoding="ANSI", index=None)
        final_thsr_station.to_csv(project_output_path+"gis_thsr_station.csv", encoding="ANSI", index=None)
        final_trtc_station.to_csv(project_output_path+"gis_trtc_station.csv", encoding="ANSI", index=None)
        final_tra_station.to_csv(project_output_path+"gis_tra_station.csv", encoding="ANSI", index=None)
        final_tymc_station.to_csv(project_output_path+"gis_tymc_station.csv", encoding="ANSI", index=None)
        final_sidewalk.to_csv(project_output_path+"gis_sidewalk.csv", encoding="ANSI", index=None)
        final_road.to_csv(project_output_path+"gis_road.csv", encoding="ANSI", index=None)
        base_site_gis.to_csv(project_output_path+"gis_base_location.csv", encoding="ANSI", index=None)
        circle.to_csv(project_output_path+"gis_base_study_area.csv", encoding="ANSI", index=None)
        " ========== DATA TO SHAPEFILE ========== "
        shapefile_output_path = output_path+ "Gis\\" + project_name + "\\shapefile"
        if os.path.exists(shapefile_output_path) == False:
            os.makedirs(shapefile_output_path)
        shapefile_output_path = shapefile_output_path+"\\" 
        " ========== 基地位置  ========== "
        if base_site_gis.shape[0] > 0:
            data_to_shapefile_shp.base_station_to_shp(base_site_gis, shapefile_output_path, 'base_location')
        " ========== 基地範圍  ========== "
        if circle.shape[0] > 0:
            data_to_shapefile_shp.base_range_to_shp(circle, shapefile_output_path, 'base_study_area')
        " ========== 市區公車  ========== "
        if final_inner_station.shape[0] > 0:
            data_to_shapefile_shp.bus_station_to_shp(final_inner_station, shapefile_output_path, 'city_bus_stops')
        " ========== 公路客運 ========== "
        if final_inter_station.shape[0] > 0:
            data_to_shapefile_shp.bus_station_to_shp(final_inter_station, shapefile_output_path, 'intercity_bus_stop')
        " ========== Ubike  ========== "
        if final_bike_station.shape[0] > 0:
            data_to_shapefile_shp.ubike_station_to_shp(final_bike_station, shapefile_output_path, 'Ubike_station')
        " ========== 路外停車 ========== "
        if final_parking_outside.shape[0] > 0:
            data_to_shapefile_shp.parking_outside_to_shp(final_parking_outside, shapefile_output_path, 'parking_lots')
        " ========== 路邊停車 ========== "
        if final_parking_roadside.shape[0] > 0:
            data_to_shapefile_shp.parking_roadside_to_shp(final_parking_roadside, shapefile_output_path, 'parking_roadside')
        " ========== 軌道運具 ========== "
        if final_thsr_station.shape[0] > 0:
            data_to_shapefile_shp.track_mode_to_shp(final_thsr_station, shapefile_output_path, 'thsr')
        if final_trtc_station.shape[0] > 0:
            data_to_shapefile_shp.track_mode_to_shp(final_trtc_station, shapefile_output_path, 'trtc')
        if final_tra_station.shape[0] > 0:
            data_to_shapefile_shp.track_mode_to_shp(final_tra_station, shapefile_output_path, 'tra')
        if final_tymc_station.shape[0] > 0:
            data_to_shapefile_shp.track_mode_to_shp(final_tymc_station, shapefile_output_path, 'tymc')
        " ========== 人行道  ========== "
        # final_sidewalk = pd.read_csv(project_output_path+"gis_sidewalk.csv", encoding="ANSI")
        if final_sidewalk.shape[0] > 0:
            data_to_shapefile_shp.sidewalk_to_shp(final_sidewalk, shapefile_output_path, 'sidewalk')
        " ========== 道路 ========== "
        if final_road.shape[0] > 0:
            data_to_shapefile_shp.road_to_shp(final_road, shapefile_output_path, 'road')
        ## 開啟資料夾
        os.startfile(project_output_path)
        ### TIA word 資料輸出
        if os.path.exists(output_path + "TIA") == False:
            os.makedirs(output_path+"TIA")
        project_output_path = output_path+ "TIA\\" + project_name
        if os.path.exists(project_output_path) == False:
            os.makedirs(project_output_path)
        project_output_path = project_output_path+"\\"
        # tia_data_output(project_output_path)
        try:
            TIA_inner_station.to_csv(project_output_path+"TIA_city_bus_stops.csv", encoding="ANSI", index=None)
        except:
            TIA_inner_station.to_csv(project_output_path+"TIA_city_bus_stops.csv", encoding="utf_8_sig", index=None)
        TIA_inner_route.to_csv(project_output_path+"TIA_city_bus_route.csv", encoding="ANSI", index=None)
        TIA_inter_station.to_csv(project_output_path+"TIA_intercity_bus_stops.csv", encoding="ANSI", index=None)
        TIA_inter_route.to_csv(project_output_path+"TIA_intercity_bus_route.csv", encoding="ANSI", index=None)
        TIA_bike_station.to_csv(project_output_path+"TIA_Ubike_station.csv", encoding="ANSI", index=None)
        TIA_parking_outside.to_csv(project_output_path+"TIA_parking_lots.csv", encoding="ANSI", index=None)
        TIA_parking_roadside.to_csv(project_output_path+"TIA_parking_roadside.csv", encoding="ANSI", index=None)
        TIA_thsr_station.to_csv(project_output_path+"TIA_thsr_station.csv", encoding="ANSI", index=None)
        TIA_trtc_station.to_csv(project_output_path+"TIA_trtc_station.csv", encoding="ANSI", index=None)
        TIA_tra_station.to_csv(project_output_path+"TIA_tra_station.csv", encoding="ANSI", index=None)
        TIA_tymc_station.to_csv(project_output_path+"TIA_tymc_station.csv", encoding="ANSI", index=None)
        TIA_sidewalk.to_csv(project_output_path+"TIA_sidewalk.csv", encoding="ANSI", index=None)
        TIA_road.to_csv(project_output_path+"TIA_road.csv", encoding="ANSI", index=None)
        ## 開啟資料夾
        os.startfile(project_output_path)
    else:
        print("===================== 結果不輸出 =====================")
    # 計時結束
    tEnd = time.time()
    # 會自動做近位
    print("It cost %f sec" % (tEnd - tStart))

