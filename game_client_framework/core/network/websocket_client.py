"""WebSocket客户端模块

此模块提供了WebSocket客户端的高层封装，支持：
- 连接池管理
- 自动重连
- 简单的消息收发接口
- 异步操作
"""

from dataclasses import dataclass, field
from typing import Optional, Type, Any, Dict
import asyncio

from game_client_framework.core.network.internal import ConnectionPool, PoolConfig
from game_client_framework.core.network.websocket_connection import (
    WebSocketConnection, WebSocketConfig, WebSocketType
)
from game_client_framework.core.protocol.base import BaseProtocol
from game_client_framework.core.protocol.packet import Packet
from game_client_framework.core.network.heartbeat import BaseHeartbeat
from game_client_framework.exceptions import ConnectionError, PoolEmptyError
from game_client_framework.utils.logger import logger

@dataclass
class WebSocketClientConfig:
    """WebSocket客户端配置
    
    Attributes:
        pool_config (PoolConfig): 连接池配置
        connection_config (WebSocketConfig): 连接配置
        protocol_class (Type[BaseProtocol]): 协议类
        packet_class (Type[Packet]): 数据包类
        heartbeat_class (Optional[Type[BaseHeartbeat]]): 心跳类（可选）
        custom_data (Dict): 自定义配置数据
    """
    pool_config: PoolConfig = field(default_factory=lambda: PoolConfig(
        min_size=1,
        max_size=10,
        idle_timeout=300.0  # 5分钟
    ))
    connection_config: WebSocketConfig = field(default_factory=lambda: WebSocketConfig(
        host="localhost",
        port=8080,
        ws_type=WebSocketType.WS,
        path="/ws"
    ))
    protocol_class: Type[BaseProtocol] = None
    packet_class: Type[Packet] = None
    heartbeat_class: Optional[Type[BaseHeartbeat]] = None
    custom_data: Dict = field(default_factory=dict)

class WebSocketClient:
    """WebSocket客户端
    
    提供简单的接口进行消息收发，自动管理连接池。
    
    Example:
        ```python
        # 创建客户端
        client = WebSocketClient(WebSocketClientConfig(
            connection_config=WebSocketConfig(
                host="game.example.com",
                port=8080,
                ws_type=WebSocketType.WSS
            ),
            protocol_class=GameProtocol,
            packet_class=GamePacket
        ))
        
        # 发送消息
        response = await client.send(message)
        
        # 接收消息
        message = await client.receive()
        
        # 使用with语句
        async with client.connection() as conn:
            await conn.send(message)
            response = await conn.receive()
        ```
    """
    def __init__(self, config: WebSocketClientConfig):
        """初始化客户端
        
        Args:
            config: 客户端配置
        """
        self._config = config
        self._pool: Optional[ConnectionPool] = None
        self._lock = asyncio.Lock()
        
    async def start(self) -> None:
        """启动客户端
        
        初始化连接池并建立初始连接。
        """
        if self._pool is not None:
            return
            
        async with self._lock:
            if self._pool is not None:  # 双重检查
                return
                
            # 创建连接池
            self._pool = ConnectionPool(
                factory=self._create_connection,
                config=self._config.pool_config
            )
            
            logger.info("WebSocket client started")
            
    async def stop(self) -> None:
        """停止客户端
        
        关闭所有连接并清理资源。
        """
        if self._pool is None:
            return
            
        async with self._lock:
            if self._pool is None:  # 双重检查
                return
                
            await self._pool.close()
            self._pool = None
            
            logger.info("WebSocket client stopped")
            
    async def _create_connection(self) -> WebSocketConnection:
        """创建新的WebSocket连接
        
        Returns:
            WebSocketConnection: 新创建的连接
        """
        connection = WebSocketConnection(
            protocol_class=self._config.protocol_class,
            packet_class=self._config.packet_class,
            heartbeat_class=self._config.heartbeat_class
        )
        await connection.connect(self._config.connection_config)
        return connection
        
    async def send(self, data: Any) -> None:
        """发送数据
        
        Args:
            data: 要发送的数据
            
        Raises:
            ConnectionError: 发送失败
            PoolEmptyError: 无法获取连接
        """
        async with self.connection() as conn:
            await conn.send(data)
            
    async def receive(self) -> Any:
        """接收数据
        
        Returns:
            接收到的数据
            
        Raises:
            ConnectionError: 接收失败
            PoolEmptyError: 无法获取连接
        """
        async with self.connection() as conn:
            return await conn.receive()
            
    def connection(self):
        """获取连接上下文管理器
        
        Returns:
            ConnectionContext: 连接上下文管理器
            
        Example:
            ```python
            async with client.connection() as conn:
                await conn.send(data)
                response = await conn.receive()
            ```
        """
        return ConnectionContext(self)
        
    async def _acquire_connection(self) -> WebSocketConnection:
        """获取连接
        
        Returns:
            WebSocketConnection: 获取到的连接
            
        Raises:
            PoolEmptyError: 无法获取连接
        """
        if self._pool is None:
            await self.start()
        return await self._pool.acquire()
        
    async def _release_connection(self, connection: WebSocketConnection) -> None:
        """释放连接
        
        Args:
            connection: 要释放的连接
        """
        if self._pool is not None:
            await self._pool.release(connection)
            
    @property
    def is_running(self) -> bool:
        """客户端是否正在运行"""
        return self._pool is not None
        
    @property
    def active_connections(self) -> int:
        """当前活跃连接数"""
        return self._pool.active_connections if self._pool else 0
        
    @property
    def idle_connections(self) -> int:
        """当前空闲连接数"""
        return self._pool.idle_connections if self._pool else 0

class ConnectionContext:
    """连接上下文管理器
    
    用于自动获取和释放连接。
    """
    def __init__(self, client: WebSocketClient):
        self._client = client
        self._connection: Optional[WebSocketConnection] = None
        
    async def __aenter__(self) -> WebSocketConnection:
        """进入上下文"""
        self._connection = await self._client._acquire_connection()
        return self._connection
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """退出上下文"""
        if self._connection:
            await self._client._release_connection(self._connection)
            self._connection = None
