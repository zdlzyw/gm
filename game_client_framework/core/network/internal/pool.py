"""连接池模块

此模块提供了通用的连接池实现，支持：
1. 连接的动态创建和回收
2. 自动的资源管理
3. 连接健康检查
4. 异步操作支持
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Any, Dict

from game_client_framework.exceptions import (
    PoolError,
    PoolEmptyError,
    PoolAcquireTimeoutError,
    PoolConfigError,
    PoolConnectionError
)
from game_client_framework.utils.logger import logger

@dataclass
class PoolConfig:
    """连接池配置
    
    属性:
        min_size (int): 最小连接数，默认为1
        max_size (int): 最大连接数，默认为10
        acquire_timeout (float): 获取连接的超时时间（秒），默认为30秒
        idle_timeout (float): 空闲连接的超时时间（秒），默认为60秒
        max_lifetime (float): 连接的最大生命周期（秒），默认为3600秒
        health_check_interval (float): 健康检查间隔（秒），默认为30秒
    
    示例:
        ```python
        # 创建一个适合单任务的配置
        config = PoolConfig(
            min_size=1,
            max_size=2,
            idle_timeout=30.0
        )
        
        # 创建一个适合批量任务的配置
        config = PoolConfig(
            min_size=5,
            max_size=20,
            idle_timeout=300.0
        )
        ```
    """
    min_size: int = 1
    max_size: int = 10
    acquire_timeout: float = 30.0
    idle_timeout: float = 60.0
    max_lifetime: float = 3600.0
    health_check_interval: float = 30.0
    
    def __post_init__(self):
        """验证配置参数的有效性"""
        if self.min_size < 0:
            raise PoolConfigError("min_size must be >= 0")
        if self.max_size < self.min_size:
            raise PoolConfigError("max_size must be >= min_size")
        if self.acquire_timeout <= 0:
            raise PoolConfigError("acquire_timeout must be > 0")
        if self.idle_timeout <= 0:
            raise PoolConfigError("idle_timeout must be > 0")
        if self.max_lifetime <= 0:
            raise PoolConfigError("max_lifetime must be > 0")
        if self.health_check_interval <= 0:
            raise PoolConfigError("health_check_interval must be > 0")

@dataclass
class PooledConnection:
    """池化连接包装器
    
    为连接对象添加池化所需的元数据。
    
    属性:
        connection: 实际的连接对象
        created_at (float): 创建时间戳
        last_used_at (float): 最后使用时间戳
        usage_count (int): 使用次数
        is_busy (bool): 是否正在使用中
    """
    connection: Any
    created_at: float = field(default_factory=time.time)
    last_used_at: float = field(default_factory=time.time)
    usage_count: int = 0
    is_busy: bool = False
    
    @property
    def idle_time(self) -> float:
        """获取空闲时间（秒）"""
        return time.time() - self.last_used_at
        
    @property
    def lifetime(self) -> float:
        """获取生命时间（秒）"""
        return time.time() - self.created_at

class ConnectionPool:
    """异步连接池
    
    提供连接的创建、获取、释放和管理功能。
    
    属性:
        size (int): 当前连接池大小
        active_connections (int): 当前活跃连接数
        idle_connections (int): 当前空闲连接数
        
    示例:
        ```python
        # 创建连接池
        pool = ConnectionPool(
            factory=create_connection,  # 连接工厂函数
            config=PoolConfig(min_size=1, max_size=10)
        )
        
        # 获取连接
        async with pool.acquire() as conn:
            # 使用连接
            await conn.send(data)
            response = await conn.receive()
        ```
    """
    def __init__(
        self,
        factory: Callable[[], Any],
        config: Optional[PoolConfig] = None,
        lazy_init: bool = True
    ):
        """初始化连接池
        
        参数:
            factory: 创建新连接的工厂函数
            config: 连接池配置，如果不提供则使用默认配置
            lazy_init: 是否使用懒加载模式，默认为True
        """
        self._factory = factory
        self._config = config or PoolConfig()
        self._connections: List[PooledConnection] = []
        self._lock = asyncio.Lock()
        self._condition = asyncio.Condition(self._lock)
        self._cleanup_task: Optional[asyncio.Task] = None
        self._last_cleanup = time.time()
        
        if not lazy_init:
            # 非懒加载模式，立即创建最小连接数
            asyncio.create_task(self._init_connections())
            
    async def _init_connections(self) -> None:
        """初始化连接池，创建最小数量的连接"""
        async with self._lock:
            while len(self._connections) < self._config.min_size:
                try:
                    conn = await self._create_connection()
                    self._connections.append(conn)
                except Exception as e:
                    logger.error(f"Failed to create initial connection: {e}")
                    break
                    
    async def _create_connection(self) -> PooledConnection:
        """创建新的连接"""
        try:
            connection = self._factory()
            return PooledConnection(connection=connection)
        except Exception as e:
            raise PoolConnectionError(f"Failed to create connection: {e}")
            
    async def acquire(self) -> Any:
        """获取一个连接
        
        如果没有可用连接且未达到最大连接数，会创建新连接。
        如果达到最大连接数，将等待直到有连接可用或超时。
        
        返回:
            连接对象
            
        异常:
            PoolEmptyError: 无法获取连接
            PoolAcquireTimeoutError: 获取连接超时
        """
        async with self._lock:
            # 尝试获取空闲连接
            connection = await self._get_idle_connection()
            if connection:
                return connection.connection
                
            # 如果没有空闲连接且未达到最大连接数，创建新连接
            if len(self._connections) < self._config.max_size:
                connection = await self._create_connection()
                self._connections.append(connection)
                connection.is_busy = True
                return connection.connection
                
            # 等待空闲连接
            try:
                async with asyncio.timeout(self._config.acquire_timeout):
                    while True:
                        await self._condition.wait()
                        connection = await self._get_idle_connection()
                        if connection:
                            return connection.connection
            except asyncio.TimeoutError:
                raise PoolAcquireTimeoutError(
                    f"Timeout waiting for connection after {self._config.acquire_timeout}s"
                )
                
    async def release(self, connection: Any) -> None:
        """释放连接回连接池
        
        参数:
            connection: 要释放的连接对象
        """
        async with self._lock:
            for pooled_conn in self._connections:
                if pooled_conn.connection == connection:
                    pooled_conn.is_busy = False
                    pooled_conn.last_used_at = time.time()
                    pooled_conn.usage_count += 1
                    self._condition.notify()
                    await self._maybe_cleanup()
                    break
                    
    async def _get_idle_connection(self) -> Optional[PooledConnection]:
        """获取一个空闲连接"""
        for connection in self._connections:
            if not connection.is_busy:
                connection.is_busy = True
                connection.last_used_at = time.time()
                return connection
        return None
        
    async def _maybe_cleanup(self) -> None:
        """检查是否需要清理连接"""
        now = time.time()
        if now - self._last_cleanup < self._config.health_check_interval:
            return
            
        self._last_cleanup = now
        await self._cleanup()
        
    async def _cleanup(self) -> None:
        """清理过期和空闲连接"""
        to_remove = []
        for conn in self._connections:
            if not conn.is_busy:
                if (
                    conn.idle_time > self._config.idle_timeout or
                    conn.lifetime > self._config.max_lifetime
                ):
                    to_remove.append(conn)
                    
        # 保持最小连接数
        if len(self._connections) - len(to_remove) < self._config.min_size:
            to_remove = to_remove[:(len(self._connections) - self._config.min_size)]
            
        for conn in to_remove:
            self._connections.remove(conn)
            
    @property
    def size(self) -> int:
        """当前连接池大小"""
        return len(self._connections)
        
    @property
    def active_connections(self) -> int:
        """当前活跃连接数"""
        return sum(1 for conn in self._connections if conn.is_busy)
        
    @property
    def idle_connections(self) -> int:
        """当前空闲连接数"""
        return sum(1 for conn in self._connections if not conn.is_busy)
        
    async def close(self) -> None:
        """关闭连接池
        
        关闭所有连接并清理资源。
        """
        async with self._lock:
            for conn in self._connections:
                if hasattr(conn.connection, 'close'):
                    await conn.connection.close()
            self._connections.clear()
            
    async def __aenter__(self) -> 'ConnectionPool':
        """异步上下文管理器入口"""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """异步上下文管理器出口"""
        await self.close()
