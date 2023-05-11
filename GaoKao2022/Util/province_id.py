# -*- coding: utf-8 -*-
import pandas as pd


def province2id(province_name):
    province_dict = {
        '全国': 0, '北京': 1, '天津': 2, '河北': 3, '山西': 4, '内蒙古': 5, '辽宁': 6, '吉林': 7, '黑龙江': 8,
        '上海': 9,'江苏': 10, '浙江': 11, '安徽': 12, '福建': 13, '江西': 14, '山东': 15, '河南': 16,
        '湖北': 17, '湖南': 18, '广东': 19, '海南': 20, '广西': 21, '甘肃': 22, '陕西': 23, '新疆': 24,
        '青海': 25, '宁夏': 26, '重庆': 27, '四川': 28, '贵州': 29, '云南': 30}
    return province_dict[province_name]


def id2province(province_id):
    if pd.isnull(province_id):
        province_id = 0
    if province_id>33 or province_id<0:
        return '未知'
    province_list = ['全国', '北京', '天津', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江', '上海', '江苏', '浙江', '安徽', '福建', '江西',
                     '山东', '河南', '湖北', '湖南', '广东', '海南', '广西', '甘肃', '陕西', '新疆', '青海', '宁夏', '重庆', '四川', '贵州', '云南',
                     '西藏', '台湾', '澳门', '香港']
    return province_list[province_id]


def id2nature(nature_id):
    if nature_id<0 or pd.isnull(nature_id):
        nature_id = 0
    nature_id = int(nature_id)
    nature_list = ["未知", "公办", "民办", "合作办学", "独立学院", "中外合作"]
    return nature_list[nature_id]
