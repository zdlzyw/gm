# _*_coding:utf-8 _*_
# !/usr/bin/python3

# Reference:********************************
# encoding: utf-8
# @Time: 2020/12/13 18:52
# @Author: Jackie
# @File: config.py
# @Function: 配置文件
# @Method:
# Reference:********************************
import json
import os

# 相关配置
import requests

PROTO_HEAD_SIZE = 33  # 协议包头长度
PROTO_HEAD_FORMAT = '!IIQQQB'  # 协议包头格式


class Config:
    # 路径配置
    basePath = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))  # 框架路径
    # ActivityConfTest目录
    activity_baseDir = os.path.join(basePath, 'ActivityConfTest')  # 根目录下ActivityConfTest目录
    activity_confDir = os.path.join(activity_baseDir, 'activity_conf')  # activity_conf目录
    activity_config = os.path.join(activity_baseDir, 'config')
    # common目录
    common_baseDir = os.path.join(basePath, 'common')  # 根目录下common目录路径
    common_common = os.path.join(common_baseDir, 'common')  # common所在路径
    common_tab = os.path.join(common_baseDir, "info_tab")  # 配表所在路径
    common_proto = os.path.join(common_baseDir, 'proto')  # proto文件所在路径
    common_lib = os.path.join(common_baseDir, 'Lib')  # 项目内依赖包目录
    common_log = os.path.join(common_baseDir, 'log')  # 日志路径
    # ConfigDataExcels目录
    configData_baseDir = os.path.join(basePath, 'ConfigDataExcels')
    # configData_baseDir = r'E:\svn\ShuZhiDoc'
    # GMTool目录
    GMTool_baseDir = os.path.join(basePath, 'GMTool')
    GMTool_conf = os.path.join(GMTool_baseDir, 'con_dir')
    GMTool_log = os.path.join(GMTool_baseDir, 'log')
    # LoadTest目录
    # loadTest_baseDir = os.path.join(basePath, 'LoadTest')
    # probablityTest目录
    probTest_baseDir = os.path.join(basePath, 'ProbTest')
    probTest_result = os.path.join(probTest_baseDir, 'result')
    # testSupport目录
    # testSupport_baseDir = os.path.join(basePath, 'testSupport')
    # tools目录
    # tools_baseDir = os.path.join(basePath, 'tools')

    # 账号信息相关
    # 新建账号的username相关，一般定义为  prefix+数字，数字从account_startWith递增
    # prefix = 'xhqgl' #'cbbt'  # 账号命名前缀 cb：赤壁之战
    # account_startWith = 50
    prefix = 'cb'  # 'cbbt'  # 账号命名前缀 cb：赤壁之战
    account_startWith = 1

    # 项目相关信息配置
    Agame = {
	    'key': 'EYyadov9mpERnwwceWxflSFYXmoGQUzB',  # Agame登录时没有key
	    'time_offset': 0,  # 服务器时间偏移
	    'area': 'Agame',
    }
    AgameCN = {
	    'key': 'GY2LjuU2YLw11A48EAGDs8QMZzUqs2CV',  # Agame登录时没有key
	    'time_offset': 0,  # 服务器时间偏移
	    'area': 'CN',
    }


    Infomation = {
        "Agame": Agame,
	    "Agame国服": AgameCN
    }

    try:
        requests.get(r'http://www.baidu.com')
        serverlist = 'serverlist.json'
    except Exception:
        serverlist = 'serverlist_内网.json'
    with open(os.path.join(basePath, serverlist), 'r', encoding='utf8') as fp:
        servers = json.load(fp)
    for k, v in Infomation.items():
        try:
            v.update(servers[k])
        except Exception:
            pass


areas = {
	'Agame': 'Agame',
	'CN': 'Agame国服'
}


def get_game_name(area):
    return areas.get(area)


if __name__ == "__main__":
    print(Config.Infomation['Agame'])
    print(Config.Infomation['Agame国服'])