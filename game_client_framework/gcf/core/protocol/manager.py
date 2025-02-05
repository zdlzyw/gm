import logging
from typing import Optional, Any, Dict
from dataclasses import dataclass
from ...exceptions import GCFError, NetworkError, SendError, ReceiveError
from ...utils.logger import logger
from ..network import BaseConnection
from .base import ProtocolBase, ProtocolConfig
from .handler import ProtocolHandler

class ProtocolManagerError(GCFError):
    """协议管理器错误"""
    pass

@dataclass
class ProtocolStats:
    """协议统计信息"""
    total_received: int = 0
    total_sent: int = 0
    decode_errors: int = 0
    encode_errors: int = 0
    handler_errors: int = 0

class ProtocolManager:
    """协议管理器"""
    def __init__(self, protocol: ProtocolBase, handler: Optional[ProtocolHandler] = None):
        self.protocol = protocol
        self.handler = handler or ProtocolHandler()
        self._connection: Optional[BaseConnection] = None
        self._buffer = bytearray()
        self.stats = ProtocolStats()
        
    def set_connection(self, connection: BaseConnection) -> None:
        """设置连接"""
        if self._connection:
            self._connection.remove_receive_callback(self._on_data)
            
        self._connection = connection
        connection.on_receive(self._on_data)
        
    async def _on_data(self, data: bytes) -> None:
        """处理接收到的数据"""
        try:
            # 将数据添加到缓冲区
            self._buffer.extend(data)
            self.stats.total_received += len(data)
            
            # 处理所有完整的消息
            while len(self._buffer) >= self.protocol._header_size:
                # 1. 尝试解析包头
                try:
                    header, remaining = self.protocol.decode_header(self._buffer)
                except Exception as e:
                    # 包头解析失败，可能是数据不完整
                    self.stats.decode_errors += 1
                    raise ReceiveError(f"包头解析失败: {e}")
                    
                # 2. 检查包完整性
                if not self.protocol.is_complete_packet(header, remaining):
                    break
                    
                # 3. 获取消息类型
                message_type = self.protocol.get_message_type(header)
                if message_type is None:
                    raise ProtocolManagerError(f"未知的消息类型: {header}")
                    
                # 4. 解码消息体
                try:
                    message = self.protocol.decode_message(message_type, remaining)
                except Exception as e:
                    # 消息体解码失败
                    self.stats.decode_errors += 1
                    raise ReceiveError(f"消息体解码失败: {e}")
                
                # 5. 处理消息
                try:
                    await self.handler.handle(header, message)
                except Exception as e:
                    # 消息处理失败
                    self.stats.handler_errors += 1
                    raise ReceiveError(f"消息处理失败: {e}")
                
                # 6. 移除已处理的消息
                total_size = header.get('size', self.protocol._header_size + len(remaining))
                self._buffer = self._buffer[total_size:]
                
        except ReceiveError as e:
            logger.error(f"接收数据错误: {e}")
            self._buffer.clear()
        except Exception as e:
            logger.error(f"处理数据错误: {e}", exc_info=True)
            self._buffer.clear()
            
    async def send(self, message: Any, **header_fields: Any) -> None:
        """发送消息
        
        Args:
            message: 要发送的消息
            **header_fields: 额外的包头字段
        """
        if not self._connection:
            raise ProtocolManagerError("未设置连接")
            
        try:
            # 1. 编码消息
            try:
                header, body = self.protocol.encode_message(message)
            except Exception as e:
                # 消息编码失败
                self.stats.encode_errors += 1
                raise SendError(f"消息编码失败: {e}")
            
            # 2. 更新包头字段
            header.update(header_fields)
            header['size'] = self.protocol._header_size + len(body)
            
            # 3. 编码包头
            encoded_header = self.protocol.encode_header(header)
            
            # 4. 发送数据
            await self._connection.send(encoded_header + body)
            self.stats.total_sent += len(encoded_header) + len(body)
            
        except SendError as e:
            logger.error(f"发送消息错误: {e}")
            raise
        except Exception as e:
            logger.error(f"发送消息错误: {e}", exc_info=True)
            raise
