# _*_coding:utf-8 _*_
# !/usr/bin/python3

# Reference:********************************
# encoding: utf-8
# @Time: 2020/12/14 11:19
# @Author: jingpf
# @File: gm_functions.py
# @Intro: 用于添加一些GM方法
# Reference:********************************

import json
import random
import time

import lupa

from Agame.common.common import PACKETS, functions
from Agame.common.common.MyException import *
from Agame.common.common.config import Config
from Agame.common.common.functions import get_excel_info


class GM_Function:
	def __init__(self, person):
		self.person = person

	# #################################################FLUSH##########################################################
	def __has_key(self, __key: str):
		"""检测当前packet_list中是否有__key的packet，没有返回None, 有则返回对应的最新的packet"""
		if __key not in self.person['packet_list'].keys() or len(self.person['packet_list'][__key]) == 0:
			print(f'未收到{__key}信息包')
			return None
		return self.person['packet_list'][__key].pop()  # 返回最新获得的对应packet

	def get_server_time(self):
		"""获取当前服务器时间戳，根据地区时间偏移量计算出国内时间及时间戳"""
		timestr = functions.get_server_time(self.person['server_time'], self.person['game']['time_offset'])
		return time.strftime("%Y-%m-%d %H:%M:%S", timestr), timestr  # 返回 详细日期，时间戳

	# def flush_general(self, general_all: bool = False, lv: bool = False):
	#     """
	#     获取玩家武将信息
	#     :param general_all: 是否选择全部武将，默认False
	#     :param lv: 是否需要武将等级，默认False
	#     :return:
	#     """
	#     """获取玩家武将信息"""
	#     self.person.MSG_C2S_Flush('武将')
	#     _result = self.__has_key('S2C_FlushKnight')
	#     if _result is not None:
	#         if not lv:
	#             if general_all is True:  # 返回全部武将信息
	#                 return {general.base_id: general.id for general in _result['knights']}
	#             # 返回已上阵武将信息
	#             return {general.base_id: general.id for general in _result['knights'] if general.position > 0}
	#         else:
	#             if general_all is True:  # 返回全部武将信息
	#                 return {general.base_id: (general.id, general.level) for general in _result['knights']}
	#             # 返回已上阵武将信息
	#             return {general.base_id: (general.id, general.level) for general in _result['knights'] if
	#                     general.position > 0}
	#     return {}

	def flush_equip(self, dressed: bool = False):
		"""
        获取玩家装备信息
        :param dressed:  #是否只获取已穿戴装备信息，默认False
        :return:
        """
		param = 'equipment.position == 0'  # 将返回未穿戴装备信息
		if dressed is True:  # 将返回已穿戴装备信息
			param = 'equipment.position != 0'
		self.person.MSG_C2S_Flush('装备')
		_result = self.__has_key('S2C_FlushEquipment')
		equipment_body = {}  # {基础id: [动态id...], ...}
		if _result is not None:
			for equipment in _result['equipments']:
				if eval(param):
					if equipment.base_id not in equipment_body.keys():
						equipment_body[equipment.base_id] = []
					equipment_body[equipment.base_id].append(equipment.id)
		return equipment_body

	def flush_treasure(self, dressed: bool = False):
		"""
        获取玩家的宝物信息
        :param dressed: 是否只获取已穿戴宝物信息
        :return:
        """
		param = 'treasure.position == 0'  # 将返回未穿戴宝物信息
		if dressed is True:  # 将返回已穿戴宝物信息
			param = 'treasure.position != 0'
		self.person.MSG_C2S_Flush('宝物')
		_result = self.__has_key('S2C_FlushTreasure')
		treasure_body = {}  # {基础id: [动态id...], ...}
		if _result is not None and len(_result['treasures']) > 0:
			for treasure in _result['treasures']:
				if eval(param):
					if treasure.base_id not in treasure_body.keys():
						treasure_body[treasure.base_id] = []
					treasure_body[treasure.base_id].append(treasure.id)
		return treasure_body

	def flush_shenqi(self, artifact_all: bool):
		"""获取神器信息"""
		self.person.MSG_C2S_Flush('神器')
		_result = self.__has_key('S2C_FlushUserArtifact')
		if _result is None:
			return {}
		elif artifact_all is True:
			return [{'id': artifact['id'], 'base_id': artifact['base_id'], 'level': artifact['level']} for artifact in
			        _result.dump()['artifact']['artifacts']]  # 获取全部的神器
		else:
			try:
				# 获取上阵的神器
				art_dic = {item['id']: item['level'] for item in
				           self.person.gm.flush_formation()['formation']['artifact']}
				return art_dic
			except KeyError as e:
				return f'报错啦{e}'

	def flush_beishi(self, back_all):
		"""获取背饰"""
		self.person.MSG_C2S_Flush('背饰背包')
		_result = self.__has_key('S2C_FlushBack')
		if _result is None:
			return {}
		elif back_all is True:
			back_list = []
			for back in _result.dump()['backs']:
				back_list.append({'id': back['id'], 'base_id': back['base_id'], 'level': back['lv']})
			return back_list
		else:
			self.person.MSG_C2S_Flush('背饰')
			user_back = self.__has_key('S2C_FlushFormation')
			return [{'id': user_back.dump()['formation']['back']['id'],
			         'base_id': user_back.dump()['formation']['back']['base_id'],
			         'level': user_back.dump()['formation']['back']['level']}]

	def flush_yongbing(self):
		"""获取佣兵"""
		self.person.MSG_C2S_Flush('佣兵')
		_result = self.__has_key('S2C_FlushCharacter')

		if _result is None:
			return {}
		return [{'character_id': character['id'], 'base_id': character['base_id']} for
		        character in _result.dump()['characters'] if character['base_id'] != 1110011]

	def flush_companion_equipment(self):
		"""输出佣兵装备"""
		self.person.MSG_C2S_Flush('佣兵装备')
		_result = self.__has_key('S2C_FlushCompanionEquipment')
		if _result is None:
			return {}
		equipment_dic = {}
		for items in _result.dump()['equipments']:
			if items['base_id'] not in equipment_dic:
				equipment_dic[items['base_id']] = []
			equipment_dic[items['base_id']].append(items['id'])
		return equipment_dic

	def flush_companion_equipment_formation(self):
		"""输出佣兵装备阵容"""
		self.person.MSG_C2S_Flush('佣兵装备阵容')
		_result = self.__has_key('S2C_FlushCompanionEquipmentFormation')
		if _result is None:
			return {}
		equipment_dic = {}
		# for items in _result.dump()['formations']:
		# 	if items['base_id'] not in equipment_dic:
		# 		equipment_dic[items['base_id']] = []
		# 	equipment_dic[items['base_id']].append(items['id'])
		return _result.dump()['formations'][0]

	def flush_formation(self):
		"""获取阵容"""
		self.person.MSG_C2S_Flush('阵容')
		_result = self.__has_key('S2C_FlushFormation')
		if _result is None:
			return {}
		return _result.dump()

	def flush_pet(self):
		"""战宠"""
		pet_list = []

		self.person.MSG_C2S_Flush('战宠')
		_result = self.__has_key('S2C_FlushPet')
		if _result.dump().get('pets') is None:
			pet_list = []
		else:
			for k, v in _result.dump()['pets'].items():
				pet_dic = {}
				pet_dic['pet_id'] = k
				pet_dic['level'] = 1
				pet_dic['base_id'] = v.base_id
				pet_list.append(pet_dic)
		return pet_list

	def flush_coin(self):
		"""获取身上银币数量"""
		self.person.MSG_C2S_Flush('资源')
		_result = self.__has_key('S2C_FlushResource')
		if _result is None:
			return {}
		return {resource.id: resource.num for resource in _result['resources'] if resource.id == 3}

	def flush_gold(self):
		"""获取身上元宝数量"""
		self.person.MSG_C2S_Flush('角色信息')
		_result = self.__has_key('S2C_OpObject')
		if _result is None:
			return {}
		return _result['user'].gold

	def flush_general_tujian(self):
		"""获取武将图鉴信息"""
		_result = self.person.MSG_C2S_KnightBook_Info()
		return dict(zip(_result['id'], _result['level']))

	# #################################################FLUSH#END######################################################

	# #################################################添加资源、设置关卡################################################
	def add_resource(self, itemType, itemId, itemNum):
		# 添加道具(type,id,num)
		return self.person.MSG_C2S_GM_Cmd(f'/user/awards/{itemType}_{itemId}_{itemNum}')

	def del_resourece(self, itemType=None, itemId=None, itemNum=None, items=None):
		# 删除道具
		if items is None:
			items = []
		if itemType is not None and itemId is not None and itemNum is not None:
			items.append((itemType, itemId, itemNum))
		if len(items) == 0:
			print('待删除资源为空')
			return None
		return self.person.MSG_C2S_Test(items, True)

	def del_treasure(self):
		"""清空多余的宝物"""
		self.del_resourece(items=[(8, k, 1) for v in self.flush_treasure().values() for k in v])

	def del_general_equip(self):
		"""清空多余的装备"""
		self.del_resourece(items=[(7, k, 1) for v in self.flush_equip().values() for k in v])

	def del_suipian(self):
		"""清空背包里所有的碎片"""
		self.del_resourece(items=[(2, k, v) for k, v in self.flush_suipian().items()])

	def del_coin(self):
		"""清空元宝及银币"""
		self.del_resourece(items=[(1, k, v) for k, v in self.flush_coin().items()])
		self.del_resourece(999, 0, self.flush_gold())

	def del_items(self):
		self.person.MSG_C2S_Flush()
		_result = self.__has_key('S2C_FlushItem')
		if _result is not None:
			self.del_resourece(items=[(3, daoju.id, daoju.num) for daoju in _result['items']])  # 清道具
		_result = self.__has_key('S2C_FlushAdvanceEquipment')
		if _result is None:
			return
		self.del_resourece(items=[(6, daoju.id, daoju.num) for daoju in _result['advance_equipments']])  # 清进阶材料

	def set_checkpoint(self, point: int):
		"""设置副本关卡:param point:设置到的关卡id，默认最新版本最后一个副本"""
		fubens = get_excel_info('main_dungeon_info')
		id_list = {conf['chapter']: conf['id'] for conf in fubens}

		for k, v in id_list.items():
			if point == k:
				self.person.MSG_C2S_GM_Cmd(f'/user/set_main_dungeon_id/{v}')
			elif point > len(id_list):
				self.person.MSG_C2S_GM_Cmd(f'/user/set_main_dungeon_id/{v}')
				return

	# #################################################添加资源、设置关卡#END############################################

	# #################################################武将操作########################################################
	def shangZhenGeneral(self, pos: int, general_id: int):
		"""上阵武将
        :param pos: 坑位，2-6
        :param general_id: 武将的道具ID
        :return:
        """
		if pos in range(2, 7):  # 坑位2-6
			_result = self.person.MSG_C2S_Formation_ChangeFormation(1, pos, general_id)
			if _result['ret'] == 1:
				print(self.person['uid'], self.person['username'], "{}上阵成功,pos={}".format(general_id, pos))
			else:
				raise ProtocolException(self.person['uid'], self.person['username'], "上阵失败", ret=_result['ret'])
		else:
			raise ValueException(self.person['uid'], self.person['username'], "武将坑位数值超出范围")
		return True

	def check_general_get(self, general_id: int, on=False):
		"""
        检测当前是否已有该武将，有则返回{base_id: dynamic_id}，没有返回False
        :param general_id:待检查的武将id
        :param on:是否只检查上阵武将，默认False
        :return:
        """
		general_all = self.flush_general(True)
		if on:
			general_all = self.flush_general()
		base_id = None
		for _id in range(int(general_id / 10) * 10, int(general_id / 10) * 10 + 8):
			if _id in general_all.keys():
				base_id = _id
				break
		if base_id:
			return {base_id: general_all[base_id]}
		return False

	def general_ShangZhen(self, general_choose_list: list):
		"""
        只上阵武将，不做培养
        :param general_choose_list:待上阵武将列表
        :return:
        """
		general_baseid_list = []
		for general in general_choose_list:
			has_general = self.check_general_get(general)
			if has_general is False:
				self.add_resource(4, general, 1)
			else:
				general, d_id = has_general.popitem()
			general_baseid_list.append(general)
		time.sleep(0.5)
		generals = self.flush_general(True)
		for pos in range(len(general_choose_list)):
			general_id = general_baseid_list[pos]
			if general_id in generals.keys():
				only_id = generals[general_id]
				self.shangZhenGeneral(pos + 2, only_id)  # 武将上阵

	def oneKey_generalShengXing(self, general_all=False):
		"""把身上所有的武将都升到满星"""
		temp_list = self.flush_general(general_all)
		for k, v in temp_list.items():
			if k % 10 < 7:
				general_id = int(k / 10) * 10
				if general_id < 400000:  # 不是武将
					continue
				self.add_resource(2, general_id, 2050)  # 加武将碎片
				for i in range(8 - (k % 10)):
					_result = self.person.MSG_C2S_Knight_StarIncrease(v)
					if _result is None or _result['ret'] != 1:
						break

	def general_ShengJi(self, general_all=False):
		"""一键给上阵的武将升级"""
		self.add_resource(3, 10, 10000000)  # 极品经验书
		general = self.flush_general(general_all, lv=True)
		self.person.MSG_C2S_Flush('角色信息')
		temp_level = self.person['packet_list']['S2C_OpObject'][-1]['user'].level  # 当前主角等级
		print(temp_level, type(temp_level))

		for k, v in general.items():
			while True:
				if temp_level < 200:
					_result = self.person.MSG_C2S_Knight_OneKey_Upgrade(v[0],
					                                                    temp_level - v[1] if v[1] <= temp_level else 0)
				else:
					_result = self.person.MSG_C2S_Knight_OneKey_Upgrade(v[0], 200 - v[1] if v[1] <= 200 else 0)
				if _result is None or _result['ret'] != 1:
					break

	def general_JinJie(self, general_all=False):
		"""将阵上武将全部进阶倒满"""
		self.add_resource(1, 3, 9999999999)
		self.add_resource(3, 11, 10000000)  # 进阶石

		for i in range(1, 73):  # 74
			self.add_resource(6, i, 100000)  # 加进阶道具
		general = self.flush_general(general_all)
		for k, v in general.items():
			while True:
				_result = self.person.MSG_C2S_Knight_AdvanceUpgrade(v)
				if _result is None or _result['ret'] != 1:
					break

	# #################################################武将操作#END####################################################

	# #################################################武将装备操作#####################################################
	def general_Equip_ChuanDai(self, equipment_list=None):
		"""
        一键穿武将装备，只穿戴不养成
        上阵装备,武器1，鞋子2，头盔3，战甲4，逆时针顺序，第二个武将武器5，鞋子6.....
        :param equipment_list: 待装备的装备list,必须是武器,鞋子,头盔,战甲的顺序
        :return:
        """
		if equipment_list is None:
			# equipment_list = [421, 422, 423, 424]  # 金色装备
			equipment_list = [401, 402, 403, 404]  # 金色装备
		for equipment_id in equipment_list:
			self.add_resource(7, equipment_id, 6)  # 添加装备
		time.sleep(0.5)
		equipment_body = self.flush_equip()  # 获取玩家的装备信息
		# 穿戴装备并养成
		for i in range(6):  # 6个武将
			poslist = [(i + 1) * 4 - 3, (i + 1) * 4 - 2, (i + 1) * 4 - 1, (i + 1) * 4]
			for pos in range(4):  # 每个武将4个装备
				daoju_id = equipment_list[pos]
				if daoju_id in equipment_body.keys():
					equip_id = equipment_body[daoju_id].pop(0)  # 都操作完了之后把该装备从列表里删除
					if pos in range(0, 24):
						_result = self.person.MSG_C2S_Formation_ChangeFormation(3, poslist[pos], equip_id)
						if _result['ret'] == 1:
							print(self.person['uid'], self.person['username'], "装备穿戴成功")
						else:
							print(self.person['uid'], self.person['username'], "装备穿戴失败，ret=", _result['ret'])
					else:
						raise ValueException(self.person['uid'], self.person['username'], "装备穿戴失败",
						                     "坑位数值超出范围")

	# return True

	def general_Equip_JingLian(self):
		"""给已经穿戴的装备精炼"""
		self.add_resource(3, 15, 999999999)  # 顶级精炼石
		equipment_body = self.flush_equip(True)
		for equip_list in equipment_body.values():
			for equip_id in equip_list:
				while True:
					_result = self.person.MSG_C2S_Equipment_RefiningOneLevel(equip_id)  # 装备精炼
					if _result is None or _result['ret'] != 1:
						print(self.person['uid'], self.person['username'], "装备精炼失败")
						break
					else:
						print(self.person['uid'], self.person['username'], "装备精炼成功")

	def general_Equip_DiaoWen(self, wenjing_list=None):
		"""
        给已经穿戴的装备雕纹
        :param wenjing_list: 需要添加的纹晶列表
        :return:
        """
		if wenjing_list is None:
			wenjing_list = [47, 48]
		for wenjing in wenjing_list:
			self.add_resource(3, wenjing, 99999999)
		equipment_body = self.flush_equip(True)
		for equip_list in equipment_body.values():
			for equip_id in equip_list:
				while True:
					_result = self.person.MSG_C2S_Equipment_Glyph(equip_id)  # 装备精炼
					if _result is None or _result['ret'] != 1:
						print(self.person['uid'], self.person['username'], "装备雕纹失败")
						break
					else:
						print(self.person['uid'], self.person['username'], "装备雕纹成功")

	def general_Equip_QiangHua(self):
		"""给已经穿戴的装备强化"""
		self.add_resource(1, 3, 9999999999)
		equipment_body = self.flush_equip(True)
		for equip_list in equipment_body.values():
			for equip_id in equip_list:
				while True:
					_result = self.person.MSG_C2S_Equipment_Upgrade(equip_id, 5)  # 强化装备
					if _result is None or _result['ret'] != 1 or _result['level'][0] >= self.person['lv'] * 2:
						print(self.person['uid'], self.person['username'], "装备强化失败")
						break
					else:
						print(self.person['uid'], self.person['username'], "装备强化成功")

	def general_Equip_DuanHun(self, duanhungang_list):
		"""
        给已经穿戴的装备锻魂
        :param duanhungang_list: 锻魂钢列表
        :return:
        """
		for _id in duanhungang_list:
			self.add_resource(3, _id, 7000)  # 添加锻魂钢
		equipment_body = self.flush_equip(True)
		for equip_list in equipment_body.values():
			for equip_id in equip_list:
				while True:
					_result = self.person.MSG_C2S_Equipment_OneKeyDot(equip_id)  # 强化锻魂
					if _result is None or _result['ret'] != 1:
						break

	def general_Equip_ZhuLing(self):
		"""给已经穿戴的装备铸灵"""
		dogFoodList = list(range(401, 405)) + list(range(421, 425)) + [5000, 5010, 5020, 5030]
		for _id in dogFoodList:
			self.add_resource(2, _id, 40000)  # 添加狗粮
		equipment_body = self.flush_equip(True)
		for equip_list in equipment_body.values():
			for equip_id in equip_list:
				dogFoodList = list(range(401, 405)) + list(range(421, 425)) + [5000, 5010, 5020, 5030]
				for _id in dogFoodList:
					while True:
						_result = self.person.MSG_C2S_Equipment_Cast(0, equip_id, _id, 100)  # 装备铸灵
						if _result is None or _result['ret'] != 1:
							break

	# #################################################武将装备操作#END#################################################

	# #################################################武将宝物操作#####################################################
	def chuanDaiBaoWu(self, pos, baowu_id):
		"""
        穿戴宝物
        :param pos: 坑位，1-12
        :param baowu_id: 宝物ID
        :return:
        """
		if pos in range(1, 13):
			_result = self.person.MSG_C2S_Formation_ChangeFormation(4, pos, baowu_id)
			if _result['ret'] == 1:
				print(self.person['uid'], self.person['username'], "宝物穿戴成功")
			else:
				print(self.person['uid'], self.person['username'], "宝物穿戴失败,ret=", _result['ret'])
		else:
			print(self.person['uid'], self.person['username'], "宝物穿戴失败", '坑位数值超出范围')

	def treasure_ChuanDai(self, baowu_list=None):
		"""
        一键穿戴宝物不养成，左1，右2，依次递增
        :param baowu_list: 需要穿戴的宝物列表
        :return:
        """
		if baowu_list is None:
			baowu_list = [11320, 12210]  # 默认加孟德新书，将军印
		for baowu in baowu_list:
			self.add_resource(8, baowu, 6)  # 加宝物
		treasure_body = self.flush_treasure()  # 获取玩家所有宝物信息
		for i in range(1, 7):  # 一共6个武将
			poslist = [i * 2 - 1, i * 2]
			for pos in range(2):  # 一个武将穿2个宝物
				daoju_id = baowu_list[pos]
				if daoju_id in treasure_body.keys():
					baowu_id = treasure_body[daoju_id].pop(0)
					self.chuanDaiBaoWu(poslist[pos], baowu_id)
					pos += 1  # 右侧宝物穿戴位置

	def baoWuJingLian(self, baowu_id, only_id):
		"""
        宝物精炼，只处理红色品质的，每个品质消耗资源不同，懒得写那么烦
        :param baowu_id: 宝物短id
        :param only_id:宝物唯一id
        :return:
        """
		dog_food_list = {11010: 11010, 11020: 11020, 11110: 11110, 11120: 11120, 11210: 11210, 11320: 11320,
		                 11410: 11210, 11420: 11320, 11510: 11210, 11520: 11320, 12010: 12010, 12020: 12020,
		                 12110: 12110, 12120: 12120, 12210: 12210, 12320: 12320, 12410: 12210, 12420: 12320,
		                 12510: 12210, 12520: 12320, }  # 精炼对应的材料列表
		# need_dogfood_num = [0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11, 11, 11, 11, 11, 12, 12, 12,
		#                     12, 12, 13, 13, 13, 13, 13, 14, 14, 14, 14, 14, 15, 15, 15, 15, 15, ]
		need_dogfood_num_new = [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5,
		                        5]
		# time.sleep(0.5)
		for num in need_dogfood_num_new:
			dogfood_list = []
			treasure_body = self.flush_treasure(False)  # 获取玩家所有宝物信息
			if dog_food_list[baowu_id] in treasure_body.keys():
				for _ in range(num):
					food_id = treasure_body[dog_food_list[baowu_id]].pop()
					dogfood_list.append(food_id)
			self.person.MSG_C2S_Treasure_Refining(only_id, dogfood_list)  # 精炼

	def add_treasure_and_unlock(self):
		"""加宝物资源并解锁"""
		self.add_resource(1, 3, 999999999)  # 银币
		self.add_resource(3, 17, 100000000)  # 宝物精炼石
		need_dogfood_num_new = [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5,
		                        5]
		baowu_list = [11320, 12210]
		for baowu_id in baowu_list:
			self.add_resource(8, baowu_id, sum(need_dogfood_num_new) * 10)
		treasure_body = self.flush_treasure(False)  # 刷新未穿戴的宝物信息
		for k, v in treasure_body.items():
			print("狗粮资源解锁中...")
			self.person.MSG_C2S_Treasure_Luck(v)
		print("狗粮资源解锁成功")

	def treasure_JingLian(self):
		"""给穿戴的宝物精炼"""
		self.add_treasure_and_unlock()
		treasure_body_weared = self.flush_treasure(True)  # 刷新已穿戴的宝物信息
		for k, v in treasure_body_weared.items():
			for treasure_id in v:
				self.baoWuJingLian(k, treasure_id)  # 宝物精炼
		self.del_treasure()  # 清理背包，以防背包满了

	def treasure_QiangHua(self):
		"""给穿戴的宝物强化"""
		self.add_resource(1, 3, 9999999999)
		treasure_body = self.flush_treasure(True)
		for treasure_list in treasure_body.values():
			for treasure_id in treasure_list:
				while True:
					self.add_resource(8, 13030, 100)  # 经验虎符
					_result = self.person.MSG_C2S_Treasure_Upgrade_OneLevel(treasure_id, 60)  # 强化宝物
					if _result is None or _result['ret'] != 1:
						break

	def treasure_DiaoWen(self):
		"""给穿戴的宝物雕纹"""
		self.add_resource(3, 49, 80000)  # 低级宝物纹晶
		self.add_resource(3, 50, 80000)  # 高级宝物纹晶
		treasure_body = self.flush_treasure(True)
		for treasure_list in treasure_body.values():
			for treasure_id in treasure_list:
				while True:
					_result = self.person.MSG_C2S_Treasure_Glyph(treasure_id)  # 雕纹
					if _result is None or _result['ret'] != 1:
						break

	# #################################################武将宝物操作#END#################################################

	def generalTuJianShengJi(self, general_id):
		"""
        武将图鉴升级
        :param general_id: 武将id
        :return:
        """
		general_id = int(general_id / 10) * 10
		while True:
			_result = self.person.MSG_C2S_KnightBook_Upgrade(general_id)
			if _result is None or _result['ret'] != 1:
				break

	def oneKey_generalTuJian(self, general_list):
		"""
        一键武将图鉴
        :param general_list:点亮图鉴的武将list
        :return:
        """
		self.add_resource(3, 37, 90000000)  # 图鉴升级卷轴
		for general_id in general_list:  # 添加所有武将，用于开图鉴
			has_general = self.check_general_get(general_id)
			if has_general is False:
				general_id = int(general_id / 10) * 10 + 7
				self.add_resource(4, general_id, 1)  # 添加所有武将
		time.sleep(0.5)
		general_list = self.flush_general(True).keys()  # 只开已有武将的
		for general_id in general_list:  # 开所有图鉴
			self.generalTuJianShengJi(general_id)  # 图鉴升级

	def get_id_of_sanguozhi(self, _key):
		"""
        repeated uint32 main_ids = 2; //主线节点激活情况
        repeated uint32 hero_ids = 3; //名将节点激活情况
        repeated uint32 nightmare_ids = 4; // 噩梦节点激活情况
        repeated uint32 town_soul_ids = 5; //镇魂节点激活情况
        repeated uint32 elite_ids = 6; //精英副本节点激活情况
        :param _key:
        :return:
        """
		_result = self.person.MSG_C2S_Scroll_Info()
		print(_key, type(_key))
		print(_result.toDict())
		if _result is not None:  # and _key in _result.toDict():
			return max(_result[_key])
		else:
			return 0

	def sanGuoZhi_zhuxian(self, num):
		"""主线三国志点亮"""
		self.add_resource(3, 24, 1000)  # 加主线残卷
		_id = 1
		for _ in range(num):
			_result = self.person.MSG_C2S_Scroll_Activate(_id, 1)
			_id += 1

	def sanGuoZhi_liezhuan(self, num):
		"""列传三国志点亮"""
		self.add_resource(3, 36, 1000)  # 加列传残卷
		_id = 1001
		for _ in range(num):
			_result = self.person.MSG_C2S_Scroll_Activate(_id, 2)
			_id += 1

	def huoDeBianZhuang(self, bianzhuang_list):
		"""
        获取变装
        :param bianzhuang_list:需要添加的变装列表
        :return:
        """
		for bianzhuang in bianzhuang_list:  # 获得所有变装
			self.add_resource(13, bianzhuang, 1)

	def getHeJi(self, heji_list):
		"""
        获得合击兵符
        :param heji_list:合击兵符列表
        :return:
        """
		for heji in heji_list:
			self.add_resource(5, heji, 1)  # 添加

	def activeHeJi(self, heji_list):
		"""
        激活合击兵符
        :param heji_list:合击兵符列表
        :return:
        """
		for heji in heji_list:
			self.person.MSG_C2S_UniteToken_Awaken(heji)  # 兵符激活

	def oneKey_ShangZhenBingFu(self, bingfu_list):
		"""
        一键上阵合击兵符
        :param bingfu_list:上阵兵符列表
        :return:
        """
		for pos in range(1, 5):
			bingfu_id = bingfu_list[pos - 1]
			bingfu_id = int(bingfu_id / 10) * 10
			_result = self.person.MSG_C2S_Formation_ChangeFormation(2, pos, bingfu_id)

	def bingFuKeYin(self, heji_list):
		"""
        激活合击兵符
        :param heji_list:合击兵符列表
        :return:
        """
		self.add_resource(3, 32, 1000000)  # 兵符灵印
		self.add_resource(3, 35, 99999999)  # 兵符灵印
		for heji in heji_list:
			heji = int(heji / 10) * 10
			while True:
				_result = self.person.MSG_C2S_UniteToken_Upgrade(heji)
				if _result is None or _result['ret'] != 1:
					break

	def bingFuTuPo(self):
		"""突破合击兵符"""
		heji_list = self.flush_heji()
		heji_list = {k: v for k, v in heji_list.items() if v < (k + 5)}
		for k, v in heji_list.items():
			self.add_resource(2, k, 1500)
			for _ in range(k + 5 - v):
				_result = self.person.MSG_C2S_UniteToken_StarIncrease(k)
				if _result is None or _result['ret'] != 1:
					break

	def make_game_robot(self, general_list=None, general_num=None):
		"""制作机器人账号，制作过程随机，战力基本不一致"""
		# 加资源，等级
		self.add_resource(1, 1, random.randint(4, 20) * 1000000)  # 加等级
		self.add_resource(999, 0, 1000000)  # 元宝
		# self.set_checkpoint()  # 执行该脚本会报错
		# 上阵武将,随机上阵4-6个武将，武将从列表里随机抽选
		if general_num is None:
			general_num = random.randint(3, 5)
		# 武将id list，并非最全的，可自选
		if general_list is None:
			general_list = [500010, 500020, 500030, 500040, 500050, 500060, 500070, 500080,
			                500090, 500100, 500110, 500120, 500130, 500140, 500150, 500160, 500170, 500180, 500190,
			                500200, 500210, 500220, 500230, 500240, 510010, 510020, 510030, 510040, 510050, 510060,
			                510070, 510080, 600020, 600030, 600050, 600080, 600090, 600100, 600110, 600120, 600010,
			                600040, 600060, 600070]
		general_choose_list = random.sample(general_list, general_num)
		for _i in range(len(general_choose_list)):
			general_choose_list[_i] = general_choose_list[_i] + random.randint(0, 7)
			self.add_resource(4, general_choose_list[_i], 1)
		time.sleep(0.5)
		generals = self.flush_general(True)
		for pos in range(len(general_choose_list)):
			general_id = general_choose_list[pos]
			if general_id in generals.keys():
				only_id = generals[general_id]
				self.shangZhenGeneral(pos + 2, only_id)
		return True

	def Join_or_Create_guild(self, server, _prefix, guild_num):
		"""
        加入/创建军团
        :param guild_name: string 军团名字
        :param level: int 军团等级
        :return:
        """

		self.person(server, 'Agame', )

	# if len(guild_name) > 8:
	# 	print(f"军团名字过长:{guild_name}")
	# 	return
	# _result = self.person.MSG_C2S_Guild_Search(guild_name)
	# if _result['ret'] == 1:
	# 	if _result['simple_guild']['member_cnt'] >= 20:
	# 		raise ProtocolException("军团人数已满")
	# elif _result['ret'] == 750:
	# 	print(self.person['uid'], self.person['username'], "已加入军团")
	# 	return True
	# elif _result['ret'] == 87 or _result['ret'] == 104:
	# 	self.person.gm.add_resource(1, 2, 1000000)
	# 	self.person.gm.add_resource(999, 0, 1000000)
	# 	_result2 = self.person.MSG_C2S_Guild_Create(guild_name)
	# 	if _result2['ret'] == 1:
	# 		self.person['is_guild_boss'] = True
	# 		self.person.MSG_C2S_Chat("/set_guild_level {}".format(level))
	# 		print(self.person['uid'], self.person['username'], "军团等级10级设置完毕")
	# 		self.person['self_guild_id'] = _result2['guild'].id
	# 		return True
	# 	else:
	# 		raise ProtocolException(self.person['uid'], "创建军团失败", ret=_result2['ret'])
	# else:
	# 	raise ProtocolException(self.person['uid'], "创建或加入军团失败", ret=_result['ret'])
	# _result = self.person.MSG_C2S_Guild_Join(self.person['self_guild_id'])
	# if _result['join']:
	# 	print(self.person['uid'], self.person['username'], "成功加入军团：", guild_name)
	# 	self.person['is_guild_boss'] = False
	# 	return True
	# else:
	# 	raise ProtocolException(self.person['uid'], self.person['username'], "加入军团失败：", ret=_result['ret'])

	def set_arena_rank(self, rank):
		self.person.gm.add_resource(1, 1, 11111111111111)
		# 培养战力: 穿戴厉害的装备7 1/2/3/4
		print("先培养一下装备....")
		self.person.gm.make_game_robot()  # 上阵武将
		self.person.gm.general_Equip_ChuanDai([1, 2, 3, 4])  # 穿戴测试装备
		# self.person.gm.general_Equip_QiangHua()  # 给已穿戴的装备强化
		self.person.gm.general_Equip_JingLian()  # 给已穿戴的装备精炼

		self.person.MSG_C2S_Chat(f'/pass_dungeon_to_spec 50')  # 设置关卡副本

		self.person.gm.add_resource(3, 16, 11111)  # 添加入场券
		self.person.MSG_C2S_Item_Use(16, 1000)  # 使用入场券道具，转换为挑战次数

		# 打战斗
		print("培养好了，开始战斗...")
		current_rank = 999999999999
		while current_rank > rank:
			_result = self.person.MSG_C2S_Arena_GetMainInfo()
			current_rank = _result['rank']
			arena_units = _result['arena_units']
			min_rank = min([i.rank for i in arena_units])
			# 挑战
			self.person.MSG_C2S_Arena_ChallengeBegin(min_rank)

	def Biography_team_battle(self, _ids):
		# 前置条件，培养一下队伍，不然打不过啊...
		self.person.gm.add_resource(1, 1, 1111111111)
		self.person.MSG_C2S_Chat(f'/pass_dungeon_to_spec 150')  # 设置关卡副本
		self.person.gm.make_game_robot()
		self.person.gm.general_Equip_ChuanDai([1, 2, 3, 4])
		self.person.gm.general_Equip_JingLian()

		# 开始打战斗
		for _id in _ids:
			self.person.MSG_C2S_Biography_CreateTeam(_id)
			self.person.MSG_C2S_Biography_InviteRobot(_id)
			self.person.MSG_C2S_Biography_AttackCampaignBegin(_id)

	def set_tower_prob(self, m_type, m_layer, knight_list):
		baseId = None
		if m_type == 2:
			baseId = 12000001
		elif m_type == 3:
			baseId = 14000001
		elif m_type == 4:
			baseId = 16000001
		elif m_type == 5:
			baseId = 18000001
		elif m_type == 1:
			baseId = 10000001
		else:
			print("输入的塔类型不存在，请重新输入")
			return
		for i in range(m_layer):
			_data = self.person.MSG_C2S_Tower_ChallengeStageBegin(baseId, knight_list)
			battle_id = _data['S2C_Tower_ChallengeStageBegin']['battle_id']
			self.person.gm.checkBattle(battle_id, _data['S2C_ReplyBattleReport'])
			baseId += 1

	# 无双试炼
	def wushuang_shilian(self, _id: int = 1):
		"""
        设置通关无双试炼章节
        :param _id:章节id，默认
        :return:
        """
		num = 0
		while True and num < _id:
			_result = self.person.MSG_C2S_DeadBattle_GetInfo()  # 获取无双试炼信息
			if _result is not None and _result['ret'] == 1:
				if _result['dbattle'].floor > _id:  # 当前层数高于目标层数则跳过
					break
				floor_task = 3 - len([i for i in _result['dbattle'].floor_star if i > 0])  # 当前层还有几个能打
				is_award = _result['dbattle'].is_award  # 当前层是否已经领取奖励
				for i in range(floor_task):  # 如果还有没打的打一下
					_result = self.person.MSG_C2S_DeadBattle_ChallengeBegin(2)
					if 'S2C_DeadBattle_ChallengeBegin' in _result.keys():
						if _result['S2C_DeadBattle_ChallengeBegin'] is None:
							print('未收到回包')
							break
						if _result['S2C_DeadBattle_ChallengeBegin']['ret'] != 1:
							print('ret值：', _result['S2C_DeadBattle_ChallengeBegin']['ret'])
							break
						battle_id = _result['S2C_DeadBattle_ChallengeBegin']['battle_id']
						self.checkBattle(battle_id, _result['S2C_ReplyBattleReport'])
				if is_award is False:
					_result = self.person.MSG_C2S_DeadBattle_BoxAward()
				_result = self.person.MSG_C2S_DeadBattle_GetInfo()
				if _result is not None and _result['ret'] == 1:
					buffs = [i for i in _result['dbattle'].floor_buff if i > 0]
					if len(buffs) > 0:
						self.person.MSG_C2S_DeadBattle_PickBuff(buffs[-1])
			else:
				break
			num += 1

	def gm_code(self, code):
		"""发送GM命令"""
		self.person.MSG_C2S_GM_Cmd(code)

	def checkBattle(self, battle_id: int, battleReport):
		"""获取战报，并生成战报结果"""
		if battleReport.__class__.__name__ == 'S2C_ReplyBattleReport':
			print('----------------------test')
			packet = PACKETS.BattleReport(self.person)
			packet.filldatafromstream(battleReport['report'])
			BattleReport_str = functions.pb2dict(packet.obj)
			print('------------------BattleReport_str', BattleReport_str)
			jsonStr = json.dumps(BattleReport_str)
			print('------------------jsonStr', jsonStr)
			# print('JKJKJKJKJK,JSONSTR', jsonStr)
			root_dir = Config.common_lib
			root_dir = root_dir.replace("\\", "/")
			if int(packet['battle_id']) == int(battle_id):
				lua = lupa.LuaRuntime()
				luapath1 = '''package.path = ";''' + root_dir + '''/battle_check/src/?.lua;" .. package.path'''
				luapath2 = '''package.path = ";''' + root_dir + '''/battle_check/src/protobuf/?.lua;" .. package.path'''
				import platform
				sysstr = platform.system()
				if sysstr == "Windows":
					lua.execute(luapath1.replace('/', r'\\'))
					lua.execute(luapath2.replace('/', r'\\'))
				else:
					lua.execute(luapath1)
					lua.execute(luapath2)
				lua.execute('''require("battle_py")''')
				autoBattleResult = lua.eval("autoBattleResult")
				resultJson = autoBattleResult(jsonStr)  # 执行战斗
				result = json.loads(resultJson)
				packet = PACKETS.BattleResult(self.person)  # 数据对象
				packet.dict2pb(result)
				battlResult = packet.getmediumstream()
				_result = self.person.MSG_C2S_CheckBattleResult(battlResult)
				if _result['ret'] == 1:
					print("战斗成功")
				else:
					print(str(self.person['uid']) + "战斗失败" + str(_result['ret']))
					if _result['ret'] == 1001:
						raise ProtocolException("战斗失败,需要更新战斗代码")  # 直接秒怪可以避免
					raise ProtocolException(str(self.person['uid']) + "战斗失败")

	def getawardname(self):
		charlist = []
		quality = {item['id']: item['quality_set'] for item in get_excel_info('character_companion_info')}
		for k, v in quality.items():
			if v == 1:
				for i in range(2, 8):
					charlist.append(str(k) + "{:0>2d}".format(i))
			if v == 2:
				for i in range(4, 10):
					charlist.append(str(k) + "{:0>2d}".format(i))
			if v == 3:
				for i in range(6, 16):
					if i == 15:
						charlist.append(str(k) + "{:0>2d}".format(i))
		return charlist

	def artifact_uplevel(self, end_level, artifact_all=False):
		"""
		神器升级
		end_level:最终等级
		artifact_all:判断升级全部神器还是上阵神器
		"""
		if artifact_all:  # 升级全部神器
			for art in self.flush_shenqi(artifact_all):
				if art['level'] == end_level:
					continue
				else:
					for i in range(art['level'], end_level + 1):
						time.sleep(0.3)
						self.person.gm.add_resource(1, 3, 10000000)
						self.person.gm.add_resource(1, 101, 10000)
						uplevel_result = self.person.MSG_C2S_Artifact_UpLevel(art['id'], i)
						if uplevel_result['ret'] == 1:
							print('*' * 20, '神器升级成功')
						elif uplevel_result['ret'] != 1:
							print('*' * 20, '神器升级失败')
							continue
		else:  # 升级上阵神器
			shenqi_dic = self.flush_shenqi(artifact_all)
			for k, v in shenqi_dic.items():
				if v == end_level:
					print('已经升级到指定等级,不升级了')
					continue
				else:
					for i in range(v, end_level + 1):
						time.sleep(0.3)
						self.person.gm.add_resource(1, 3, 10000)
						self.person.gm.add_resource(1, 101, 10000)
						uplevel_result = self.person.MSG_C2S_Artifact_UpLevel(k, i)
						if uplevel_result['ret'] == 1:
							print('*' * 20, '神器升级成功')
						else:
							print('*' * 20, '神器升级失败')

	def Back_UpgradeLv(self, end_level, beishi_all):
		"""
		背饰升级
		end_level:最终等级
		"""
		for back in self.flush_beishi(beishi_all):
			if back['level'] == end_level:
				print('已经升级到指定等级,不升级了')
				continue
			else:
				for i in range(back['level'], end_level + 1):
					self.person.gm.add_resource(3, 4, 10000)  # 背饰升级道具
					time.sleep(0.2)
					upgradelv_result = self.person.MSG_C2S_Back_UpgradeLv(back['id'], i)
					if upgradelv_result['ret'] == 1:
						print('*' * 20, '背饰升级成功')
					else:
						print('*' * 20, '背饰升级失败')

	def add_allbeishi(self):
		'''
		加全部背饰
		'''
		count = 0
		print("正在添加背饰.....")
		print("开始解锁背包格子....")
		while True:
			count += 1
			self.person.gm.add_resource(999, 0, 900)
			time.sleep(0.5)
			resp = self.person.MSG_C2S_Back_ExpandBag()
			# if resp['ret']!=1:
			# 	break
			if count == 40:
				break
		back_info = get_excel_info('back_info')
		back_list = [back_item['id'] for back_item in back_info if back_item['next_id'] == 0]
		b_num = 0
		for back_id in back_list:
			b_num += 1
			time.sleep(0.3)
			self.person.gm.add_resource(16, back_id, 1)
		print("背饰全部添加完毕.....")

	def add_allshenqi(self):
		"""
		加全部神器
		"""
		artifact_info = get_excel_info('artifact_info')
		artifact_list = [artid['id'] for artid in artifact_info if artid['star_num'] == 0]
		for art in artifact_list:
			time.sleep(0.3)
			self.person.gm.add_resource(10, art, 1)
		print('全部神器添加完毕')

	def add_allyongbin(self):
		'''
		加全部佣兵
		'''
		print("正在添加所有佣兵......")
		for i in self.getawardname():
			time.sleep(0.3)
			self.person.gm.add_resource(4, i, 1)
		# avatar_info = get_excel_info('avatar_info')
		# character_list = [item['id'] for item in avatar_info]
		# for i in character_list:
		# 	time.sleep(0.3)
		# 	self.person.gm.add_resource(13, i, 1)
		print('全部佣兵添加完毕')

	def set_eqlv(self, lv):
		'''
		设置装备品质
		'''
		print("正在设置装备品质.....")
		level_list = []
		equipment = get_excel_info("equipment_info")
		equipment_id = {conf['id']: conf['quality'] for conf in equipment}
		for k, v in equipment_id.items():
			if v == int(lv):
				level_list.append(k)
		for level in level_list[:11]:
			self.person.gm.add_resource(6, level, 1)
			self.person.MSG_C2S_GM_Cmd(f"/user/wear_equipment/{level}")
		print(f'装备品质{lv}级设置成功')
		return True

	def artifact_upstart(self, lv, artifact_all: bool):
		'''
		神器升星
		'''
		if artifact_all:
			for art_start in self.flush_shenqi(artifact_all):
				for _ in range(lv):
					time.sleep(0.2)
					_result = self.person.MSG_C2S_Artifact_UpStar(art_start['id'])
					if _result['ret'] != 1:
						continue
		else:
			for k, v in self.flush_shenqi(artifact_all).items():
				for _ in range(lv):
					time.sleep(0.2)
					_result = self.person.MSG_C2S_Artifact_UpStar(k)
					k += 1
					if _result['ret'] != 1:
						continue

	def shangzheng_yongbing(self, character_list):
		'''
		上阵佣兵
		'''
		_result = self.person.MSG_C2S_Formation_Save(character_list=character_list)
		return _result['ret']

	def shangzheng_beishi(self, back_id):
		"""
		上阵背饰
		"""
		_result = self.person.MSG_C2S_Formation_Save(back_id=back_id)
		return _result['ret']

	def shangzheng_shenqi(self, art_list):
		"""
		上阵神器
		"""
		_result = self.person.MSG_C2S_Formation_Save(art_list=art_list)
		return _result['ret']

	def shangzheng_zhanchong(self, pet_list):
		"""
		上阵战宠
		"""
		_result = self.person.MSG_C2S_Formation_Save(pet_list=pet_list)
		return _result['ret']

	def shangzheng_huobanzhuangbei(self, quality):
		"""
		上阵佣兵装备
		"""
		huobanzhuangbei_info = self.person.gm.flush_companion_equipment()
		quality_list = [item['id'] for item in get_excel_info('companion_equipment_info') if item['quality'] == quality]
		_result1 = self.person.MSG_C2S_CompanionEquip_ChangeFormation(2, [
			{'equip_id': huobanzhuangbei_info.get(quality_list[i])[0]} for i in range(len(quality_list))])  # 阵位1
		_result2 = self.person.MSG_C2S_CompanionEquip_ChangeFormation(3, [
			{'equip_id': huobanzhuangbei_info.get(quality_list[j])[1]} for j in range(len(quality_list))])  # 阵位2
		if _result1['ret'] == 1 and _result2['ret'] == 1:
			return True
		return False

	def huobanzhuangbei_uplv(self, level):
		"""
		伙伴装备升级
		"""
		self.person.gm.flush_companion_equipment_formation()
		type = 1
		slot = 2
		count = 0
		au = 0
		while True:
			count += 1
			time.sleep(0.2)
			self.person.gm.add_resource(1, 106, 1000)
			up_result = self.person.MSG_C2S_CompanionEquip_Upgrade(slot, type, count)
			if up_result['level'] == level:
				au += 1
				type += 1
				count = 0
			if type == 5:
				slot = 3
				type = 1
			if au == 8:
				break


