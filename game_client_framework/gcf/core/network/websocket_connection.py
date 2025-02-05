from enum import Enum
import asyncio
import websockets
from dataclasses import dataclass
from typing import Optional, Type
from .connection import BaseConnection
from .protocol import BaseProtocol
from .heartbeat import BaseHeartbeat
from .packet import Packet
from ...exceptions import ConnectionError
from ...utils.logger import logger

class WebSocketType(Enum):
    """WebSocket连接类型"""
    WS = "ws"    # 普通WebSocket，用于测试环境
    WSS = "wss"  # 安全WebSocket，用于生产环境

@dataclass
class WebSocketConfig:
    """WebSocket连接配置"""
    host: str                           # 主机地址
    port: int                           # 端口
    ws_type: WebSocketType = WebSocketType.WS  # 连接类型，默认ws
    path: str = "/ws"                   # 路径
    auto_reconnect: int = 10            # 自动重连间隔（秒），0表示不自动重连
    connect_timeout: float = 20.0       # 连接超时时间（秒）

    def get_uri(self) -> str:
        """获取WebSocket URI"""
        return f"{self.ws_type.value}://{self.host}:{self.port}{self.path}"

class WebSocketConnection(BaseConnection):
    """WebSocket连接实现"""
    def __init__(self, protocol_class: Type[BaseProtocol], packet_class: Type[Packet], 
                 heartbeat_class: Optional[Type[BaseHeartbeat]] = None):
        super().__init__()
        self._ws = None
        self._packet = packet_class()
        self._protocol = protocol_class(self._packet)
        self._heartbeat = heartbeat_class() if heartbeat_class else None
        self._message_task = None
        self._reconnect_task = None
        
    async def _connect(self, config: WebSocketConfig) -> None:
        """实现WebSocket连接"""
        try:
            # 构建WebSocket URL
            url = config.get_uri()
            
            # 建立连接
            self._ws = await asyncio.wait_for(
                websockets.connect(url),
                timeout=config.connect_timeout
            )
            
            # 启动心跳
            if self._heartbeat:
                await self._heartbeat.start()
            
            # 启动消息处理
            self._message_task = asyncio.create_task(self._message_loop())
            
            # 如果配置了自动重连，启动重连任务
            if config.auto_reconnect > 0:
                self._reconnect_task = asyncio.create_task(self._auto_reconnect(config))
            
            logger.debug(f"WebSocket connected to {url}")
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect: {e}")

    async def _auto_reconnect(self, config: WebSocketConfig) -> None:
        """自动重连处理"""
        while True:
            try:
                if not self._ws or self._ws.closed:
                    logger.info(f"Attempting to reconnect in {config.auto_reconnect} seconds...")
                    await asyncio.sleep(config.auto_reconnect)
                    await self._connect(config)
                await asyncio.sleep(1)  # 检查间隔
            except Exception as e:
                logger.error(f"Reconnection failed: {e}")

    async def _disconnect(self) -> None:
        """实现WebSocket断开连接"""
        # 停止重连任务
        if self._reconnect_task:
            self._reconnect_task.cancel()
            self._reconnect_task = None
            
        # 停止消息处理
        if self._message_task:
            self._message_task.cancel()
            self._message_task = None
            
        # 停止心跳
        if self._heartbeat:
            await self._heartbeat.stop()
            
        # 关闭连接
        if self._ws:
            await self._ws.close()
            self._ws = None

    async def _send(self, data: bytes) -> None:
        """实现数据发送"""
        if not self._ws:
            raise ConnectionError("Not connected")
        await self._ws.send(data)

    async def _receive(self) -> bytes:
        """实现数据接收"""
        if not self._ws:
            raise ConnectionError("Not connected")
        data = await self._ws.recv()
        return data if isinstance(data, bytes) else data.encode()

    async def _message_loop(self) -> None:
        """消息处理循环"""
        try:
            while True:
                data = await self._receive()
                
                if self._heartbeat:
                    await self._heartbeat.handle_response(data)
                    
                await self._protocol.handle_message(data)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in message loop: {e}")
            await self.disconnect()
