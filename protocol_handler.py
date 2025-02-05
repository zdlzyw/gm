from typing import Dict, Any, Optional, Callable, Type
from google.protobuf.message import Message
from .packet import Packet

class ProtocolHandler:
    """
    协议处理器,负责:
    1. 注册协议ID和对应的protobuf消息类型
    2. 序列化/反序列化protobuf消息
    3. 处理协议回调
    """
    
    def __init__(self):
        # 协议ID -> protobuf消息类型的映射
        self._protocol_types: Dict[int, Type[Message]] = {}
        # 协议ID -> 回调函数的映射
        self._handlers: Dict[int, Callable] = {}
        # 当前序列号
        self._sequence: int = 0
        
    def register_protocol(self, protocol_id: int, message_type: Type[Message], 
                         handler: Optional[Callable] = None):
        """注册协议"""
        self._protocol_types[protocol_id] = message_type
        if handler:
            self._handlers[protocol_id] = handler
            
    def get_sequence(self) -> int:
        """获取新的序列号"""
        self._sequence += 1
        return self._sequence
        
    def pack_message(self, protocol_id: int, message: Message) -> Optional[bytes]:
        """将protobuf消息打包成网络包"""
        if protocol_id not in self._protocol_types:
            return None
            
        data = message.SerializeToString()
        packet = Packet(protocol_id, self.get_sequence(), data)
        return packet.pack()
        
    def unpack_message(self, data: bytes) -> Optional[tuple[int, Message]]:
        """从网络包解析出protobuf消息"""
        packet = Packet.unpack(data)
        if not packet:
            return None
            
        message_type = self._protocol_types.get(packet.protocol_id)
        if not message_type:
            return None
            
        message = message_type()
        message.ParseFromString(packet.data)
        
        return packet.protocol_id, message
        
    def handle_message(self, protocol_id: int, message: Message):
        """处理收到的消息"""
        handler = self._handlers.get(protocol_id)
        if handler:
            handler(message)
