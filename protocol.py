from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, Awaitable
import asyncio
import logging
from .packet import BasePacket

# 消息处理器类型
MessageHandler = Callable[[int, Dict[str, Any]], Awaitable[None]]

class BaseProtocol(ABC):
    """协议处理基类"""
    def __init__(self, packet: BasePacket):
        self._packet = packet
        self._handlers: Dict[int, MessageHandler] = {}
        self._default_handler: Optional[MessageHandler] = None
        self._logger = logging.getLogger(self.__class__.__name__)
        
    def register_handler(self, message_id: int, handler: MessageHandler) -> None:
        """注册消息处理器
        
        Args:
            message_id: 消息ID
            handler: 处理器函数
        """
        self._handlers[message_id] = handler
        
    def register_default_handler(self, handler: MessageHandler) -> None:
        """注册默认消息处理器"""
        self._default_handler = handler
        
    async def handle_message(self, data: bytes) -> None:
        """处理接收到的消息
        
        Args:
            data: 接收到的字节数据
        """
        try:
            # 解包数据
            message_id, message_data = self._packet.unpack(data)
            
            # 查找处理器
            handler = self._handlers.get(message_id)
            if handler:
                await handler(message_id, message_data)
            elif self._default_handler:
                await self._default_handler(message_id, message_data)
            else:
                self._logger.warning(f"No handler for message {message_id}")
                
        except Exception as e:
            self._logger.error(f"Error handling message: {e}", exc_info=True)
            
    def encode(self, message_id: int, data: Dict[str, Any]) -> bytes:
        """编码消息
        
        Args:
            message_id: 消息ID
            data: 要编码的数据
            
        Returns:
            bytes: 编码后的字节数据
        """
        return self._packet.pack(message_id, data)
        
    def decode(self, data: bytes) -> tuple[int, Dict[str, Any]]:
        """解码消息
        
        Args:
            data: 要解码的字节数据
            
        Returns:
            tuple[int, Dict[str, Any]]: 消息ID和解码后的数据
        """
        return self._packet.unpack(data)