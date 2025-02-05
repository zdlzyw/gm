# _*_coding:utf-8 _*_
# !/usr/bin/python3

import base64
import hashlib

# Reference:********************************
# encoding: utf-8
# @Time: 2020/12/13 18:53
# @Author: Jackie
# @File: actions.py
# @Function:  框架重构后的actions定义都在这里，完善后可将老的actions删除
# @Method:
# Reference:********************************
import json
import ssl
import time
import traceback
import urllib.parse
from urllib.parse import urlencode, unquote
import loguru
import websocket
from websocket import create_connection
from Agame.common.common import functions, PACKETS
from Agame.common.common.Defines import PACKET_DEFINE
from Agame.common.common.MyException import *
from Agame.common.common.functions import response_time
from Agame.common.proto import base_pb2, cs_pb2
from Agame.common.proto import out_base_pb2


def form_token(account):
	# 使用 "_" 分隔 account
	account_parts = account.split("_")

	if len(account_parts) != 2:
		return ""  # 如果分隔后不是两个部分，返回空字符串

	# 提取 account_system_id 和 user_id
	account_system_id = account_parts[0]
	user_id = account_parts[1]

	# 创建参数字典
	v = {
		"account_system_id": account_system_id,  # 第一部分
		"osdk_game_id": "2012901",
		"user_id": user_id,  # 第二部分
		"time": str(int(time.time())),  # 当前时间的 Unix 时间戳
		"osdk_user_id": account,  # 原始账户
		"extend": "1|1|1",
		"channel_id": "1",
	}

	token_key = "EYyadov9mpERnwwceWxflSFYXmoGQUzB"

	# 将 v 字典按字母顺序排序
	sorted_keys = sorted(v.keys())
	sorted_v = {k: v[k] for k in sorted_keys}

	# 编码参数并添加 token_key
	result = unquote(urlencode(sorted_v) + token_key)  # URL 编码并添加 token_key
	print(result)
	# 计算 MD5 签名
	tmp = hashlib.md5(result.encode()).hexdigest()
	sorted_v["sign"] = tmp  # 将签名添加到参数中

	# 将参数转换为 JSON
	info = {k: sorted_v[k] for k in sorted_v}

	try:
		data = json.dumps(info).encode()  # 转换为 JSON 字符串并编码为字节
		return base64.b64encode(data).decode()  # 返回 base64 编码的字符串
	except Exception as e:
		print(f"Error: {e}")
		return ""


# 前端生成token
def get_token(input_account, game_secret):
	op_id = 1
	op_game_id = 1
	game_id = 1
	account = input_account
	t = {
		"account_system_id": "1_",
		"osdk_game_id": "196377847",
		"user_id": urllib.parse.quote(account),
		"time": int(time.time() * 1000),
		"osdk_user_id": "1_" + account,
		"extend": f"{op_id}|{game_id}|{op_game_id}",
		"channel_id": "1",
	}
	sorted_t = dict(sorted(t.items()))
	t_str = "&".join([f"{k}={v}" for k, v in sorted_t.items()])
	t_str += game_secret
	t["sign"] = hashlib.md5(t_str.encode("utf-8")).hexdigest()
	osdk_ticket = base64.b64encode(json.dumps(t).encode("utf-8")).decode("utf-8")
	return osdk_ticket


# 登录角色操作
class login:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, token=False):
		"""
        读取配置，连接服务器
        :return:
        """
		if self.person["server"] is not None:
			serverName = self.person["server"]
		else:
			raise NoneException("未选择测试服务器")

		if (
				self.person["game"] is not None and serverName is not None
		):  # 从配置中读取服务器信息并登录
			self.person["server_id"] = self.person["game"][serverName]["sid"]
			self.person["host"] = self.person["game"][serverName]["gateway_domain"]
			self.person["port"] = self.person["game"][serverName]["gateway_port"]
			__result = self.person.connectToServer()
			if __result:
				while True:
					__result = self.person.MSG_C2G_Login(token)
					if __result["ret"] == 1 or __result["ret"] == 3:
						print(self.person["username"], "登陆成功")
						return __result
					elif __result["ret"] == 136:
						loguru.logger.error("服务器未开服")
						return __result
					else:
						loguru.logger.error(
							f"{self.person['username']}, '登录失败，ret={__result['ret']}"
						)
						# print(self.person['username'], '登录失败，ret=', __result['ret'])
						raise NoneException
		else:
			raise NoneException(
				self.person["server"] + "服务器选择错误，配置中没有该服务器，game=",
				self.person["game"],
			)


# websocket连接服务器
class connectToServer:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, max_retries=3, retry_interval=5):
		"""
        连接服务器并增加断线重连机制。

        :param max_retries: 最大重试次数
        :param retry_interval: 每次重试间隔时间（秒）
        :return: True 表示成功连接，抛出异常则连接失败
        """
		if self.person["socket"]:  # 如果当前socket不为空就先断掉连接
			self.person["socket"].close()
			self.person["socket"] = None  # 清空 socket 对象

		# 根据地区使用不同的连接方式
		if self.person["game"]["area"] == "Agame":
			url = f"ws://{self.person['host']}:{self.person['port']}/ws"
		elif self.person["game"]["area"] == "CN":
			url = f"wss://{self.person['host']}:{self.person['port']}/ws"
		else:
			raise ValueError(f"未知地区：{self.person['game']['area']}")

		# 尝试连接服务器
		for attempt in range(1, max_retries + 1):
			try:
				self.person["socket"] = create_connection(url, timeout=20)
				self.person["logintime"] = time.time()
				loguru.logger.info(f"成功连接到服务器: {url}")
				return True  # 连接成功，退出循环
			except Exception as e:
				loguru.logger.error(
					f"第 {attempt} 次连接服务器失败, 错误: {e}, server={url}"
				)
				if attempt < max_retries:
					loguru.logger.info(f"{retry_interval} 秒后重试...")
					time.sleep(retry_interval)  # 等待一段时间再重试
				else:
					loguru.logger.critical(
						f"多次尝试连接失败，服务器可能在维护。server={url}"
					)
					raise NoneException("服务器连接失败，可能在维护", url)


# 账号信息登录
class MSG_C2G_Login:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, token=False):
		# 整理登录包
		packet = PACKETS.C2G_Login(self.person)
		packet["sid"] = self.person["server_id"]
		packet["gateway_ip"] = self.person["host"]
		logininfo_proto = out_base_pb2.LoginInfo()

		Client_proto = base_pb2.Client()
		if token is False:  # 简单判断下是不是token登录
			logininfo_proto.token = get_token(
				self.person["username"], self.person["game"]["key"]
			)  # 正常登录
		else:
			logininfo_proto.token = str(self.person["username"]).strip('\n')  # token登录
		Client_proto.fingerprint_id = "0_0_0"
		# Client_proto.device_name = 'youzu_id'
		Client_proto.language = "zh"
		Client_proto.device_os = "DESKTOP_BROWSER"
		Client_proto.app_version = "0.0.0.0"
		Client_proto.sdk_version = "1.0.0"
		logininfo_proto.version = 9999999
		logininfo_proto.client.CopyFrom(Client_proto)
		login = logininfo_proto.SerializeToString()
		packet["info"] = login
		# 发包登录
		_result = functions.sendpacket(packet)
		if _result:
			if (
					self.person.has_a_key("packet_list")
					and "G2C_Login" in self.person["packet_list"].keys()
			):
				_result = self.person["packet_list"]["G2C_Login"][0]
			else:
				_result = functions.waitforpacket(self.person, "G2C_Login")
			if _result is None:
				self.person.MSG_C2G_Login(token)
			if _result["ret"] == 1:  # 登录成功
				print("账号登录成功", self.person["username"], _result.dump())
				S2C_SyncTime = self.person.MSG_C2S_SyncTime()  # 同步时间
				self.person["server_time"] = S2C_SyncTime["server_time"]
				self.person["uid"] = _result["uid"]
				self.person["sid"] = _result["sid"]
			elif _result["ret"] == 5:  # 重复登录
				raise NoneException(
					"重复登录,创建角色失败", str(self.person["username"])
				)
			elif _result["ret"] == 3:  # 没有角色信息，创建角色
				# print("新账号，开始创建角色")
				loguru.logger.debug("新账号，开始创建角色")
				G2C_Create = self.person.MSG_C2G_Create()  # 发包建角
				if G2C_Create["ret"] == 1:  # 创建成功
					S2C_SyncTime = self.person.MSG_C2S_SyncTime()  # 同步时间
					# # S2C_SyncTime = S2C_SyncTime[0].dump()
					self.person["server_time"] = S2C_SyncTime["server_time"]
					self.person["uid"] = G2C_Create["uid"]
					self.person["sid"] = G2C_Create["sid"]
					msg = (
							"角色创建成功，账号："
							+ self.person["username"]
							+ "，角色名："
							+ str(self.person["username"])
							+ "，UID："
							+ str(self.person["uid"])
							+ ",sever_time："
							+ str(self.person["server_time"])
					)
					loguru.logger.debug(msg)
				else:
					raise GmException("创建角色失败" + str(G2C_Create["uid"]))
			elif _result["ret"] == 2:  # 服务器维护了
				raise GameServerStopException("服务器维护中,创建账号失败")
		return _result


# 创建角色
class MSG_C2G_Create:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2G_Create(self.person)
		packet["sid"] = self.person["server_id"]
		create_info = out_base_pb2.CreateInfo()
		create_info.name = self.person["username"]
		create_info.base_id = 1110011
		createinfo = create_info.SerializeToString()
		packet["info"] = createinfo
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "G2C_Create")
		return _result


# 心跳包
class MSG_C2G_KeepAlive:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2G_KeepAlive(self.person)

		_result = functions.sendpacket(packet)
		if _result:
			print(self.person["uid"], self.person["username"], "KeepAlive")
		else:
			print(
				self.person["uid"],
				self.person["username"],
				"KeepAlive Failed,ret=",
				_result["ret"],
			)
		return _result


# 同步时间
class MSG_C2S_SyncTime:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_SyncTime(self.person)
		packet["client_time"] = int(time.time())

		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_SyncTime")
		return _result


# 离线
class MSG_C2G_Offline:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2G_Offline(self.person)
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(
				self.person, self.__class__.__name__.replace("MSG_C2S", "S2C")
			)
		return _result


# 获取玩家装备信息
class MSG_S2C_OpObject:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_TreasureBox_Open(self.person)
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_TreasureBox_Open")
		return _result


#  发道具
class MSG_C2S_GM_Cmd:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, cmd):
		packet = PACKETS.C2S_GM_Cmd(self.person)
		packet["cmd"] = cmd

		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_GM_Cmd")
		return _result


# 开宝箱协议
class MSG_C2S_TreasureBox_Open:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_TreasureBox_Open(self.person)
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_TreasureBox_Open")
		return _result.dump()


