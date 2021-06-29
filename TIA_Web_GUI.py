# -*- coding: utf-8 -*-
"""
Created on Fri Jun 11 08:56:19 2021

@author: ChuanYu
"""
import flask
import TIA_AUTO_main
from configparser import ConfigParser

def Run_TIA(project_name, base1_name, base1_position, base1_range, base2_name, base2_position, base2_range,
            InnerCity_Bus, InterCity_Bus, Bike, Parking_Outside, Parking_Roadside, THSR, TRA, TRTC, KRTC, TYMC, KLRT, 
            NTDLRT, TRTCMG, sidewalk):        
    "========= 基地資訊 get =========="
    # project_name = project_entry.get()
    # print(project_name)
    base_name = []
    base_coordinate = {}
    base_range = {}
    if base1_name != '':
        base_name.append(base1_name)
        base_coordinate[base1_name] = base1_position.split(', ')
        base_coordinate[base1_name][0] = float(base_coordinate[base1_name][0])
        base_coordinate[base1_name][1] = float(base_coordinate[base1_name][1])
        base_range[base1_name] = float(base1_range)
        # base_across_city[base1_name] = base1_crosscity
        # print(base_across_city)
    if base2_name != '':
        base_name.append(base2_name)
        base_coordinate[base2_name] = base2_position.split(', ')
        base_coordinate[base2_name][0] = float(base_coordinate[base2_name][0])
        base_coordinate[base2_name][1] = float(base_coordinate[base2_name][1])
        base_range[base2_name] = float(base2_range)
        # base_across_city[base2_name] = base2_crosscity
        # print(base_across_city)

    modal = {}   
    modal['InnerCity_Bus'] = InnerCity_Bus
    modal['InterCity_Bus'] = InterCity_Bus
    modal['Bike'] = Bike
    modal['Parking_Outside'] = Parking_Outside
    modal['Parking_Roadside'] = Parking_Roadside
    modal['THSR'] = THSR
    modal['TRA'] = TRA
    modal['TRTC'] = TRTC
    modal['KRTC'] = KRTC
    modal['TYMC'] = TYMC
    modal['KLRT'] = KLRT
    modal['NTDLRT'] = NTDLRT
    modal['TRTCMG'] = TRTCMG

    road_type_choice = {}
    road_type_choice['SideWalk'] = sidewalk
    # project_name = 'C000_府中美學'
    # base_name = ['府中站', '市民廣場']
    # base_coordinate = {'府中站': [25.00853207650213, 121.45942177851646],
    #                     '市民廣場': [25.01234076405166, 121.46571388726626]}
    # base_range = {'府中站': 500, '市民廣場': 500}
    # city['主縣市'] = '新北市'
    # city['跨縣市'] = ''
    # other_city = []
    # base_across_city = {'府中站': 'N', '市民廣場': 'N'}
    
    # project_name = '2.Twe_base(範例檔案)'
    # base_name = ['府中站', '市民廣場']
    # base_coordinate = {'府中站': [25.00853207650213, 121.45942177851646],
    #                     '市民廣場': [25.01234076405166, 121.46571388726626]}
    # base_range = {'府中站': 500, '市民廣場': 500}
    # city['主縣市'] = '新北市'
    # city['跨縣市'] = ''
    # other_city = []
    # base_across_city = {'府中站': 'N', '市民廣場': 'N'}
    
    # project_name = '1.One_base(範例檔案)'
    # base_name = ['府中站']
    # base_coordinate = {'府中站': [25.00853207650213, 121.45942177851646]}
    # base_range = {'府中站': 500}
    # city['主縣市'] = '新北市'
    # city['跨縣市'] = ''
    # other_city = []
    # base_across_city = {'府中站': 'N'}
    
    # project_name = 'C000_西門'
    # base_name = ['捷運西門站']
    # base_coordinate = {'捷運西門站': [25.042163997223607, 121.50829715210693]}
    # base_range = {'捷運西門站': 500}
    # city['主縣市'] = '臺北市'
    # city['跨縣市'] = ''
    # other_city = [] 
    # base_across_city = {'捷運西門站': 'N'}
    
    # project_name = 'C000_test'
    # base_name = ['THI']
    # base_coordinate = {'THI': [25.047795700115252, 121.57754008241648]}
    # base_range = {'THI': 500}
    # city['主縣市'] = '臺北市'
    # city['跨縣市'] = ''
    # other_city = [] 
    # base_across_city = {'THI': 'N'}
    
    # project_name = 'C975_南松山再生'
    # base_name = ['南松山']
    # base_coordinate = {'南松山': [25.047346526888532, 121.56316124176087]}
    # base_range = {'南松山': 900}
    # city['主縣市'] = '臺北市'
    # city['跨縣市'] = ''
    # other_city = [] 
    # base_across_city = {'南松山': 'N'}
    
    # project_name = 'C961'
    # base_name = ['桃園火車站']
    # base_coordinate = {'桃園火車站': [24.989109647446853, 121.31487290669371]}
    # base_range = {'桃園火車站': 1500}
    # city['主縣市'] = '桃園市'
    # city['跨縣市'] = ''
    # other_city = [] 
    # base_across_city = {'桃園火車站': 'N'}
    
    # project_name = 'C000_test'
    # base_name = ['台北車站']
    # base_coordinate = {'台北車站': [25.048077709955578, 121.51694045423902]}
    # base_range = {'台北車站': 1000}
    # city['主縣市'] = '臺北市'
    # city['跨縣市'] = ''
    # other_city = [] 
    # base_across_city = {'台北車站': 'N'}
    
    # project_name = 'Test_THI台中'
    # base_name = ['THI台中']
    # base_coordinate = {'THI台中': [24.162737489416855, 120.6694385060803]}
    # base_range = {'THI台中': 1000}
    # city['主縣市'] = '臺中市'
    # city['跨縣市'] = '彰化縣'
    # other_city = [] 
    # base_across_city = {'THI台中': 'N'}
    TIA_AUTO_main.TIA(project_name, base_name, base_coordinate, base_range, modal, road_type_choice, output_bool = True)

