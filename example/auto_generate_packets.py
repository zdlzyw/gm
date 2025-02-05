# _*_coding:utf-8 _*_
# !/usr/bin/python3

# Reference:********************************
# encoding: utf-8
# @Time: 2020/12/9
# @Author: Jakie
# @File: auto_generate_packets.py
# @Function: 执行该脚本可将cs.proto和cg.proto文件中的方法及协议id取出并定义在PACKETS和Defines文件中，
# 每次替换proto文件都需要手动执行一次
# @Method:
# Reference:********************************

import os

from Agame.common.common.config import Config

desFileName = os.path.join(Config.common_common, 'PACKETS.py')
defineFileName = os.path.join(Config.common_common, "Defines.py")

need_operate_list = ['BattleReport', 'BattleResult']


def AutoGeneratePackets():
    proto_file_list = [filename for filename in os.listdir(Config.common_proto) if filename.endswith('.proto')]
    buf = []
    for proto_file in proto_file_list:
        proto_file_path = os.path.join(Config.common_proto, proto_file)
        with open(proto_file_path, 'r', encoding='utf8') as f:
            buf += f.readlines()

    fd = open(desFileName, 'w')
    fd.writelines('# coding:utf8\n\n')
    fd.writelines('from Agame.common.common.Packet import Packet\n')

    fdefine = open(defineFileName, 'w')
    fdefine.writelines("# coding:utf8")
    fdefine.writelines("\n\nPACKET_DEFINE = {\n")

    for line in buf:
        # if 'MSG_' not in line or '=' not in line or 'MSG_ENUM_DEFAULT' in line or '//MSG' in line or '//	MSG' in line or 'MSG_BEGIN' in \
        #         line or 'MSG_NONE' in line or 'MSG_END' in line or "	//" in line or line.count("//") == 2:
        if 'MSG_' not in line or '=' not in line or 'MSG_ENUM_DEFAULT' in line or '//MSG' in line or '//	MSG' in line or 'MSG_BEGIN' in \
                line or 'MSG_NONE' in line or 'MSG_END' in line or line.count("//") == 2:
            continue
        # text = ''
        if '//' in line:
            line, text = line.split('//')
        line = line.replace('MSG_', "")
        line = line.replace(';', "")
        line = line.strip()
        print(line)
        name, value = line.split('=')
        name = name.strip()
        value = value.strip()

        fd.writelines("\n\nclass %s(Packet):\n" % name)
        fd.writelines("    pass\n")

        fdefine.writelines("    '%s': '%s',\n" % (value, name))
    for line in need_operate_list:
        fd.writelines("\n\nclass %s(Packet):\n" % line)
        fd.writelines("    pass\n")
    fd.close()
    fdefine.writelines('}\n')
    fdefine.close()
    print('PACKETS.py 和 Defines.py 生成完毕')


if __name__ == '__main__':
    AutoGeneratePackets()
    print('over')
