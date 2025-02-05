from typing import Any, Dict, Type, Optional, Tuple
from google.protobuf import message as pb_message
from .base import ProtocolBase, ProtocolConfig, HeaderField, EncodeError, DecodeError
from ...exceptions import GCFError, SerializationError, DeserializationError
from ...utils.logger import logger

class ProtobufError(GCFError):
    """Protobuf相关错误"""
    pass

class ProtobufProtocolBase(ProtocolBase):
    """Protobuf协议基类"""
    
    def __init__(self, config: Optional[ProtocolConfig] = None):
        super().__init__(config)
        # 消息类型映射
        self._msg_id_to_type: Dict[int, Type[pb_message.Message]] = {}
        self._type_to_msg_id: Dict[Type[pb_message.Message], int] = {}
        
    def register_message(self, msg_id: int, msg_type: Type[pb_message.Message]) -> None:
        """注册消息类型"""
        self._msg_id_to_type[msg_id] = msg_type
        self._type_to_msg_id[msg_type] = msg_id
        
    def decode_message(self, message_type: Type[pb_message.Message], data: bytes) -> Any:
        """解码消息体"""
        try:
            msg = message_type()
            try:
                msg.ParseFromString(data)
            except Exception as e:
                raise DeserializationError(f"消息反序列化失败: {e}")
            return msg
        except Exception as e:
            logger.error(f"解码消息失败: {e}")
            raise
            
    def encode_message(self, message: pb_message.Message) -> Tuple[Dict[str, Any], bytes]:
        """编码消息"""
        try:
            # 1. 获取消息ID
            msg_type = type(message)
            msg_id = self._type_to_msg_id.get(msg_type)
            if msg_id is None:
                raise ProtobufError(f"未注册的消息类型: {msg_type.__name__}")
                
            # 2. 序列化消息体
            try:
                body = message.SerializeToString()
            except Exception as e:
                raise SerializationError(f"消息序列化失败: {e}")
            if len(body) > self.config.max_packet_size - self._header_size:
                raise EncodeError("消息编码", f"消息体过大: {len(body)} 字节")
                
            # 3. 准备包头字段
            return {'messageId': msg_id}, body
            
        except Exception as e:
            logger.error(f"编码消息失败: {e}")
            if not isinstance(e, EncodeError):
                raise EncodeError("消息编码", str(e))
            raise