# 刷新基础数据
class MSG_C2S_Flush:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, item="all"):
		"""
        获取角色所有信息
        :param item:获得啥信息，默认所有
        :return:
        """
		flush_item = {
			"佣兵": "character",
			"背饰背包": "back",
			"神器": "artifact",
			"背饰": "user_back",
			"佣兵图鉴": "companion_book",
			"佣兵装备": "companion_equipment",
			"战宠": "pet",
			"阵容": "formation",
			"佣兵装备阵容": "companion_equipment_formation",
		}
		packet = PACKETS.C2S_Flush(self.person)
		if item in flush_item.keys():
			packet[f"{flush_item[item]}"] = True
		else:
			for key_word in flush_item.values():
				packet[f"{key_word}"] = True

		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Flush")
			if _result is not None and _result["ret"] == 1:
				print("Flush成功")
			else:
				if _result is not None:
					print("Flush失败，ret=", _result["ret"])
				print("Flush失败,None")
		return _result.dump()


# 装备系统
class MSG_C2S_Equipment_Wear:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id):
		packet = PACKETS.C2S_Equipment_Wear(self.person)
		packet["id"] = id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Equipment_Wear")
		return _result


# 出售装备
class MSG_C2S_Equipment_Sale:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id):
		packet = PACKETS.C2S_Equipment_Sale(self.person)
		for ids in id:
			packet["ids"].append(ids)
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Equipment_Sale")
		return _result


# 发包工具
class sendAction:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, adict):
		if not isinstance(adict, dict):
			raise ValueException("value error!{} is not dict".format(adict))
		else:
			if "message" in adict.keys():
				messageid = adict.pop("message")
				if str(messageid) in PACKET_DEFINE.keys():
					obj_name = PACKET_DEFINE[str(messageid)]
					if hasattr(PACKETS, obj_name):
						packet = eval("PACKETS.{}(self.person)".format(obj_name))
						if len(adict.values()) > 0:
							packet.dict2pb(adict)
						try:
							_result = functions.sendpacket(packet)
							obj_name = obj_name.replace("C2S", "S2C")
							_result = functions.waitforpacket(self.person, obj_name)
							return _result
						except Exception:
							raise NoneException(
								"send error!packet error,\n{}".format(
									traceback.format_exc()
								)
							)
				else:
					raise NoneException("send error!messageid not found in defines")
			else:
				raise NoneException("send error!! messageid not found in dict")


# 创建公会
class MSG_C2S_Guild_Create:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, prefix, name, _level=1, _verify=1):
		packet = PACKETS.C2S_Guild_Create(self.person)
		# packet.dict2pb({'join_condition': {'level': _level, 'verify': _verify}})
		packet.dict2pb(
			{
				"icons": [10201, 202, 301, 405],
				"prefix": prefix,
				"name": name,
				"welcome": 1,
				"join_condition": {"level": 0, "verify": 0},
				"announce": "ssss",
				"tags": ["潜力新人"],
			}
		)
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Guild_Create")
		return _result.dump()


# 公会搜索
class MSG_C2S_Guild_Search:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, guild_name):
		guild_name = guild_name
		packet = PACKETS.C2S_Guild_Search(self.person)
		packet["guild_name"] = guild_name
		_result = functions.sendpacket(packet)
		print(_result)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Guild_Search")
		return _result.dump()


# 加入公会
class MSG_C2S_Guild_Join:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, guild_id):
		packet = PACKETS.C2S_Guild_Join(self.person)
		packet["guild_id"] = guild_id
		_result = functions.sendpacket(packet)
		print(_result)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Guild_Join")
		return _result.dump()


# 加好友
class MSG_C2S_Friend_Search:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, name):
		packet = PACKETS.C2S_Friend_Search(self.person)
		packet["name"] = name
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Friend_Search")
		return _result.dump()


# 交换布阵信息
class MSG_C2S_Formation_Exchange:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, type, character_id, slot):
		packet = PACKETS.C2S_Formation_Exchange(self.person)
		packet["type"] = type
		packet["character_id"] = character_id
		packet["slot"] = slot
		packet["adjust"] = True
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Formation_Exchange")
			return _result.dump()
		except AttributeError as f:
			pass


# 升级阵位
class MSG_C2S_Formation_Upgrade:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, slot):
		packet = PACKETS.C2S_Formation_Upgrade(self.person)
		packet["slot"] = slot
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Formation_Upgrade")
		return _result.dump()


# 刷新装备信息
class MSG_C2S_Flush_Equip:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, equip=True):
		packet = PACKETS.C2S_Flush(self.person)
		packet["equip"] = equip
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_FlushEquip")
		return _result.dump()


# 披风养成
class MSG_C2S_Cloak_Upgrade:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Cloak_Upgrade(self.person)
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Cloak_Upgrade")
		return _result.dump()


# 佣兵抽卡
class MSG_C2S_Recruit_Roll:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, recruit_id, tp, free, recruit_tp, adv):
		"""
        uint32 recruit_id = 1; //卡池ID
        uint32 tp = 2; //0-单抽 1-十连
        bool free = 3; //本次单抽是否免费
        uint32 recruit_tp = 4; //卡池类型 读enums.RECRUIT_POOL_TYPE
        bool adv = 5; // 是否广告
        """
		packet = PACKETS.C2S_Recruit_Roll(self.person)
		packet["recruit_id"] = recruit_id
		packet["tp"] = tp
		packet["free"] = free
		packet["recruit_tp"] = recruit_tp
		packet["adv"] = adv

		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Recruit_Roll")
		return _result.dump()


# 公会boss-发起挑战
class MSG_C2S_GuildBoss_ChallengeBegin:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, boss_id):
		"""
        uint32 boss_id = 1; //bossId
        """
		packet = PACKETS.C2S_GuildBoss_ChallengeBegin(self.person)
		packet["boss_id"] = boss_id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(
				self.person,
				["S2C_GuildBoss_ChallengeBegin", "S2C_GuildBoss_ChallengeFinish"],
			)
		return _result.dump()


# 好友申请
class MSG_C2S_Friend_Apply:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, uid: int):
		"""
        uint64 uid = 1;
        """
		packet = PACKETS.C2S_Friend_Apply(self.person)
		packet["uid"] = uid
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Friend_Apply")
		return _result.dump()


# 好友赠礼
class MSG_C2S_Friend_GiveGift:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, uid: int):
		"""
        uint64 uid = 1;
        """
		packet = PACKETS.C2S_Friend_GiveGift(self.person)
		packet["uid"] = uid
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Friend_GiveGift")
		return _result.dump()


# 同意好友申请
class MSG_C2S_Friend_Ack:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, uid: int, agree: bool):
		"""
        uint64 uid = 1;
        bool agree = 2;      // 是否同意
        """
		packet = PACKETS.C2S_Friend_Ack(self.person)
		packet["uid"] = uid
		packet["agree"] = agree
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Friend_Ack")
		return _result.dump()


# 触发小游戏
class MSG_C2S_CasualGame_Random:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_CasualGame_Random(self.person)
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_CasualGame_Random")
		return _result.dump()


# 进入小游戏
class MSG_C2S_CasualGame_EnterGame:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, idx):
		"""
        uint32 idx = 1; // 小游戏下标，从0开始
        """
		packet = PACKETS.C2S_CasualGame_EnterGame(self.person)
		packet["idx"] = idx
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_CasualGame_EnterGame")
		return _result.dump()


# 刷新小游戏
class FlushUserCasualGame:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Flush(self.person)
		packet["casual_game"] = True
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_FlushUserCasualGame")
		return _result.dump()


# 结束小游戏
class MSG_C2S_CasualGame_FinishGame:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_CasualGame_FinishGame(self.person)
		# 如果小游戏是红包雨的话,这里需要携带参数
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_CasualGame_FinishGame")
		return _result.dump()


# 刷新小游戏
class FlushUserCasualGame:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Flush(self.person)
		packet["casual_game"] = True
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_FlushUserCasualGame")
		return _result.dump()


# 主角技能树升级
class MSG_C2S_SkillTree_Upgrade:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id):
		"""
        uint32 id = 1; // 目标id
        """
		packet = PACKETS.C2S_SkillTree_Upgrade(self.person)
		packet["id"] = id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_SkillTree_Upgrade")
		# return _result.dump()
		return _result


# 角色刷新
class MSG_C2S_FlushCharacter:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Flush(self.person)
		packet["character"] = True
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_FlushCharacter")
		return _result.dump()


# 阵位升级
class MSG_C2S_Formation_Upgrade:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, slot):
		"""
        uint32 slot = 1;            // 升级 slot id,当前版本只能取2和3
        """
		packet = PACKETS.C2S_Formation_Upgrade(self.person)
		packet["slot"] = slot
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Formation_Upgrade")
		return _result.dump()


# 装备背饰
class MSG_C2S_Back_Equip:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id, lv_exchange):
		"""
        uint64 id = 1; // 要装备的背饰id
        bool lv_exchange = 2; // 等级是否置换
        """
		packet = PACKETS.C2S_Back_Equip(self.person)
		packet["id"] = id
		packet["lv_exchange"] = lv_exchange
		try:
			_result = functions.sendpacket(packet)
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Back_Equip")
			return _result.dump()
		except AttributeError as f:
			pass


# 背饰刷新
class MSG_S2C_FlushBack:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Flush(self.person)
		packet["back"] = True
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_FlushBack")
		return _result.dump()


# 刷新当前用户穿戴的背饰
class MSG_S2C_FlushUserBack:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Flush(self.person)
		packet["user_back"] = True
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_FlushUserBack")
		return _result.dump()


# 背饰刷新
class MSG_S2C_FlushBack:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Flush(self.person)
		packet["back"] = True
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_FlushBack")
		return _result.dump()


# 背饰升级
class MSG_C2S_Back_UpgradeLv:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id, new_lv):
		"""
        uint64 id = 1; // 背饰id
        uint32 new_lv = 2; // 目标等级
        """
		packet = PACKETS.C2S_Back_UpgradeLv(self.person)
		packet["formation_id"] = id
		packet["new_lv"] = new_lv
		try:
			_result = functions.sendpacket(packet)
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Back_UpgradeLv")
			return _result.dump()
		except AttributeError as f:
			print("*" * 30, f)
			pass


# 神器刷新
class MSG_S2C_FlushUserArtifact:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Flush(self.person)
		packet["artifact"] = True
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_FlushUserArtifact")
		return _result.dump()


# 神器升级
class MSG_C2S_Artifact_UpLevel:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id, level):
		"""
        uint32 id = 1; //神器id
        uint32 level = 2; //目标等级
        """
		packet = PACKETS.C2S_Artifact_UpLevel(self.person)
		packet["id"] = id
		packet["level"] = level
		try:
			_result = functions.sendpacket(packet)
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Artifact_UpLevel")
			return _result.dump()
		except AttributeError as e:
			pass


# 神器升星
class MSG_C2S_Artifact_UpStar:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id):
		"""
        uint32 id = 1; //神器id
        """
		packet = PACKETS.C2S_Artifact_UpStar(self.person)
		packet["id"] = id
		try:
			_result = functions.sendpacket(packet)
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Artifact_UpStar")
			return _result.dump()
		except AttributeError as f:
			pass


# 宝箱开启
class MSG_C2S_TreasureBox_BuyUpgradeCnt:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_TreasureBox_BuyUpgradeCnt(self.person)
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(
				self.person, "S2C_TreasureBox_BuyUpgradeCnt"
			)
		return _result.dump()


