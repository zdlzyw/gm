"""Protobuf协议实现模块

此模块提供了基于Protocol Buffers的协议实现。
"""

from typing import Dict, Type, Any, Optional
from google.protobuf.message import Message

from game_client_framework.core.protocol.base import BaseProtocol, HeaderField, ProtocolConfig
from game_client_framework.exceptions import (
    PacketError,
    PacketEncodeError,
    PacketDecodeError
)

class ProtobufProtocol(BaseProtocol):
    """Protobuf协议实现
    
    基于Protocol Buffers的协议实现，提供：
    1. 消息类型注册
    2. 自动序列化/反序列化
    3. 灵活的包头定义
    
    使用此类时，需要：
    1. 继承此类
    2. 在 __init__ 中注册所需的包头字段
    3. 注册消息类型
    
    Example:
        ```python
        class GameProtocol(ProtobufProtocol):
            def __init__(self):
                super().__init__()
                # 注册包头字段
                self.register_header_field(HeaderField('msg_id', 2, 'int'))
                self.register_header_field(HeaderField('length', 4, 'int'))
                
                # 注册消息类型
                self.register_message(LoginRequest)
                self.register_message(LoginResponse)
        ```
    """
    
    def __init__(self, config: Optional[ProtocolConfig] = None):
        """初始化协议
        
        Args:
            config: 协议配置，如果为None则使用默认配置
        """
        super().__init__(config)
        self._message_types: Dict[int, Type[Message]] = {}
        
    def register_message(self, message_class: Type[Message]) -> None:
        """注册消息类型
        
        Args:
            message_class: Protobuf消息类
            
        Raises:
            PacketError: 消息类型已存在或无效
        """
        if not hasattr(message_class, 'TYPE_ID'):
            raise PacketError(f"消息类 {message_class.__name__} 未定义 TYPE_ID")
            
        type_id = message_class.TYPE_ID
        if type_id in self._message_types:
            raise PacketError(f"消息类型 {type_id} 已被注册")
            
        self._message_types[type_id] = message_class
        
    def get_message_type(self, type_id: int) -> Type[Message]:
        """获取消息类型
        
        Args:
            type_id: 消息类型ID
            
        Returns:
            消息类型类
            
        Raises:
            PacketError: 消息类型不存在
        """
        if type_id not in self._message_types:
            raise PacketError(f"未知的消息类型: {type_id}")
        return self._message_types[type_id]
        
    def encode_message(self, message: Message) -> tuple[Dict[str, Any], bytes]:
        """编码消息
        
        Args:
            message: Protobuf消息对象
            
        Returns:
            (包头字段字典, 消息体数据)
            
        Raises:
            PacketEncodeError: 编码失败
        """
        try:
            body = message.SerializeToString()
            header = {
                'msg_id': message.TYPE_ID,
                'length': len(body) + self._header_size
            }
            return header, body
        except Exception as e:
            raise PacketEncodeError(f"编码消息失败: {e}")
            
    def decode_message(self, message_type: Type[Message], data: bytes) -> Message:
        """解码消息
        
        Args:
            message_type: 消息类型类
            data: 要解码的数据
            
        Returns:
            解码后的消息对象
            
        Raises:
            PacketDecodeError: 解码失败
        """
        try:
            message = message_type()
            message.ParseFromString(data)
            return message
        except Exception as e:
            raise PacketDecodeError(f"解码消息失败: {e}")
            
    def is_complete_packet(self, header: Dict[str, Any], remaining: bytes) -> bool:
        """检查是否是完整的数据包
        
        Args:
            header: 已解码的包头
            remaining: 剩余数据
            
        Returns:
            是否是完整的数据包
        """
        total_len = header['length']
        return len(remaining) >= total_len - self._header_size