app=flask.Flask(__name__)
@app.route('/',methods=['POST','GET'])
def index():
    if flask.request.method =='POST':
        ## 專案名稱
        project_name = flask.request.form.get('project_name')
        ## 基地一資訊
        base1_name = flask.request.form.get('base1_name')
        base1_position = flask.request.form.get('base1_position')
        base1_range = flask.request.form.get('base1_range')
        ## 基地二資訊
        base2_name = flask.request.form.get('base2_name')
        base2_position = flask.request.form.get('base2_position')
        base2_range = flask.request.form.get('base2_range')
        ## 公共運具資訊
        if flask.request.form.get('InnerCity_Bus') == "on":
            InnerCity_Bus = 'Y'
        else:
            InnerCity_Bus = 'N'
        if flask.request.form.get('InterCity_Bus') == "on":
            InterCity_Bus = 'Y'
        else:
            InterCity_Bus = 'N'
        if flask.request.form.get('Bike') == "on":
            Bike = 'Y'
        else:
            Bike = 'N'
        if flask.request.form.get('Parking_Outside') == "on":
            Parking_Outside = 'Y'
        else:
            Parking_Outside = 'N'
        if flask.request.form.get('Parking_Roadside') == "on":
            Parking_Roadside = 'Y'
        else:
            Parking_Roadside = 'N'
        if flask.request.form.get('THSR') == "on":
            THSR = 'Y'
        else:
            THSR = 'N'
        if flask.request.form.get('TRA') == "on":
            TRA = 'Y'
        else:
            TRA = 'N'
        if flask.request.form.get('TRTC') == "on":
            TRTC = 'Y'
        else:
            TRTC = 'N'
        if flask.request.form.get('TYMC') == "on":
            TYMC = 'Y'
        else:
            TYMC = 'N'
        if flask.request.form.get('KRTC') == "on":
            KRTC = 'Y'
        else:
            KRTC = 'N'
        if flask.request.form.get('KLRT') == "on":
            KLRT = 'Y'
        else:
            KLRT = 'N'
        if flask.request.form.get('NTDLRT') == "on":
            NTDLRT = 'Y'
        else:
            NTDLRT = 'N'
        if flask.request.form.get('TRTCMG') == "on":
            TRTCMG = 'Y'
        else:
            TRTCMG = 'N'
        ## 人行道資訊
        if flask.request.form.get('sidewalk_yes') == "on":
            sidewalk = "Y"
        elif flask.request.form.get('sidewalk_no') == "on":
            sidewalk = "N"
        else:
            sidewalk = "N"
        Run_TIA(project_name, base1_name, base1_position, base1_range, base2_name, base2_position, base2_range,
            InnerCity_Bus, InterCity_Bus, Bike, Parking_Outside, Parking_Roadside, THSR, TRA, TRTC, KRTC, TYMC, KLRT, 
            NTDLRT, TRTCMG, sidewalk)
        return flask.render_template("TIA.html")
    else:
        return flask.render_template("TIA.html")
# 		if flask.request.values['send']=='送出':
# 			return render_template('test.html',name=request.values['user'])
# 	return render_template('test.html',name="")

if __name__ == '__main__':
# 	app.run(debug=True)
    app.run(host="192.168.14.219", port=8000)