# 宝箱升级
class MSG_C2S_TreasureBox_Upgrade:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_TreasureBox_Upgrade(self.person)
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_TreasureBox_Upgrade")
		return _result.dump()


# 刷新小游戏
class MSG_S2C_FlushUserCasualGame:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Flush(self.person)
		packet["casual_game"] = True
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_FlushUserCasualGame")
		return _result.dump()


# 迷宫-使用装置
class MSG_C2S_Rogue_UseDevice:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, type, characters):
		"""
                uint32 type = 1; //装置类型（1:复活装置/2:交换装置）
        repeated uint64 characters = 2; //佣兵ID列表
        """
		packet = PACKETS.C2S_Rogue_UseDevice(self.person)
		packet.dict2pb({"type": type, "characters": [characters]})
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Rogue_UseDevice")
		return _result.dump()


# 迷宫-进入格子
class MSG_C2S_Rogue_EnterGrid:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, layer, grid_id):
		"""
                uint32 layer = 1; 层ID
        uint32 grid_id = 2; 格子ID
        """
		packet = PACKETS.C2S_Rogue_EnterGrid(self.person)
		packet["layer"] = layer
		packet["grid_id"] = grid_id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Rogue_EnterGrid")
		return _result.dump()


# 迷宫-选择地图难度
class MSG_C2S_Rogue_SelectDifficulty:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, type, difficulty):
		"""
        uint32 type = 1; //地图类型
        uint32 difficulty = 2; //难度
        """
		packet = PACKETS.C2S_Rogue_SelectDifficulty(self.person)
		packet["type"] = type
		packet["difficulty"] = difficulty
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Rogue_SelectDifficulty")
		return _result.dump()


# 获取指定阵容
class MSG_C2S_Formation_Get:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, type):
		"""
        uint32 type = 1;            // 阵位类型，读enums.FORMATION_TYPE
        """
		packet = PACKETS.C2S_Formation_Get(self.person)
		packet["type"] = type
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Formation_Get")
		return _result.dump()


# //宝箱/掉落/温泉/事件
class MSG_C2S_Rogue_Try:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, option, grid_id):
		"""
                uint32 option = 1; //选项（宝箱：0表示放弃，不可选宝箱传1）
        uint32 grid_id = 2; //格子ID
        """
		packet = PACKETS.C2S_Rogue_Try(self.person)
		packet["option"] = option
		packet["grid_id"] = grid_id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Rogue_Try")
		return _result.dump()


# 领取日常任务奖励
class MSG_C2S_DailyQuest_AwardQuest:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, ids):
		"""
        repeated uint32 ids = 1;
        bool with_active = 2; // 是否同时领取活跃奖励
        """
		packet = PACKETS.C2S_DailyQuest_AwardQuest(self.person)
		packet.dict2pb({"ids": [ids], "with_active": False})
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_DailyQuest_AwardQuest")
		return _result.dump()


# 背饰升星
class MSG_C2S_Back_UpgradeStar:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id, consume_id):
		"""
        uint64 id = 1; // 背饰id
        uint64 consume_id = 2; // 消耗的背饰id
        """
		packet = PACKETS.C2S_Back_UpgradeStar(self.person)
		packet["id"] = id
		packet["consume_id"] = consume_id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Back_UpgradeStar")
		return _result.dump()


# 背饰商店刷新
class MSG_C2S_Back_Refresh:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Back_Refresh(self.person)
		packet.dict2pb({"free": False})
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Back_Refresh")
		return _result.dump()


# 购买背饰
class MSG_C2S_Back_Buy:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, idx):
		packet = PACKETS.C2S_Back_Buy(self.person)
		packet["idx"] = idx
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Back_Buy")
		return _result.dump()


# 设置心愿
class MSG_C2S_Back_SetWish:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, wish_id):
		"""
        uint32 wish_id = 1; // 心愿对应的背饰id
        """
		packet = PACKETS.C2S_Back_SetWish(self.person)
		packet["wish_id"] = wish_id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Back_SetWish")
		return _result.dump()


# 设置头像
class MSG_C2S_Avatar_Set:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id):
		"""
        uint32 id = 1; //头像id
        """
		packet = PACKETS.C2S_Avatar_Set(self.person)
		packet["id"] = id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Avatar_Set")
		return _result.dump()


# 设置头像框
class MSG_C2S_Avatar_Frame_Set:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id):
		"""
        uint32 id = 1; //头像框id
        """
		packet = PACKETS.C2S_Avatar_Frame_Set(self.person)
		packet["id"] = id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Avatar_Frame_Set")
		return _result.dump()


# 七日签到领奖
class MSG_C2S_SevenSign_Award:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id):
		"""
        uint32 id = 1; // 待领取的奖励id
        """
		packet = PACKETS.C2S_SevenSign_Award(self.person)
		packet["id"] = id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_SevenSign_Award")
		return _result.dump()


# 每日签到领奖
class MSG_C2S_DailySign_ObtainReward:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_DailySign_ObtainReward(self.person)
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_DailySign_ObtainReward")
		return _result.dump()


# 推送礼包
class MSG_C2S_PushGift_Buy:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id):
		"""
        uint32 id = 1;
        """
		packet = PACKETS.C2S_PushGift_Buy(self.person)
		packet["id"] = id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_PushGift_Buy")
		return _result.dump()


# 成就领奖
class MSG_C2S_Achievement_Award:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, ids):
		"""
        repeated uint32 ids = 1;    //成就id
        """
		packet = PACKETS.C2S_Achievement_Award(self.person)
		packet.dict2pb({"ids": [ids]})
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Achievement_Award")
		return _result.dump()


# 七日活动-任务领奖
class MSG_C2S_SevenAct_AwardQuest:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, ids):
		"""
        repeated uint32 ids = 1;
        """
		packet = PACKETS.C2S_SevenAct_AwardQuest(self.person)
		packet.dict2pb({"ids": [ids]})
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_SevenAct_AwardQuest")
		return _result.dump()


# 七日活动-积分领奖
class MSG_C2S_SevenAct_AwardPoint:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, ids):
		"""
        repeated uint32 ids = 1;
        """
		packet = PACKETS.C2S_SevenAct_AwardPoint(self.person)
		packet.dict2pb({"ids": [ids]})
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_SevenAct_AwardPoint")
		return _result.dump()


# 背饰分解
class MSG_C2S_Back_Decompose:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id):
		"""
        uint64 id = 1; // 要分解的背饰id
        """
		packet = PACKETS.C2S_Back_Decompose(self.person)
		packet["id"] = id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Back_Decompose")
		return _result.dump()


# 重置背饰
class MSG_C2S_C2S_Back_Reset:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id):
		"""
        uint64 id = 1; // 要重置的背饰id
        """
		packet = PACKETS.C2S_Back_Reset(self.person)
		packet["id"] = id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Back_Reset")
		return _result.dump()


# 背饰上锁
class MSG_C2S_Back_Lock:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id, lock):
		"""
                uint64 id = 1; // 背饰id
        bool lock = 2; // true-上锁 false-下锁
        """
		packet = PACKETS.C2S_Back_Lock(self.person)
		packet["id"] = id
		packet["lock"] = lock
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Back_Lock")
		return _result.dump()


# 每日特惠领取
class MSG_C2S_DailySpecials_Award:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, ids):
		"""
        repeated uint32 ids = 1; //待领取的礼包id列表
        """
		packet = PACKETS.C2S_DailySpecials_Award(self.person)
		packet.dict2pb({"ids": [ids]})
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_DailySpecials_Award")
		return _result.dump()


# 首充领奖
class MSG_C2S_FirstRecharge_Award:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id):
		"""
        uint32 id = 1; //待领取的礼包id
        """
		packet = PACKETS.C2S_FirstRecharge_Award(self.person)
		packet["id"] = id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_FirstRecharge_Award")
		return _result.dump()


# 累充奖励领取
class MSG_C2S_AccumulatedRecharge_Award:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id):
		"""
        uint32 id = 1; //待领取的礼包id
        """
		packet = PACKETS.C2S_AccumulatedRecharge_Award(self.person)
		packet["id"] = id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(
				self.person, "S2C_AccumulatedRecharge_Award"
			)
		return _result.dump()


# 基金奖励领取
class MSG_C2S_Fund_ObtainReward:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, fund_type, id, pay):
		"""
        uint32 fund_type = 1;     // 基金类型
        uint32 id = 2;            // id
        bool pay = 3;             // 是否领取付费奖励
        """
		packet = PACKETS.C2S_Fund_ObtainReward(self.person)
		packet["fund_type"] = fund_type
		packet["id"] = id
		packet["pay"] = pay
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Fund_ObtainReward")
		return _result.dump()


# 领取任务奖励
class MSG_C2S_DailyQuest_AwardQuest:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, ids):
		"""
        repeated uint32 ids = 1;
        bool with_active = 2; // 是否同时领取活跃奖励
        """
		packet = PACKETS.C2S_DailyQuest_AwardQuest(self.person)
		packet.dict2pb({"ids": [ids], "with_active": False})
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_DailyQuest_AwardQuest")
		return _result.dump()


# 领取活跃任务奖励
class MSG_C2S_DailyQuest_AwardActive:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, ids):
		"""
        repeated uint32 ids = 1;
        """
		packet = PACKETS.C2S_DailyQuest_AwardActive(self.person)
		packet.dict2pb({"ids": [ids]})
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_DailyQuest_AwardActive")
		return _result.dump()


# 战令购买等级
class MSG_C2S_BattlePass_BuyLv:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, buy_lv):
		"""
        uint32 buy_lv = 1; //购买几级
        """
		packet = PACKETS.C2S_BattlePass_BuyLv(self.person)
		packet["buy_lv"] = buy_lv
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_BattlePass_BuyLv")
		return _result.dump()


# 战令领取等级奖励
class MSG_C2S_BattlePass_AwardLv:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_BattlePass_AwardLv(self.person)
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_BattlePass_AwardLv")
		return _result.dump()


# 战令领取任务奖励
class MSG_C2S_BattlePass_AwardQuest:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, ids):
		"""
        repeated uint32 ids = 1;
        """
		packet = PACKETS.C2S_BattlePass_AwardQuest(self.person)
		packet.dict2pb({"ids"[ids]})
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_BattlePass_AwardQuest")
		return _result.dump()


# 迷宫-激活科技树
class MSG_C2S_Rogue_ActiveTree:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id):
		"""
        uint32 id = 1; //节点ID
        """
		packet = PACKETS.C2S_Rogue_ActiveTree(self.person)
		packet["id"] = id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Rogue_ActiveTree")
		return _result.dump()


# 迷宫-图鉴奖励领取
class MSG_C2S_Rogue_BookAward:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, type, value):
		"""
                uint32 type = 1; //图鉴类型（4-事件/9-遗物/10-消耗品）
        uint32 value = 2; //事件ID/遗物AdvanceId/消耗品AdvanceId
        """
		packet = PACKETS.C2S_Rogue_BookAward(self.person)
		packet["type"] = type
		packet["value"] = value
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Rogue_BookAward")
		return _result.dump()


