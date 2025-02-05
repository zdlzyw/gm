from typing import Optional
from google.protobuf import message
from .protocol_handler import ProtocolHandler
import cs_pb2  # 导入生成的protobuf类

class ItemProtocol:
    """道具相关协议处理"""
    
    # 协议ID定义
    MSG_C2S_Item_Use = 100100  # 示例ID,需要替换为实际的协议ID
    MSG_S2C_Item_Use = 100101
    MSG_S2C_GetAwardNotify = 100008
    
    def __init__(self, protocol_handler: ProtocolHandler):
        self.protocol_handler = protocol_handler
        self._register_protocols()
        
    def _register_protocols(self):
        """注册协议和回调"""
        self.protocol_handler.register_protocol(
            self.MSG_C2S_Item_Use, 
            cs_pb2.C2S_Item_Use,
        )
        self.protocol_handler.register_protocol(
            self.MSG_S2C_Item_Use, 
            cs_pb2.S2C_Item_Use,
            self._handle_item_use_response
        )
        self.protocol_handler.register_protocol(
            self.MSG_S2C_GetAwardNotify,
            cs_pb2.S2C_GetAwardNotify,
            self._handle_award_notify
        )
        
    def use_item(self, item_id: int, num: int, index: int = 0, 
                 extra: str = "", quiet: bool = False) -> Optional[bytes]:
        """发送使用道具请求"""
        request = cs_pb2.C2S_Item_Use()
        request.id = item_id
        request.num = num
        request.index = index
        request.extra = extra
        request.quiet = quiet
        
        return self.protocol_handler.pack_message(self.MSG_C2S_Item_Use, request)
        
    def _handle_item_use_response(self, message: cs_pb2.S2C_Item_Use):
        """处理使用道具响应"""
        if message.ret != 0:
            print(f"使用道具失败: {message.ret}")
            return
            
        print(f"使用道具成功: id={message.id}, num={message.num}")
        
        # 处理原始奖励
        if message.origin_awards:
            print("获得原始奖励:")
            for award in message.origin_awards:
                print(f"- 类型:{award.type}, 值:{award.value}, 数量:{award.size}")
                
        # 处理最终奖励
        if message.awards:
            print("获得最终奖励:")
            for awards in message.awards:
                for award in awards.detail:
                    print(f"- ID:{award.uid}, 类型:{award.award.type}, " 
                          f"值:{award.award.value}, 数量:{award.award.size}")
                    
    def _handle_award_notify(self, message: cs_pb2.S2C_GetAwardNotify):
        """处理奖励通知"""
        print(f"收到奖励通知: tip_type={message.tip_type}")
        
        # 处理实际奖励
        if message.awards:
            print("获得实际奖励:")
            for award in message.awards:
                print(f"- ID:{award.uid}, 类型:{award.award.type}, "
                      f"值:{award.award.value}, 数量:{award.award.size}")
                
        # 处理邮件奖励
        if message.mail_awards:
            print("获得邮件奖励:")
            for award in message.mail_awards:
                print(f"- 类型:{award.type}, 值:{award.value}, 数量:{award.size}")
