"""WebSocket连接实现模块

此模块提供了基于WebSocket协议的连接实现，支持：
- 安全和非安全的WebSocket连接
- 消息的异步收发
- 心跳机制
- 连接状态管理
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Type, Any
import asyncio
import websockets

from game_client_framework.core.network.internal.connection import BaseConnection
from game_client_framework.core.network.heartbeat import BaseHeartbeat
from game_client_framework.core.protocol.packet import Packet
from game_client_framework.core.protocol.base import BaseProtocol
from game_client_framework.exceptions import ConnectionError, ConnectionTimeoutError
from game_client_framework.utils.logger import logger

class WebSocketType(Enum):
    """WebSocket连接类型
    
    Attributes:
        WS: 普通WebSocket连接，用于测试环境
        WSS: 安全WebSocket连接，用于生产环境
    """
    WS = "ws"    # 普通WebSocket
    WSS = "wss"  # 安全WebSocket

@dataclass
class WebSocketConfig:
    """WebSocket连接配置
    
    Attributes:
        host (str): 主机地址
        port (int): 端口号
        ws_type (WebSocketType): 连接类型，默认为WS
        path (str): WebSocket路径，默认为"/ws"
        connect_timeout (float): 连接超时时间（秒），默认为20秒
        
    Example:
        ```python
        config = WebSocketConfig(
            host="game.example.com",
            port=8080,
            ws_type=WebSocketType.WSS,
            path="/game/ws"
        )
        ```
    """
    host: str
    port: int
    ws_type: WebSocketType = WebSocketType.WS
    path: str = "/ws"
    connect_timeout: float = 20.0

    def get_uri(self) -> str:
        """获取WebSocket URI
        
        Returns:
            str: 完整的WebSocket URI
        """
        return f"{self.ws_type.value}://{self.host}:{self.port}{self.path}"

class WebSocketConnection(BaseConnection):
    """WebSocket连接实现
    
    提供基于WebSocket协议的连接实现，支持：
    - 异步消息收发
    - 心跳机制
    - 连接状态管理
    - 健康检查
    
    Example:
        ```python
        conn = WebSocketConnection(
            protocol_class=GameProtocol,
            packet_class=GamePacket
        )
        
        # 连接到服务器
        await conn.connect(config)
        
        # 发送数据
        await conn.send(data)
        
        # 接收数据
        response = await conn.receive()
        ```
    """
    def __init__(
        self,
        protocol_class: Type[BaseProtocol],
        packet_class: Type[Packet],
        heartbeat_class: Optional[Type[BaseHeartbeat]] = None
    ):
        """初始化WebSocket连接
        
        Args:
            protocol_class: 协议类
            packet_class: 数据包类
            heartbeat_class: 心跳类（可选）
        """
        super().__init__()
        self._ws = None
        self._packet = packet_class()
        self._protocol = protocol_class(self._packet)
        self._heartbeat = heartbeat_class() if heartbeat_class else None
        self._message_task: Optional[asyncio.Task] = None
        self._config: Optional[WebSocketConfig] = None
        
    async def _connect(self, config: WebSocketConfig) -> None:
        """实现WebSocket连接
        
        Args:
            config: WebSocket连接配置
            
        Raises:
            ConnectionError: 连接失败时抛出
            ConnectionTimeoutError: 连接超时时抛出
        """
        try:
            self._config = config
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
            
            logger.debug(f"WebSocket connected to {url}")
            
        except asyncio.TimeoutError as e:
            raise ConnectionTimeoutError(f"Connection timeout after {config.connect_timeout}s")
        except Exception as e:
            raise ConnectionError(f"Failed to connect: {e}")

    async def _disconnect(self) -> None:
        """实现WebSocket断开连接"""
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
            
        logger.debug("WebSocket disconnected")

    async def _send(self, data: Any) -> None:
        """实现数据发送
        
        Args:
            data: 要发送的数据
            
        Raises:
            ConnectionError: 发送失败时抛出
        """
        if not self._ws:
            raise ConnectionError("Not connected")
            
        try:
            # 使用协议编码数据
            encoded_data = self._protocol.encode(data)
            await self._ws.send(encoded_data)
        except Exception as e:
            raise ConnectionError(f"Failed to send data: {e}")

    async def _receive(self) -> Any:
        """实现数据接收
        
        Returns:
            接收到的数据
            
        Raises:
            ConnectionError: 接收失败时抛出
        """
        if not self._ws:
            raise ConnectionError("Not connected")
            
        try:
            data = await self._ws.recv()
            # 使用协议解码数据
            return self._protocol.decode(data)
        except Exception as e:
            raise ConnectionError(f"Failed to receive data: {e}")

    async def _message_loop(self) -> None:
        """消息处理循环"""
        try:
            while True:
                if not self._ws:
                    break
                try:
                    message = await self._ws.recv()
                    # 处理消息...
                except websockets.ConnectionClosed:
                    break
                except Exception as e:
                    logger.error(f"Error in message loop: {e}")
                    break
        finally:
            await self._handle_connection_lost()

    async def _handle_connection_lost(self) -> None:
        """处理连接丢失"""
        logger.warning("Connection lost")
        await self._disconnect()
        
    @property
    def is_healthy(self) -> bool:
        """检查连接是否健康
        
        Returns:
            bool: 连接是否健康
        """
        return (
            self._ws is not None and 
            not self._ws.closed and 
            self._state_manager.is_connected
        )
        
    async def reset(self) -> None:
        """重置连接状态
        
        用于连接池复用连接时重置状态。
        """
        await self._disconnect()
        if self._config:
            await self._connect(self._config)