# 结算-退出
class MSG_C2S_Rogue_Quit:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Rogue_Quit(self.person)
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Rogue_Quit")
		return _result.dump()


# 迷宫-领取首通奖励
class MSG_C2S_Rogue_GetFirstAward:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id):
		"""
        uint32 id = 1; //迷宫ID
        """
		packet = PACKETS.C2S_Rogue_GetFirstAward(self.person)
		packet["id"] = id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Rogue_GetFirstAward")
		return _result.dump()


# 迷宫-丢弃资源
class MSG_C2S_Rogue_DiscardResource:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, type, ids):
		"""
                uint32 type = 1; //资源类型（4:佣兵/10002:消耗品）
        repeated uint64 ids = 2; //资源ID
        """
		packet = PACKETS.C2S_Rogue_DiscardResource(self.person)
		packet.dict2pb({"type": type, "ids": [ids]})
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Rogue_DiscardResource")
		return _result.dump()


# 宝库-割草游戏
class MSG_C2S_Mow_BeginMow:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, mow_id):
		"""
        uint32 mow_id = 1;
        """
		packet = PACKETS.C2S_Mow_BeginMow(self.person)
		packet["mow_id"] = mow_id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Mow_BeginMow")
		return _result.dump()


# 宝库-结束游戏
class MSG_C2S_Mow_FinishMow:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		"""
        repeated uint32 compelete_targets = 1;      // 完成任务索引
        """
		packet = PACKETS.C2S_Mow_FinishMow(self.person)
		packet.dict2pb({"compelete_targets": [1, 2, 3]})
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Mow_FinishMow")
		return _result.dump()


# 宝库-扫荡
class MSG_C2S_Mow_Sweep:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, mow_id):
		"""
        uint32 mow_id = 1;
        """
		packet = PACKETS.C2S_Mow_Sweep(self.person)
		packet["mow_id"] = mow_id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Mow_Sweep")
		return _result.dump()


# 月卡每日领奖
class MSG_C2S_MonthlyCard_DailyAward:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id):
		"""
        repeated uint32 id = 1; //月卡id
        """
		packet = PACKETS.C2S_MonthlyCard_DailyAward(self.person)
		packet.dict2pb({"id": id})
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_MonthlyCard_DailyAward")
		return _result.dump()


# 图鉴激活
class MSG_C2S_Back_ActiveBook:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, compose_id):
		"""
        repeated uint32 compose_id = 1; // 背饰图鉴ID列表
        """
		packet = PACKETS.C2S_Back_ActiveBook(self.person)
		packet.dict2pb({"compose_id": [compose_id]})
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Back_ActiveBook")
		return _result.dump()


# 自动开箱
class MSG_C2S_TreasureBox_SetAutoOpenCondition:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_TreasureBox_SetAutoOpenCondition(self.person)
		packet.dict2pb(
			{
				"condition": {
					"equip_handle_type": 2,
					"quality": 30,
					"max_open_num": 1,
					"filter_equip_attr": [
						{"equipment_type": 1, "attr": [0, 0]},
						{"equipment_type": 2, "attr": [0, 0]},
						{"equipment_type": 3, "attr": [0, 0]},
						{"equipment_type": 4, "attr": [0, 0]},
						{"equipment_type": 5, "attr": [0, 0]},
						{"equipment_type": 6, "attr": [0, 0]},
						{"equipment_type": 7, "attr": [0, 0]},
						{"equipment_type": 8, "attr": [0, 0]},
						{"equipment_type": 9, "attr": [0, 0]},
						{"equipment_type": 10, "attr": [0, 0]},
						{"equipment_type": 11, "attr": [0, 0]},
					],
					"fight_value_up_stop": 999,
					"upspeed": 100,
					"equip_attr_toggle": True,
				}
			}
		)
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(
				self.person, "S2C_TreasureBox_SetAutoOpenCondition"
			)
		return _result.dump()


# 刷新用户
class MSG_C2S_FlushUser:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Flush(self.person)
		packet["user"] = True
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_FlushUser")
		return _result.dump()


# 佣兵图鉴激活
class MSG_C2S_CompanionBook_UpgradeLv:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, advance_id, new_lv):
		"""
                uint32 advance_id = 1;
        uint32 new_lv = 2; // 目标等级
        """
		packet = PACKETS.C2S_CompanionBook_UpgradeLv(self.person)
		packet["advance_id"] = advance_id
		packet["new_lv"] = new_lv
		try:
			_result = functions.sendpacket(packet)
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_CompanionBook_UpgradeLv"
				)
			return _result.dump()
		except AttributeError as e:
			print(e)
			pass


# 刷新佣兵图鉴
class FlushCharacter:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Flush(self.person)
		packet["character"] = True
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_FlushCharacter")
		return _result.dump()


#
class MSG_C2S_Back_ActiveBook:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, compose_id):
		"""
        repeated uint32 compose_id = 1; // 背饰图鉴ID列表
        """
		packet = PACKETS.C2S_Back_ActiveBook(self.person)
		packet.dict2pb({"compose_id": compose_id})
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Back_ActiveBook")
		return _result.dump()


# 神器缘分激活
class MSG_C2S_Artifact_Compose_Active:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id):
		"""
        uint32 id = 1; //神器缘分id
        """
		packet = PACKETS.C2S_Artifact_Compose_Active(self.person)
		packet["id"] = id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(
				self.person, "S2C_Artifact_Compose_Active"
			)
		return _result.dump()


# 佣兵升级品质
class MSG_C2S_CharacterCompanion_UpgradeQuality:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		"""
                repeated out_base.CharacterCompanionUpgradeQuality upgrade_group = 1;    // 升级组
        bool quick = 2; // 是否快捷飞升
        """
		packet = PACKETS.C2S_CharacterCompanion_UpgradeQuality(self.person)
		packet["id"] = id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(
				self.person, "S2C_CharacterCompanion_UpgradeQuality"
			)
		return _result.dump()


# 爬塔挑战
class MSG_C2S_Tower_ChallengeBegin:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id):
		"""
        uint32 id = 1;              // 挑战层数(关卡)
        """
		packet = PACKETS.C2S_Tower_ChallengeBegin(self.person)
		packet["id"] = id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Tower_ChallengeBegin")
		return _result


# buff选择
class MSG_C2S_Tower_SelectBuff:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, slot_idx, buff_id):
		"""
                uint32 slot_idx = 1;           // buff 槽位索引
        uint32 buff_id = 2;
        """
		packet = PACKETS.C2S_Tower_SelectBuff(self.person)
		packet["slot_idx"] = slot_idx
		packet["buff_id"] = buff_id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Tower_SelectBuff")
		return _result.dump()


# 刷新爬塔数据
class MSG_C2S_FlushUserTower:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Flush(self.person)
		packet["tower"] = True
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_FlushUserTower")
		return _result.dump()


# 神器一键上阵
class MSG_C2S_Artifact_Equip_OneKey:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, ids):
		"""
        repeated uint32 ids = 1; //上阵的神器id列表（对应位置1-4，0表示下阵）
        """
		packet = PACKETS.C2S_Artifact_Equip_OneKey(self.person)
		packet.dict2pb({"ids": ids})
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Artifact_Equip_OneKey")
		return _result.dump()


# 领取额外奖励
class MSG_C2S_Recruit_AwardExtra:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, recruit_id, num, recruit_tp):
		"""
        uint32 recruit_id = 1; //卡池ID
        uint32 num = 2; //领取次数
        uint32 recruit_tp = 3; //卡池类型 读enums.RECRUIT_POOL_TYPE
        """
		packet = PACKETS.C2S_Recruit_AwardExtra(self.person)
		packet["recruit_id"] = recruit_id
		packet["num"] = num
		packet["recruit_tp"] = recruit_tp
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Recruit_AwardExtra")
		return _result.dump()


# 使用道具
class MSG_C2S_Item_Use:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id, num, quiet, rechargeId=0):
		"""
        uint32 id = 1; //道具ID
        uint32 num = 2; //使用数量
        uint32 index = 3; //可选道具用于选择位置 非可选道具没用 从1开始
        string extra = 4; //额外参数，使用代金券要通过它透传充值额外参数，跟正式充值透传的sdk_ex一致。格式如 {"rechargeId":10001}
        bool quiet = 5;     //是否静默使用，true时不推送MSG_S2C_GetAwardNotify
        """
		packet = PACKETS.C2S_Item_Use(self.person)
		packet.dict2pb(
			{
				"id": id,
				"num": num,
				"extra": '{"rechargeId":%s,"param1":0,"param2":0,"select_gift_index":""}'
				         % rechargeId,
			}
		)
		packet["quiet"] = quiet
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Item_Use")
		return _result.dump()


# 地下城进入格子
class MSG_C2S_Rogue_EnterGrid:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, layer, grid_id):
		"""
        uint32 layer = 1; //层ID
        uint32 grid_id = 2; //格子ID
        """
		packet = PACKETS.C2S_Rogue_EnterGrid(self.person)
		packet["layer"] = layer
		packet["grid_id"] = grid_id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Rogue_EnterGrid")
		return _result.dump()


# 地下城迷宫难度选择
class MSG_C2S_Rogue_SelectDifficulty:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, type, difficulty):
		"""
        uint32 type = 1; //地图类型
        uint32 difficulty = 2; //难度
        """
		packet = PACKETS.C2S_Rogue_SelectDifficulty(self.person)
		packet["type"] = type
		packet["difficulty"] = difficulty
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Rogue_SelectDifficulty")
		return _result.dump()


# 地下城迷宫宝箱掉落事件
class MSG_C2S_Rogue_Try:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, option, grid_id):
		"""
        uint32 option = 1; //选项（宝箱：0表示放弃，不可选宝箱传1）
        uint32 grid_id = 2; //格子ID
        """
		packet = PACKETS.C2S_Rogue_Try(self.person)
		packet["option"] = option
		packet["grid_id"] = grid_id
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Rogue_Try")
		return _result.dump()


# 地下城迷宫商店刷新
class MSG_C2S_Rogue_FlushShop:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Rogue_FlushShop(self.person)
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Rogue_FlushShop")
		return _result.dump()


# 竞技场进入玩法
class MSG_C2S_Arena_Enter:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Arena_Enter(self.person)
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Arena_Enter")
		return _result.dump()


# 招募
class MSG_C2S_Rogue_Recruit:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Rogue_Recruit(self.person)
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Rogue_Recruit")
		return _result.dump()


# 招募选择
class MSG_C2S_Rogue_RecruitSelect:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, option):
		packet = PACKETS.C2S_Rogue_RecruitSelect(self.person)
		"""
		uint32 option = 1; //佣兵选项
		"""
		packet["option"] = option
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Rogue_RecruitSelect")
		return _result.dump()


# 获取领地信息
class MSG_C2S_Territory_GetInfo:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Territory_GetInfo(self.person)
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Territory_GetInfo")
		return _result.dump()


# 佣兵装备锻造
class MSG_C2S_CompanionEquip_Forge:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, size):
		"""
        uint32 size = 1; // 锻造数量
        """
		packet = PACKETS.C2S_CompanionEquip_Forge(self.person)
		packet["size"] = size
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_CompanionEquip_Forge")
		return _result.dump()


