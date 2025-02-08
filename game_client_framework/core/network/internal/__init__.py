"""内部网络组件包

此包包含框架内部使用的网络核心组件：

1. 连接池
   - 连接池配置
   - 连接池管理器
   - 池化连接包装器

2. 基础连接
   - 连接状态管理
   - 连接生命周期
   - 错误处理
"""

from game_client_framework.core.network.internal.pool import (
    ConnectionPool, PoolConfig, PooledConnection
)
from game_client_framework.core.network.internal.connection import (
    BaseConnection, ConnectionState
)

__all__ = [
    'ConnectionPool',
    'PoolConfig',
    'PooledConnection',
    'BaseConnection',
    'ConnectionState'
]
