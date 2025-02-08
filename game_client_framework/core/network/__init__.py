"""网络模块

此模块提供了网络通信的核心功能，包括：

1. WebSocket 客户端
   - 异步消息收发
   - 自动重连
   - 连接状态管理

2. 连接池管理
   - 动态连接创建
   - 资源自动回收
   - 连接健康检查

3. 心跳机制
   - 可配置心跳间隔
   - 自动心跳管理
   - 超时检测
"""

from game_client_framework.core.network.internal import ConnectionPool, PoolConfig
from game_client_framework.core.network.websocket_connection import (
    WebSocketConnection, WebSocketConfig, WebSocketType
)
from game_client_framework.core.network.websocket_client import WebSocketClient

__all__ = [
    'WebSocketClient',
    'WebSocketConnection',
    'WebSocketConfig',
    'WebSocketType',
    'ConnectionPool',
    'PoolConfig'
]