# 主城升级
class MSG_C2S_Territory_UpgradeMainCity:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Territory_UpgradeMainCity(self.person)
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(
				self.person, "S2C_Territory_UpgradeMainCity"
			)
		return _result.dump()


# 建筑升级
class MSG_C2S_Territory_UpgradeBuilding:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, type):
		"""
        uint32 type = 1; // 建筑类型
        """
		packet = PACKETS.C2S_Territory_UpgradeBuilding(self.person)
		packet["type"] = type
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(
				self.person, "S2C_Territory_UpgradeBuilding"
			)
		return _result.dump()


# 贸易区刷新
class MSG_C2S_Territory_RefreshTradeArea:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, is_adv):
		"""
        bool is_adv = 1;
        """
		packet = PACKETS.C2S_Territory_RefreshTradeArea(self.person)
		packet["is_adv"] = is_adv
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(
				self.person, "S2C_Territory_RefreshTradeArea"
			)
		return _result.dump()


# 主题活动抽奖
class MSG_C2S_ThemeActivity_Roll:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, tp):
		"""
        uint32 tp = 1; // 0-单抽 1-十连
        """
		packet = PACKETS.C2S_ThemeActivity_Roll(self.person)
		packet["tp"] = tp
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_ThemeActivity_Roll")
		return _result.dump()


# 主题文案新建刮刮卡
class MSG_C2S_ThemeActivity_NewLottery:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_ThemeActivity_NewLottery(self.person)
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(
				self.person, "S2C_ThemeActivity_NewLottery"
			)
		return _result.dump()


# 主题活动刮奖
class MSG_C2S_ThemeActivity_Scrape:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, idx):
		"""
        repeated uint32 idx = 1; // 要刮的位置 从0开始
        """
		packet = PACKETS.C2S_ThemeActivity_Scrape(self.person)
		packet.dict2pb({"idx": idx})
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_ThemeActivity_Scrape")
		return _result.dump()


# 磨坊产出
class MSG_C2S_Territory_ObtainBuildingRewardsUseItem:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, type, value, size):
		"""
                uint32 type = 1;            // 建筑类型
        base.Award cost_item = 2;   // 消耗道具
        """
		packet = PACKETS.C2S_Territory_ObtainBuildingRewardsUseItem(self.person)
		Award_proto = base_pb2.Award()
		Award_proto.type = type
		Award_proto.value = value
		Award_proto.size = size
		packet.dict2pb(
			{"type": 5, "cost_item": {"type": type, "value": value, "size": size}}
		)
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(
				self.person, "S2C_Territory_ObtainBuildingRewardsUseItem"
			)
		return _result.dump()


# 输出佣兵装备
class MSG_C2S_FlushCompanionEquipment:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Flush(self.person)
		packet["companion_equipment"] = True
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(
				self.person, "S2C_FlushCompanionEquipment"
			)
		return _result.dump()


# 佣兵装备合成
class MSG_C2S_CompanionEquip_Combine:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, type, quality, equip_ids, op_type):
		"""
                repeated out_base.CompanionEquipmentCombineGroup groups = 1;
        uint32 op_type = 2; // 操作类型（1:合成/2:一键）
        """
		packet = PACKETS.C2S_CompanionEquip_Combine(self.person)
		packet.dict2pb(
			{
				"groups": [{"type": type, "quality": quality, "equip_ids": equip_ids}],
				"op_type": op_type,
			}
		)
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_CompanionEquip_Combine")
		return _result.dump()


# 获取爬塔信息
class MSG_C2S_Tower_GetInfo:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Tower_GetInfo(self.person)
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_Tower_GetInfo")
		return _result.dump()


# 输出好友
class MSG_C2S_FlushUserFriendSystem:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Flush(self.person)
		packet["friend_system"] = True
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(self.person, "S2C_FlushUserFriendSystem")
		return _result.dump()


# 解锁背饰背包格子
class MSG_C2S_Back_ExpandBag:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Back_ExpandBag(self.person)
		try:
			_result = functions.sendpacket(packet)
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Back_ExpandBag")
			return _result
		except AttributeError as f:
			pass


# 竞赛任务奖励
class MSG_C2S_Competition_ObtainQuestAward:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, ids: list, act_id):
		packet = PACKETS.C2S_Competition_ObtainQuestAward(self.person)
		"""
		  uint32 ids = 1;
          uint32 act_id = 2;
		"""
		packet.dict2pb({"ids": ids, "act_id": act_id})
		_result = functions.sendpacket(packet)
		if _result:
			_result = functions.waitforpacket(
				self.person, "S2C_Competition_ObtainQuestAward"
			)
		return _result.dump()


# 战宠招募(买蛋)
class MSG_C2S_Pet_Recruit_Roll:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, cost_type):
		"""
        uint32 cost_type = 1;  //消耗类型（1-使用免费次数 2-使用道具 3-使用钻石 4-使用广告）
        """
		packet = PACKETS.C2S_Pet_Recruit_Roll(self.person)
		packet["cost_type"] = cost_type
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Pet_Recruit_Roll")
			return _result.dump()
		except TypeError as f:
			pass


# 战宠招募选择(开蛋)
class MSG_C2S_Pet_Recruit_Select:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Pet_Recruit_Select(self.person)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Pet_Recruit_Select")
			return _result.dump()
		except TypeError as f:
			pass


# 获取公会gve信息
class MSG_C2S_GuildGVE_GetInfo:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_GuildGVE_GetInfo(self.person)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_GuildGVE_GetInfo")
			return _result.dump()
		except TypeError as f:
			pass


# 宝库领奖
class MSG_C2S_GuildGVE_BoxAward:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, tp, limit, pos):
		"""
        uint32 tp = 1; // 副本阶段
        bool limit = 2; // 是否有限奖
        uint32 pos = 3; // 有限牌的翻牌位置 从0开始
        """
		packet = PACKETS.C2S_GuildGVE_BoxAward(self.person)
		packet["tp"] = tp
		packet["limit"] = limit
		packet["pos"] = pos
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_GuildGVE_BoxAward")
			return _result.dump()
		except TypeError as f:
			pass


# 战宠合成
class MSG_C2S_Pet_UpQuality:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, main_id, sub_id):
		"""
        uint64 main_id = 1; // 待升品宠物id
        uint64 sub_id = 2;  // 材料宠物id
        repeated base.Award addition_items = 3; // 提升概率道具
        """
		packet = PACKETS.C2S_Pet_UpQuality(self.person)
		packet.dict2pb({"main_id": main_id, "sub_id": sub_id, "addition_items": ""})
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Pet_UpQuality")
			return _result.dump()
		except TypeError as f:
			pass


# 获取神兽Boss信息
class MSG_C2S_Secret_GetBossInfo:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Secret_GetBossInfo(self.person)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Secret_GetBossInfo")
			return _result.dump()
		except TypeError as f:
			pass


# 进入神兽boss房间
class MSG_C2S_Secret_EnterBossRoom:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, boss_id):
		packet = PACKETS.C2S_Secret_EnterBossRoom(self.person)
		"""
		uint32 boss_id = 1; //BossId
		"""
		packet["boss_id"] = boss_id
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Secret_EnterBossRoom"
				)
			return _result.dump()
		except TypeError as f:
			pass


# 挑战boss神兽
class MSG_C2S_Secret_ChallengeBossBegin:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, boss_id):
		packet = PACKETS.C2S_Secret_ChallengeBossBegin(self.person)
		"""
		uint32 boss_id = 1;
		"""
		packet["boss_id"] = boss_id
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Secret_ChallengeBossBegin"
				)
			return _result.dump()
		except TypeError as f:
			pass


# 刷新战宠
class MSG_S2C_FlushPet:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Flush(self.person)
		packet["pet"] = True
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_FlushPet")
			return _result
		except TypeError as f:
			pass


# 战宠升级
class MSG_C2S_Pet_UpLevel:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, slot, level):
		"""
                uint32 slot = 1; // 阵位ID(阵位id:1-出战位 2-助战位)
        uint32 level = 2; // 目标等级
        """
		packet = PACKETS.C2S_Pet_UpLevel(self.person)
		packet["slot"] = slot
		packet["level"] = level
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Pet_UpLevel")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 佣兵装备升级
class MSG_C2S_CompanionEquip_Upgrade:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, slot, type, level):
		"""
        uint32 slot = 1; // 对应佣兵阵位（当前版本只能取2和3）
        uint32 type = 2; // 装备类型
        uint32 level = 3; // 目标等级
        """
		packet = PACKETS.C2S_CompanionEquip_Upgrade(self.person)
		packet["slot"] = slot
		packet["type"] = type
		packet["level"] = level
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_CompanionEquip_Upgrade"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


#
# # 战宠装备升级
# class MSG_C2S_CompanionEquip_Upgrade:
# 	def __init__(self, person):
# 		self.person = person
#
# 	@response_time
# 	def run(self, pet_slot, equip_slot):
# 		'''
# 		  uint32 pet_slot = 1; // 阵位ID(阵位id:1-出战位 2-助战位)
# 		  uint32 equip_slot = 2; // 装备槽位
# 		  repeated uint64 ids = 3; // 消耗装备列表
# 		  map<uint32, uint32> items = 4; // 消耗道具列表
# 		'''
# 		packet = PACKETS.C2S_CompanionEquip_Upgrade(self.person)
# 		packet.dict2pb({'pet_slot': pet_slot, 'equip_slot': equip_slot, 'items': {140: 500}})
# 		_result = functions.sendpacket(packet)
# 		try:
# 			if _result:
# 				_result = functions.waitforpacket(self.person, 'S2C_CompanionEquip_Upgrade')
# 			return _result.dump()
# 		except TypeError as f:
# 			print('报错啦,报错信息', f)
# 			pass


