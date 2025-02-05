# _*_coding:utf-8 _*_
# !/usr/bin/python3

# Reference:********************************
# encoding: utf-8
# @Time: 2020/12/13 18:49
# @Author: Jackie
# @File: Packet.py
# @Function:  定义数据协议包的类，可进行proto数据包的处理
# @Method:
# Reference:********************************
import json

from Lib.protobuf.json_format import MessageToJson, MessageToDict
from Agame.common.common.config import PROTO_HEAD_SIZE, PROTO_HEAD_FORMAT
from Agame.common.proto import bs_pb2
from Agame.common.proto import cg_pb2
from Agame.common.proto import cs_pb2
# from proto import enums_pb2
# from proto import out_base_pb2
# from proto import ret_pb2
from Lib.protobuf import descriptor as descriptor_mod
from google.protobuf.message import Message

FD = descriptor_mod.FieldDescriptor

import struct


class Packet:
    def __init__(self, person=None):
        """
        协议信息初始化，生成协议对象
        :param person:
        """
        self.messageId = ""
        if hasattr(cs_pb2, self.__class__.__name__):
            self.messageId = eval('cs_pb2.MSG_%s' % self.__class__.__name__)
            self.obj = eval("cs_pb2.%s()" % self.__class__.__name__)
        elif hasattr(cg_pb2, self.__class__.__name__):
            self.messageId = eval('cg_pb2.MSG_%s' % self.__class__.__name__)
            self.obj = eval("cg_pb2.%s()" % self.__class__.__name__)
        elif hasattr(bs_pb2, self.__class__.__name__):
            if self.__class__.__name__ in ['BattleResult', 'BattleReport']:
                self.messageId = 0
            else:
                self.messageId = eval('bs_pb2.MSG_%s' % self.__class__.__name__)
            self.obj = eval("bs_pb2.%s()" % self.__class__.__name__)
        self.person = person
        self.size = 0
        # self.subobj = []

    def __getitem__(self, item):
        """
        取协议包体的属性值
        :param item:
        :return:
        """
        return eval('self.obj.%s' % item)

    def __setitem__(self, key, value):
        """
        设置协议包体属性字段
        :param key:key
        :param value:value
        :return:
        """
        self.obj.__setattr__(key, value)

    def getdatastream(self):
        if hasattr(cs_pb2, self.__class__.__name__):
            self.messageId = eval("cs_pb2.MSG_%s" % self.__class__.__name__)  # 协议id
        elif hasattr(cg_pb2, self.__class__.__name__):
            self.messageId = eval("cg_pb2.MSG_%s" % self.__class__.__name__)  # 协议id
        elif hasattr(bs_pb2, self.__class__.__name__):
            if self.__class__.__name__ in ['BattleResult', 'BattleReport']:
                self.messageId = 0
            else:
                self.messageId = eval("bs_pb2.MSG_%s" % self.__class__.__name__)  # 协议id
        self.size = PROTO_HEAD_SIZE + self.getdatasize()  # 包的长度
        cid = 0
        flag = 0
        senddata = struct.pack(PROTO_HEAD_FORMAT, self.size, self.messageId, self.person['uid'], self.person['sid'],
                               cid, flag)
        senddata += self.obj.SerializeToString()
        return senddata

    def filldatafromstream(self, buf):
        try:
            self.obj.ParseFromString(buf)
        except:
            pass


    def getmediumstream(self):
        return self.obj.SerializeToString()

    def getdatasize(self):
        return self.obj.ByteSize()

    def handle(self):
        pass

    def toJson(self):
        return MessageToJson(self.obj)

    def pb2dict(self, obj):
        """
        protobuf转字典
        :param obj:proto协议对象
        :return: dict 协议信息
        """
        adict = {}
        # if not obj.IsInitialized():
        #     return None
        try:
            for field in obj.DESCRIPTOR.fields:
                if not getattr(obj, field.name):
                    continue
                if not field.label == FD.LABEL_REPEATED:
                    if not field.type == FD.TYPE_MESSAGE:
                        adict[field.name] = getattr(obj, field.name)
                    else:
                        value = self.pb2dict(getattr(obj, field.name))
                        if value:
                            adict[field.name] = value
                else:
                    if field.type == FD.TYPE_MESSAGE and field.name != 'pets' and field.name != 'grid_awards' and field.name != 'reward_counts':
                        adict[field.name] = [self.pb2dict(v) for v in getattr(obj, field.name)]
                        # adict[field.name] = getattr(obj, field.name)
                    else:
                        # adict[field.name] = [v for v in getattr(obj, field.name)]
                        adict[field.name] = getattr(obj, field.name)
            return adict
        except:
            pass
    def toDict(self):
        # adict = MessageToDict(self.obj)
        adict = self.pb2dict(self.obj)
        adict['message'] = self.messageId
        return adict

    def dict2pb(self, adict=None, message=None):
        if message is None:
            message = self.obj
        def parse_list(values, message):
            """parse list to protobuf message"""
            if len(values) >= 0 and isinstance(values[0], dict):  # value needs to be further parsed
                for v in values:
                    cmd = message.add()
                    parse_dict(v, cmd)
            else:  # value can be set
                message.extend(values)

        def parse_dict(values, message):
            for k, v in values.items():
                if isinstance(v, dict):  # value needs to be further parsed
                    parse_dict(v, getattr(message, k))
                elif isinstance(v, list):
                    parse_list(v, getattr(message, k))
                else:  # value can be set
                    try:
                        setattr(message, k, v)
                    except AttributeError:
                        print('try to access invalid attributes %r.%r = %r', message, k, v)
                    except:
                        pass
            return message
        return parse_dict(adict, message)

    def dump(self):
        return self.toDict()


if __name__ == '__main__':
    pass
