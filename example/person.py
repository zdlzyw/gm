# _*_coding:utf-8 _*_
# !/usr/bin/python3

# Reference:********************************
# encoding: utf-8
# @Time: 2020/12/13 18:50
# @Author: Jackie
# @File: person.py
# @Function:  定义机器人的类，包含各种属性及方法
# @Method:
# Reference:********************************
import time

from Agame.common.common import functions, actions
from Agame.common.common.config import Config
from Agame.common.common.gm_functions import GM_Function


class Person:
    def __init__(self, server, game='Agame', username=None):
        """
        信息初始化
        :param server: 登录哪个服务器，example：'QA1','新QA2',可自行在config中配置服务器参数
        :param game:搞哪个游戏，用于加载配置的，名字在配置Config.Information里要有的
        """
        self.__data = {'uid': 0, 'sid': 0, 'username': str(username),'game': Config.Infomation[game],'area': game, 'socket': None, 'server': server, 'buffer': b'',
                       'heartbeattime': time.time(), 'packet_list': {},
                       'socket_closed': False}
        if self.__data['username'] is None:  # 如果当前无账号则新建账号
            self.__data['username'] = functions.getUserAccount(server)
        self.gm = GM_Function(self)

    def __setitem__(self, key, value):
        """
        把自己当字典,可以直接读写对象的属性 __data[key]=value
        :param key: key
        :param value: value
        :return:
        """
        return self.setData(key, value)

    def setData(self, key, value):
        """
        把自己当字典,可以直接读写对象的属性 __data[key]=value
        :param key: key
        :param value: value
        :return:
        """
        self.__data[key] = value
        return self.getData(key)

    def __getitem__(self, key):
        """
        把自己当字典,可以直接读写对象的属性
        :param key: key
        :return: __data[key]
        """
        return self.__data[key]

    def getData(self, key):
        """
        把自己当字典,可以直接读写对象的属性
        :param key: key
        :return: __data[key]
        """
        if key in self.__data.keys():
            return self.__data[key]
        else:
            return None

    def __str__(self):
        """
        对象的描述，直接返回自己的所有字典值
        :return:
        """
        return str(self.__data)

    def has_a_key(self, key):
        if key in self.__data.keys():
            return True
        return False

    def __getattr__(self, name):
        """
        用于获取actions作为自己的属性，当访问object不存在的属性时会调用该方法
        :param name: 方法名
        :return:
        """

        def errorInfo(*args, **kwargs):
            print("Action: %s not defined" % name)

        if hasattr(actions, name):
            self.__action = eval("actions.{}(self)".format(name))
            func = self.__action.run
        else:
            return errorInfo

        def wrapper(*args, **kwargs):
            _result = func(*args, **kwargs)  # 执行方法
            if len(_result) == 2:
                _result, use_time = _result
            return _result

        return wrapper

    @staticmethod
    def sayBye():
        # 本人恶趣味，不服来干
        print('少年，我看你根骨奇佳，特传授你如来神掌。。。收钱。。。你我缘尽于此，拜拜了您嘞')


if __name__ == "__main__":
    person = Person('东南亚CBT服', 'Jgame东南亚', 'jk101')
    # person = Person('国内提审服', 'Jgame送审', 'jk101')
    person.login()
    # person.gm.general_PeiYang_kuaiJie()
    # person.MSG_C2S_Flush('武将')
    # _result = person['packet_list']["S2C_FlushKnight"][-1]
    # print(_result.toDict())
    # person.MSG_C2S_Flush('宝物')
    # _result = person['packet_list']["S2C_FlushTreasure"][-1]
    # _result = [ for s in _result['treasures'] if s.position > 0]
    # print(_result)