# 碎片合成
class MSG_C2S_Fragment_Compose:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id, num):
		"""
        uint32 id = 1; //碎片ID
        uint32 num = 2; //碎片数量
        uint32 compose_num = 3; //合成数量，支持批量合成
        repeated base.Award replace = 4; //碎片不足时的替代品，如佣兵万能碎片
        bool quiet = 5; //是否静默使用，true时不推送MSG_S2C_GetAwardNotify
        """
		packet = PACKETS.C2S_Fragment_Compose(self.person)
		compose = cs_pb2.C2S_Fragment_Compose()
		compose.id = id
		compose.num = num
		compose.compose_num = 1
		compose.quiet = True
		packet.obj = compose
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Fragment_Compose")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 佣兵装备调整阵容
class MSG_C2S_CompanionEquip_ChangeFormation:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, slot, equip_id: list):
		packet = PACKETS.C2S_CompanionEquip_ChangeFormation(self.person)
		packet.dict2pb({"formations": [{"slot": slot, "positions": equip_id}]})
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_CompanionEquip_ChangeFormation"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 战宠缘分激活
class MSG_C2S_Pet_Compose_Active:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, ids: list):
		packet = PACKETS.C2S_Pet_Compose_Active(self.person)
		packet.dict2pb({"ids": ids})
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Pet_Compose_Active")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 战宠装备升级
class MSG_C2S_Pet_Equipment_UpLevel:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, pet_slot, equip_slot):
		"""
        uint32 pet_slot = 1; // 阵位ID(阵位id:1-出战位 2-助战位)
        uint32 equip_slot = 2; // 装备槽位
        repeated uint64 ids = 3; // 消耗装备列表
        map<uint32, uint32> items = 4; // 消耗道具列表
        """
		packet = PACKETS.C2S_Pet_Equipment_UpLevel(self.person)
		pet_equipment_uplevel = cs_pb2.C2S_Pet_Equipment_UpLevel()
		pet_equipment_uplevel.pet_slot = pet_slot
		pet_equipment_uplevel.equip_slot = equip_slot
		pet_equipment_uplevel.ids.extend(0)
		pet_equipment_uplevel.items[140] = 300
		packet.obj = pet_equipment_uplevel
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Pet_Equipment_UpLevel"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 公会gve-怪物挑战
class MSG_C2S_GuildGVE_ChallengeBegin:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, stage_id, difficult):
		"""
        uint32 stage_id = 1; // 挑战关卡 id
        uint32 difficult = 2; // 难度
        """
		packet = PACKETS.C2S_GuildGVE_ChallengeBegin(self.person)
		packet["stage_id"] = stage_id
		packet["difficult"] = difficult
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_GuildGVE_ChallengeBegin"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 公会每日签到
class MSG_C2S_Guild_DailySign:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Guild_DailySign(self.person)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Guild_DailySign")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 发起公会加成
class MSG_C2S_GuildGVE_StartAddition:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_GuildGVE_StartAddition(self.person)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_GuildGVE_StartAddition"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 公会-赠送挑战次数
class MSG_C2S_GuildGVE_Give:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, target):
		packet = PACKETS.C2S_GuildGVE_Give(self.person)
		packet["target"] = target
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_GuildGVE_Give")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 领地-佣兵驻守
class MSG_C2S_Territory_CompanionEquip:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, type, idx, companion_id):
		"""
        uint32 type = 1; // 建筑类型
        uint32 idx = 2; // 驻守位置 从0开始
        uint64 companion_id = 3; // 佣兵ID 0代表下阵
        """
		packet = PACKETS.C2S_Territory_CompanionEquip(self.person)
		packet["type"] = type
		packet["idx"] = idx
		packet["companion_id"] = companion_id
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Territory_CompanionEquip"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 浮空兽岛-挑战神兽
class MSG_C2S_Secret_ChallengeBegin:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, chapter_id, stage_id):
		"""
        uint32 chapter_id = 1; //章节ID
        uint32 stage_id = 2; //关卡ID
        """
		packet = PACKETS.C2S_Secret_ChallengeBegin(self.person)
		packet["chapter_id"] = chapter_id
		packet["stage_id"] = stage_id
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Secret_ChallengeBegin"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 巅峰竞技场-刷新匹配
class MSG_C2S_PeakArena_RefreshMatch:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, refresh_type):
		"""
        uint32 refresh_type = 1;      // 刷新类型,0:表示默认优先扣除免费次数然后付费刷新,1:表示广告刷新,2:表示进入界面修改当前名次上的玩家
        """
		packet = PACKETS.C2S_PeakArena_RefreshMatch(self.person)
		packet["refresh_type"] = refresh_type
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_PeakArena_RefreshMatch"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 巅峰竞技场-挑战
class MSG_C2S_PeakArena_ChallengeBegin:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, uid, battle_reason, id):
		"""
        uint64 uid = 1;             // 挑战玩家 uid
        uint32 battle_reason = 2;   // 挑战原因,0:表示正常挑战匹配到的玩家,1:表示复仇挑战玩家
        uint32 id = 3;              // 复仇需要传唯一 id
        """
		packet = PACKETS.C2S_PeakArena_ChallengeBegin(self.person)
		packet["uid"] = uid
		packet["battle_reason"] = battle_reason
		packet["id"] = id
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_PeakArena_ChallengeBegin"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 领地-征服封城
class MSG_C2S_TerritoryLord_CaptureChallengeBegin:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, pos, vassal_user_id, lord_user_id, confront_state):
		"""
        uint32 pos = 1;
        uint64 vassal_user_id = 2; //要征服的封臣id
        uint64 lord_user_id = 3; //对方所属的领主id
        uint32 confront_state = 4; //要征服的封臣的迎战状态(1: 领主迎战，2: 自身迎战)
        """
		packet = PACKETS.C2S_TerritoryLord_CaptureChallengeBegin(self.person)
		packet["pos"] = pos
		packet["vassal_user_id"] = vassal_user_id
		packet["lord_user_id"] = lord_user_id
		packet["confront_state"] = confront_state
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_TerritoryLord_CaptureChallengeBegin"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 领地-领取事件奖励
class MSG_C2S_Territory_ObtainEventRewards:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id, option_index):
		"""
        uint32 id = 1;            // 事件 id
        uint32 option_index = 2;  // 选项 index 从 1 开始
        """
		packet = PACKETS.C2S_Territory_ObtainEventRewards(self.person)
		packet["id"] = id
		packet["option_index"] = option_index
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Territory_ObtainEventRewards"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 节庆活动抽卡
class MSG_C2S_FestivalActivity_StageChallenge:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, stage_id):
		"""
        uint32 stage_id = 1; // 关卡id
        """
		packet = PACKETS.C2S_FestivalActivity_StageChallenge(self.person)
		packet["stage_id"] = stage_id
		packet["num"] = 1
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_FestivalActivity_StageChallenge"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 节庆活动抽卡获取活动信息
class MSG_C2S_FestivalActivity_GetInfo:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_FestivalActivity_GetInfo(self.person)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_FestivalActivity_GetInfo"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 节庆活动进入下一关
class MSG_C2S_FestivalActivity_StageEnd:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, stage_id):
		"""
        uint32 stage_id = 1; // 关卡id
        """
		packet = PACKETS.C2S_FestivalActivity_StageEnd(self.person)
		packet["stage_id"] = stage_id
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_FestivalActivity_StageEnd"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 节庆活动领取任务奖励
class MSG_C2S_FestivalActivity_QuestAward:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, quest_ids):
		"""
        repeated uint32 quest_ids = 1; // 任务id
        """
		packet = PACKETS.C2S_FestivalActivity_QuestAward(self.person)
		packet.dict2pb({"quest_ids": [quest_ids]})
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_FestivalActivity_QuestAward"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 道具购买
class MSG_C2S_ScoreShop_Buy:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id, cnt):
		"""
        uint64 id = 1;  // 商品ID和num的合并字段
        uint32 cnt = 2; // 购买次数
        """
		packet = PACKETS.C2S_ScoreShop_Buy(self.person)
		packet["id"] = id
		packet["cnt"] = cnt
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_ScoreShop_Buy")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 公会发红包
class MSG_C2S_Guild_RedPacket_Send:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, base_id):
		"""
        uint32 base_id = 1;  // 红包id
        """
		packet = PACKETS.C2S_Guild_RedPacket_Send(self.person)
		packet["base_id"] = base_id
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Guild_RedPacket_Send"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 公会开红包
class MSG_C2S_Guild_RedPacket_Open:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id, num):
		"""
        map<uint32, uint32> ids = 1;  // 红包id列表（key：baseid value：数量）
        """
		packet = PACKETS.C2S_Guild_RedPacket_Open(self.person)
		RedPacket = cs_pb2.C2S_Guild_RedPacket_Open()
		RedPacket.ids[id] = num
		packet.obj = RedPacket
		print(packet.obj)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Guild_RedPacket_Open"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 钓鱼
class MSG_C2S_WishPool_Fishing:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_WishPool_Fishing(self.person)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_WishPool_Fishing")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 钓鱼获取详情
class MSG_C2S_WishPool_GetInfo:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_WishPool_GetInfo(self.person)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_WishPool_GetInfo")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 领取钓鱼每日奖励
class MSG_C2S_WishPool_DailyAward:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, pool_type):
		packet = PACKETS.C2S_WishPool_DailyAward(self.person)
		packet["pool_type"] = pool_type
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_WishPool_DailyAward"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 公会红包拾取
class MSG_C2S_Guild_RedPacket_Pick:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id):
		"""
        uint64 id = 1;  // 红包唯一id
        """
		packet = PACKETS.C2S_Guild_RedPacket_Pick(self.person)
		packet["id"] = id
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Guild_RedPacket_Pick"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 获取公会红包信息
class MSG_C2S_Guild_RedPacket_GetInfo:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Guild_RedPacket_GetInfo(self.person)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Guild_RedPacket_GetInfo"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 神器缘分升级
class MSG_C2S_Artifact_Compose_UpLevel:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id):
		# uint32
		# id = 1; // 神器缘分id
		packet = PACKETS.C2S_Artifact_Compose_UpLevel(self.person)
		packet["id"] = id
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Artifact_Compose_UpLevel"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 永恒战场进入活动
class MSG_C2S_Slg_Enter:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Slg_Enter(self.person)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Slg_Enter")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 永恒战场获取地图显示数据
class MSG_C2S_Slg_GetMapShowData:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, x, y):
		"""
        base.Point center = 1;  // 中心点
        """
		packet = PACKETS.C2S_Slg_GetMapShowData(self.person)
		packet.dict2pb({"center": {"x": x, "y": y}})
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Slg_GetMapShowData")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 永恒战场驻扎主城
class MSG_C2S_Slg_StationMainCity:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, tp, pos, id):
		"""
        uint32 tp  = 1;  // 驻扎胚子类型
        uint32 pos = 2;
        uint64 id  = 3;
        """
		packet = PACKETS.C2S_Slg_StationMainCity(self.person)
		packet["tp"] = tp
		packet["pos"] = pos
		packet["id"] = id
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Slg_StationMainCity"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 永恒战场攻城车出征
class MSG_C2S_Slg_CityMarch:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, move_path, city_move_path):
		"""
        uint32 city_id                = 1;  // 城池id
        base.SlgUserTeam team         = 2;  // 攻击队伍阵容及兵种兵力
        repeated base.Point move_path = 3;  // 行军路径
        int64 supply_troop            = 4;  // 补给或返还兵力
        """
		data = self.person.gm.flush_yongbing()
		for item in data:
			item["id"] = item.pop("character_id")
		packet = PACKETS.C2S_Slg_CityMarch(self.person)
		enter_info = self.person.MSG_C2S_Slg_Enter()
		tp = 0
		if enter_info.get("teams"):
			teams = enter_info["teams"]
			for troop in teams:
				if troop.get("troops"):
					supply_troop = troop["troops"]
					tp = supply_troop
			packet.dict2pb(
				{
					"city_id": 202,
					"teams": [teams[0]],
					"move_path": move_path,
					"supply_troop": tp,
					"city_move_path": city_move_path,
					"team_index": 1,
					"march_tp": 0,
				}
			)
		else:
			packet.dict2pb(
				{
					"city_id": 202,
					"teams": [
						{
							"index": 1,
							"troop_type": 1,
							"troop_level": 16,
							"troops": 1000,
							"characters": data[:3],
						}
					],
					"move_path": move_path,
					"supply_troop": 1000,
					"city_move_path": city_move_path,
					"team_index": 1,
					"march_tp": 0,
				}
			)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Slg_CityMarch")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 永恒战场组队boss创建队伍
class MSG_C2S_Slg_BossCreateTeam:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, boss_id, move_path):
		"""
        uint32 boss_id                = 1;  // 要挑战的bossId
        base.SlgUserTeam user_team    = 2;  // 攻击队伍阵容及兵种兵力
        repeated base.Point move_path = 3;  // 行军路径
        int64 supply_troop            = 4;  // 补给或返还兵力
        """
		packet = PACKETS.C2S_Slg_BossCreateTeam(self.person)
		packet.dict2pb(
			{
				"boss_id": boss_id,
				"move_path": move_path,
				"supply_troop": 750,
				"team_index": 1,
				"teams": [
					{
						"index": 1,
						"troop_type": 1,
						"troop_level": 1,
						"troops": 750,
						"uid": self.person["uid"],
						"characters": self.person.gm.flush_yongbing()[:3],
						"supply_troop": 750,
						"authority": 1,
					}
				],
			}
		)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Slg_BossCreateTeam")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 永恒战场获取排行榜
class MSG_C2S_Slg_GetRank:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id, city_id, limit):
		"""
        uint32 id      = 1;  // 1-个人榜 2-公会内部榜 3-公会榜 4-最终龙堡榜
        uint32 city_id = 2;
        uint32 limit   = 3;  // 0-全部拉取 非0-拉取前N个
        """
		packet = PACKETS.C2S_Slg_GetRank(self.person)
		packet["id"] = id
		packet["city_id"] = city_id
		packet["limit"] = limit
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Slg_GetRank")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 永恒战场建筑升级
class MSG_C2S_Slg_UpgradeBarrack:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, tp, level):
		"""
        uint32 tp    = 1;  // 要更新哪个类型的兵营
        uint32 level = 2;
        """
		packet = PACKETS.C2S_Slg_UpgradeBarrack(self.person)
		packet["tp"] = tp
		packet["level"] = level
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Slg_UpgradeBarrack")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 永恒战场主营升级
class MSG_C2S_Slg_UpgradeMainCity:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, level):
		"""
        uint32 level = 1;
        """
		packet = PACKETS.C2S_Slg_UpgradeMainCity(self.person)
		packet["level"] = level
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Slg_UpgradeMainCity"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 永恒战场补给站奖励领取
class MSG_C2S_Slg_ObtainSupplyReward:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Slg_ObtainSupplyReward(self.person)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Slg_ObtainSupplyReward"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 永恒战场使用补给令
class MSG_C2S_Slg_UseSupplyToken:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Slg_UseSupplyToken(self.person)
		packet.dict2pb({"item_id": 233, "size": 1000})
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Slg_UseSupplyToken")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 永恒战场组队boss,队伍列表
class MSG_C2S_Slg_BossTeamList:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, boss_id):
		packet = PACKETS.C2S_Slg_BossTeamList(self.person)
		# uint32 boss_id = 1;
		packet["boss_id"] = boss_id
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Slg_BossTeamList")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 永恒战场迁城
class MSG_C2S_Slg_MoveHome:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, path):
		packet = PACKETS.C2S_Slg_MoveHome(self.person)
		packet.dict2pb({"path": path})
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Slg_MoveHome")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 永恒战场组队boss离开队伍
class MSG_C2S_Slg_BossLeave:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, team_id, is_dismiss):
		packet = PACKETS.C2S_Slg_BossLeave(self.person)
		"""
		  uint64 team_id  = 1;
          bool is_dismiss = 2;  // 是否解散
		"""
		packet["team_id"] = team_id
		packet["is_dismiss"] = is_dismiss
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Slg_BossLeave")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 永恒战场打野怪
class MSG_C2S_Slg_PVEMarch:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, monster_id, move_path):
		packet = PACKETS.C2S_Slg_PVEMarch(self.person)
		"""
	  uint32 monster_id               = 1;  // 怪物id
	  repeated base.SlgUserTeam teams = 2;  // 攻击队伍阵容及兵种兵力
	  repeated base.Point move_path   = 3;  // 行军路径
	  int64 supply_troop              = 4;  // 补给或返还兵力
		"""
		packet.dict2pb(
			{
				"monster_id": monster_id,
				"teams": [
					{
						"index": 1,
						"troop_type": 1,
						"troop_level": 1,
						"troops": 750,
						"characters": self.person.gm.flush_yongbing()[:3],
					}
				],
				"move_path": move_path,
				"supply_troop": 750,
			}
		)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Slg_PVEMarch")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 永恒战场-查看怪物队伍信息
class MSG_C2S_Slg_GetMonsterInfo:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Slg_GetMonsterInfo(self.person)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Slg_GetMonsterInfo")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 聊天
class MSG_C2S_Chat_Content:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, chat_type, target_id, context):
		packet = PACKETS.C2S_Chat_Content(self.person)
		packet.dict2pb(
			{
				"chat": {
					"chat_type": chat_type,
					"target_id": target_id,
					"content": context,
					"extra_param": None,
				}
			}
		)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Chat_Content")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 礼包购买
class MSG_C2S_Pack_Buy:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id, cnt):
		"""
        uint32 id  = 1;  // 礼包ID
        uint32 cnt = 2;  // 购买次数
        """
		packet = PACKETS.C2S_Pack_Buy(self.person)
		packet["id"] = id
		packet["cnt"] = cnt
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Pack_Buy")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 宠物之星奖励领取
class MSG_C2S_Competition_ObtainScoreAward:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, act_id):
		"""
        uint32 act_id = 1;
        """
		packet = PACKETS.C2S_Competition_ObtainScoreAward(self.person)
		packet["act_id"] = act_id
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Competition_ObtainScoreAward"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 魔法棋局活动设置心愿单
class MSG_C2S_ThemeActivity_SetWish:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, wish_index, wish_award):
		"""
        uint32 wish_index     = 1;  // 心愿索引 从1开始
        base.Award wish_award = 2;  // 心愿奖励
        """
		packet = PACKETS.C2S_ThemeActivity_SetWish(self.person)
		packet.dict2pb({"wish_index": wish_index, "wish_award": wish_award})
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_ThemeActivity_SetWish"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 战宠一键合成
class MSG_C2S_Pet_UpQuality_OneKey:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, ids: list, auto_use_add_items: bool):
		"""
        repeated uint64 ids     = 1;  // 选择的宠物id列表
        bool auto_use_add_items = 2;  // 是否自动使用提升概率道具
        """
		packet = PACKETS.C2S_Pet_UpQuality_OneKey(self.person)
		packet.dict2pb({"ids": ids, "auto_use_add_items": auto_use_add_items})
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Pet_UpQuality_OneKey"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 一番赏活动抽奖
class MSG_C2S_Gacha_Draw:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, num: int):
		"""
        uint32 num = 1;  // 抽奖次数
        """
		packet = PACKETS.C2S_Gacha_Draw(self.person)
		packet["num"] = num
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Gacha_Draw")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 一番赏活动选择奖励
class MSG_C2S_Gacha_ChoseAward:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, award_id: int, index: int):
		"""
                uint32 award_id = 1;  // 奖励id
        uint32 index    = 2;  // drop index
        """
		packet = PACKETS.C2S_Gacha_ChoseAward(self.person)
		packet["award_id"] = award_id
		packet["index"] = index
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Gacha_ChoseAward")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 一番赏活动重置奖池
class MSG_C2S_Gacha_Reset:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Gacha_Reset(self.person)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Gacha_Reset")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 炼金工坊获取宝箱数据
class MSG_C2S_Alchemy_GuildChests:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, tp):
		"""
        uint32 tp = 1;  // 宝箱类型
        """
		packet = PACKETS.C2S_Alchemy_GuildChests(self.person)
		packet["tp"] = tp
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Alchemy_GuildChests"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 炼金工坊领取宝箱奖励
class MSG_C2S_Alchemy_ObtainChestAward:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, ids: list):
		"""
        repeated uint64 ids = 1;  // 要领取的宝箱id
        """
		packet = PACKETS.C2S_Alchemy_ObtainChestAward(self.person)
		packet.dict2pb({"ids": ids})
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Alchemy_ObtainChestAward"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 炼金工坊获取滚屏公告
class MSG_C2S_ScrollAnnounce_GetInfo:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_ScrollAnnounce_GetInfo(self.person)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_ScrollAnnounce_GetInfo"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 公会快速加入
class MSG_C2S_Guild_FastJoin:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Guild_FastJoin(self.person)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Guild_FastJoin")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 炼金工坊-药剂合成
class MSG_C2S_Alchemy_PotionCompose:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id, num):
		"""
                uint32 id  = 1;  // 对应alchemy_potion_info表的id
        uint32 num = 2;  // 要兑换的次数
        """
		packet = PACKETS.C2S_Alchemy_PotionCompose(self.person)
		packet["id"] = id
		packet["num"] = num
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Alchemy_PotionCompose"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 炼金工坊-炼金
class MSG_C2S_Alchemy_Build:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, material_id, size, stone_id):
		"""
        uint32 material_id = 1;  // 对应alchemy_material_info的id
        uint64 size        = 2;  // 投入的材料数量
        uint32 stone_id    = 3;  // 要炼得石头id, 对应alchemy_stone_info得id
        """
		packet = PACKETS.C2S_Alchemy_Build(self.person)
		packet["material_id"] = material_id
		packet["size"] = size
		packet["stone_id"] = stone_id
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Alchemy_Build")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 炼金工坊-领取任务奖励
class MSG_C2S_Alchemy_ObtainQuestAward:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id: list):
		"""
        repeated uint32 ids = 1;  // 要领取的任务id
        """
		packet = PACKETS.C2S_Alchemy_ObtainQuestAward(self.person)
		packet.dict2pb({"ids": id})
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Alchemy_ObtainQuestAward"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 炼金工坊-领取公会积分奖励
class MSG_C2S_Alchemy_ObtainGuildPointAward:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id: list):
		"""
        repeated uint32 ids = 1;  // 要领取的奖励id
        """
		packet = PACKETS.C2S_Alchemy_ObtainGuildPointAward(self.person)
		packet.dict2pb({"ids": id})
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Alchemy_ObtainQuestAward"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 哥布林矿场-领取任务奖励
class MSG_C2S_Gacha_QuestAward:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, quest_ids: list):
		"""
        repeated uint32 quest_ids = 1;
        """
		packet = PACKETS.C2S_Gacha_QuestAward(self.person)
		packet.dict2pb({"quest_ids": quest_ids})
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Gacha_QuestAward")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 公会设置公会玩家是否在公会大厅
class MSG_C2S_Guild_InGuild:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, enter: bool):
		"""
        bool enter = 1;
        """
		packet = PACKETS.C2S_Guild_InGuild(self.person)
		packet["enter"] = enter
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Guild_InGuild")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 保存阵容
class MSG_C2S_Formation_Save:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(
			self, types=1, back_id=None, art_list=None, pet_list=None, character_list=None
	):
		"""
        uint32 type = 1;            // 阵位类型，读enums.FORMATION_TYPE
        base.Formation formation = 2; // 阵容
        character_id,base_id # 佣兵id 账号id
        """
		flush_formation = self.person.gm.flush_formation()
		if back_id:
			flush_beishi_result = self.person.gm.flush_beishi(True)
			back = next(
				(item for item in flush_beishi_result if item["base_id"] == back_id),
				None,
			)
		elif flush_formation["formation"].get("back") is None:
			back = {"id": 0, "base_id": 0, "level": 0}
		else:
			back = flush_formation["formation"]["back"]

		if art_list:
			flush_shenqi_result = self.person.gm.flush_shenqi(True)
			artifact = [
				item for item in flush_shenqi_result if item["base_id"] in art_list
			]
		elif flush_formation["formation"].get("back") is None:
			artifact = [{"id": 0, "base_id": 0, "level": 0}]
		else:
			artifact = flush_formation["formation"].get("artifact")
		if pet_list:
			found_base_ids = set()
			flush_pet_result = self.person.gm.flush_pet()
			pets = [
				item
				for item in flush_pet_result
				if item["base_id"] in pet_list
				   and item["base_id"] not in found_base_ids
				   and not found_base_ids.add(item["base_id"])
			]
		elif flush_formation["formation"].get("pets") is None:
			pets = [{"id": 0, "base_id": 0, "level": 0}]
		else:
			pets = flush_formation["formation"]["pets"]
		if character_list:
			found_base_ids = set()
			flush_yongbing_result = self.person.gm.flush_yongbing()
			unit_list = [
				item
				for item in flush_yongbing_result
				if item["base_id"] in character_list
				   and item["base_id"] not in found_base_ids
				   and not found_base_ids.add(item["base_id"])
			]
			unit_list.insert(0, flush_formation["formation"]["units"][0])
			units = unit_list
			unit_ids = [0, 0, 0, 0, 0, 0]
			unit_ids[0] = list(flush_formation["formation"]["formation"]["unit_ids"])[0]
			if len(character_list) == 2:
				unit_ids[1] = units[1]["character_id"]
				unit_ids[2] = units[2]["character_id"]
			elif len(character_list) == 5:
				unit_ids[1] = units[1]["character_id"]
				unit_ids[2] = units[2]["character_id"]
				unit_ids[3] = units[3]["character_id"]
				unit_ids[4] = units[4]["character_id"]
				unit_ids[5] = units[5]["character_id"]
			else:
				unit_ids[1] = units[1]["character_id"]
		else:
			units = flush_formation["formation"]["units"]
			unit_ids = list(flush_formation["formation"]["formation"]["unit_ids"])
		packet = PACKETS.C2S_Formation_Save(self.person)
		packet.dict2pb(
			{
				"type": types,
				"formation": {
					"units": units,
					"formation": {
						"unit_ids": unit_ids,
						"battle_layout": [2, 1, 3, 4, 5, 6],
					},
					"back": back,
					"artifact": artifact,
					"pets": pets,
					"fight_value": flush_formation["formation"]["fight_value"],
				},
			}
		)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Formation_Save")
			return _result
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 钓鱼-抽奖
class MSG_C2S_WishPool_Draw:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, pool_type: int):
		"""
        uint32 pool_type = 1;
        """
		packet = PACKETS.C2S_WishPool_Draw(self.person)
		packet["pool_type"] = pool_type
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_WishPool_Draw")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 永恒战场-宣战
class MSG_C2S_Slg_CityDeclare:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, city_id: int, tp: int):
		"""
        uint32 city_id = 1;
        uint32 tp = 2;  // 0-宣战 1-取消宣战
        """
		packet = PACKETS.C2S_Slg_CityDeclare(self.person)
		packet["city_id"] = city_id
		packet["tp"] = tp
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Slg_CityDeclare")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 背饰图鉴激活
class MSG_C2S_Back_UpgradeBook:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, advance_ids):
		"""
        map<uint32, uint32> advance_ids = 1;  // key:advance_id value:target_lv
        """
		packet = PACKETS.C2S_Back_UpgradeBook(self.person)
		packet.dict2pb({"advance_ids": advance_ids})
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Back_UpgradeBook")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 请求公会协助
class MSG_C2S_Guild_ReqAssist:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Guild_ReqAssist(self.person)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Guild_ReqAssist")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 公会协助
class MSG_C2S_Guild_AssistOther:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, uid):
		packet = PACKETS.C2S_Guild_AssistOther(self.person)
		packet["uid"] = uid
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Guild_AssistOther")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 公会合并请求
class MSG_C2S_Guild_SetMergeSetting:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, type, merge_tag, announce):
		packet = PACKETS.C2S_Guild_SetMergeSetting(self.person)
		packet.dict2pb(
			{
				"type": type,
				"merge_setting": {"merge_tag": merge_tag, "announce": announce},
			}
		)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Guild_SetMergeSetting"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 获取公会列表
class MSG_C2S_Guild_GetGuildList:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Guild_GetGuildList(self.person)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Guild_GetGuildList")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 宝石合成
class MSG_C2S_Gem_Compose:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, gem_list):
		packet = PACKETS.C2S_Gem_Compose(self.person)
		packet.dict2pb({"list": gem_list})
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Gem_Compose")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 发送公会合并请求
class MSG_C2S_Guild_SendMergeRequest:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, guild_id, types):
		"""
                uint64 guild_id = 1;
        uint32 type     = 2;  // 1-吞并（发起者成为主公会） 2-合并（接受者成为主公会）
        """
		packet = PACKETS.C2S_Guild_SendMergeRequest(self.person)
		packet["guild_id"] = guild_id
		packet["type"] = types
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Guild_SendMergeRequest"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 棋盘保存
class MSG_C2S_GemBoard_Save:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, boards):
		"""
        map<uint32, out_base.GemBoardEquip> boards = 1;  // key-棋盘ID
        bool oneKey                                = 2;  // 是否一键操作
        """
		packet = PACKETS.C2S_Guild_SendMergeRequest(self.person)
		packet.dict2pb({"boards": {boards: {"gems": {6: 211}}}})
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_GemBoard_Save")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 龙骨遗迹创建队伍
class MSG_C2S_CrossTeam_Create:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, level, public):
		"""
        uint32 level = 1;  // 等级条件
        bool public  = 2;  // 是否公开                             = 2;  // 是否一键操作
        """
		packet = PACKETS.C2S_CrossTeam_Create(self.person)
		packet["level"] = level
		packet["public"] = public
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_CrossTeam_Create")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 龙骨遗迹获取队伍信息
class MSG_C2S_CrossTeam_GetInfo:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_CrossTeam_GetInfo(self.person)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_CrossTeam_GetInfo")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 龙骨遗迹获取队伍信息
class MSG_C2S_Artifact_Compose_ActiveAndUpLevel:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, ids):
		"""
        repeated uint32 ids = 1;  // 目标神器缘分id
        """
		packet = PACKETS.C2S_Artifact_Compose_ActiveAndUpLevel(self.person)
		packet.dict2pb({"ids": ids})
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(
					self.person, "S2C_Artifact_Compose_ActiveAndUpLevel"
				)
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 龙骨遗迹快速加入队伍
class MSG_C2S_CrossTeam_FastJoin:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_CrossTeam_FastJoin(self.person)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_CrossTeam_FastJoin")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 宝藏转轮抽奖
class MSG_C2S_LuckyWheel_Roll:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, roll_num):
		packet = PACKETS.C2S_LuckyWheel_Roll(self.person)
		packet["roll_num"] = roll_num
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_LuckyWheel_Roll")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 宝藏转轮抽活动信息
class MSG_C2S_LuckyWheel_GetInfo:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_LuckyWheel_GetInfo(self.person)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_LuckyWheel_GetInfo")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 一番赏活动信息
class MSG_C2S_Gacha_GetInfo:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Gacha_GetInfo(self.person)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Gacha_GetInfo")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# vip奖励领取
class MSG_C2S_Vip_GetAwards:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, tp, vip_lv):
		packet = PACKETS.C2S_Vip_GetAwards(self.person)
		packet['tp'] = tp
		packet['vip_lv'] = vip_lv
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Vip_GetAwards")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 节庆活动签到
class MSG_C2S_Celebration_SignIn:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, ids):
		packet = PACKETS.C2S_Celebration_SignIn(self.person)
		packet.dict2pb({'ids': ids})
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Celebration_SignIn")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 领取祈福卡
class MSG_C2S_Celebration_ReceivePrayCard:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, share_id, from_uid):
		"""
          uint64 share_id = 1;  // 分享的唯一id
          uint64 from_uid = 2;  // 分享的玩家id
        """
		packet = PACKETS.C2S_Celebration_ReceivePrayCard(self.person)
		packet['share_id'] = share_id
		packet['from_uid'] = from_uid
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Celebration_ReceivePrayCard")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 圣诞活动领取任务奖励
class MSG_C2S_Celebration_ObtainQuestAward:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, ids):
		"""
          repeated uint32 ids = 1;
        """
		packet = PACKETS.C2S_Celebration_ObtainQuestAward(self.person)
		packet.dict2pb({'ids': ids})
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Celebration_ObtainQuestAward")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 圣诞活动领取战令任务奖励
class MSG_C2S_Celebration_BattlePassAwardQuest:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, ids):
		"""
          repeated uint32 ids = 1;
        """
		packet = PACKETS.C2S_Celebration_BattlePassAwardQuest(self.person)
		packet.dict2pb({'ids': ids})
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Celebration_BattlePassAwardQuest")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 圣诞活动领取战令等级奖励
class MSG_C2S_Celebration_BattlePassAwardLv:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self):
		packet = PACKETS.C2S_Celebration_BattlePassAwardLv(self.person)
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Celebration_BattlePassAwardLv")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 圣诞活动boss抽卡
class MSG_C2S_CelebrationBoss_Roll:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, recruit_id):
		"""
        uint32 recruit_id = 1;  // 奖池id
        """

		packet = PACKETS.C2S_CelebrationBoss_Roll(self.person)
		packet['recruit_id'] = recruit_id
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_CelebrationBoss_Roll")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 圣诞活动团购
class MSG_C2S_Celebration_TeamBuy:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id, num):
		"""
      uint32 id  = 1;
      uint32 num = 2;
        """

		packet = PACKETS.C2S_Celebration_TeamBuy(self.person)
		packet['id'] = id
		packet['num'] = num
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Celebration_TeamBuy")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass


# 圣诞活动提交祈福卡
class MSG_C2S_Celebration_SubmitPrayCard:
	def __init__(self, person):
		self.person = person

	@response_time
	def run(self, id):
		"""
      uint32 id  = 1;
        """

		packet = PACKETS.C2S_Celebration_SubmitPrayCard(self.person)
		packet['id'] = id
		_result = functions.sendpacket(packet)
		try:
			if _result:
				_result = functions.waitforpacket(self.person, "S2C_Celebration_SubmitPrayCard")
			return _result.dump()
		except TypeError as f:
			print("报错啦,报错信息", f)
			pass
