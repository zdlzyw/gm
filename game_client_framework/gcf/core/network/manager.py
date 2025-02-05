from typing import Dict, Optional, List, Callable, Any
from asyncio import Task, create_task, gather, Lock
import asyncio
from .connection import BaseConnection, ConnectionState
from ...utils.logger import logger

class ConnectionManager:
    """连接管理器
    
    管理多个连接实例，提供连接的管理、监控等功能。
    支持自定义连接管理策略和并发控制。
    
    使用示例:
    ```python
    # 创建管理器
    manager = ConnectionManager(
        max_concurrent_operations=5,  # 最大并发操作数
        check_interval=5.0           # 检查间隔（秒）
    )
    
    # 自定义重连策略
    async def my_reconnect_strategy(conn: BaseConnection) -> None:
        await asyncio.sleep(5)  # 等待5秒后重连
        if not conn.is_connected:
            await conn.connect(conn._config)
            
    manager.set_reconnect_strategy(my_reconnect_strategy)
    
    # 添加连接
    manager.add_connection("main", main_conn)
    manager.add_connection("backup", backup_conn)
    
    # 开始监控（使用自定义间隔）
    manager.start_monitoring(check_interval=2.0)
    ```
    """
    def __init__(
        self,
        max_concurrent_operations: int = 10,
        check_interval: float = 1.0
    ):
        # 连接字典
        self._connections: Dict[str, BaseConnection] = {}
        self._connections_lock = Lock()  # 用于保护连接字典的访问
        
        # 监控配置
        self._monitor_task: Optional[Task] = None
        self._running = False
        self._check_interval = check_interval
        
        # 并发控制
        self._max_concurrent = max_concurrent_operations
        self._semaphore = asyncio.Semaphore(max_concurrent_operations)
        
        # 自定义策略
        self._reconnect_strategy: Optional[Callable[[BaseConnection], Any]] = None
        self._connection_check: Optional[Callable[[BaseConnection], bool]] = None
        
    async def add_connection(self, name: str, connection: BaseConnection) -> None:
        """添加连接到管理器（线程安全）"""
        async with self._connections_lock:
            if name in self._connections:
                raise ValueError(f"Connection '{name}' already exists")
                
            if not isinstance(connection, BaseConnection):
                raise TypeError(f"Connection must be an instance of BaseConnection")
                
            self._connections[name] = connection
            logger.info(f"Added connection: {name}")
            
    async def remove_connection(self, name: str) -> None:
        """移除连接（线程安全）"""
        async with self._connections_lock:
            if name in self._connections:
                del self._connections[name]
                logger.info(f"Removed connection: {name}")
                
    def set_reconnect_strategy(
        self, 
        strategy: Callable[[BaseConnection], Any]
    ) -> None:
        """设置重连策略"""
        self._reconnect_strategy = strategy
        
    def set_connection_check(
        self, 
        check: Callable[[BaseConnection], bool]
    ) -> None:
        """设置连接检查方法"""
        self._connection_check = check
        
    async def _safe_operation(self, operation: Callable, *args, **kwargs) -> None:
        """安全地执行操作（带并发控制）"""
        async with self._semaphore:
            try:
                await operation(*args, **kwargs)
            except Exception as e:
                logger.error(f"Operation failed: {e}", exc_info=True)
                
    async def connect_all(self) -> None:
        """并发连接所有未连接的连接"""
        async with self._connections_lock:
            connections = list(self._connections.values())
            
        tasks = []
        for conn in connections:
            if conn.state == ConnectionState.DISCONNECTED:
                tasks.append(self._safe_operation(conn.connect, conn._config))
                
        if tasks:
            await gather(*tasks)
            
    async def disconnect_all(self) -> None:
        """并发断开所有已连接的连接"""
        async with self._connections_lock:
            connections = list(self._connections.values())
            
        tasks = []
        for conn in connections:
            if conn.state == ConnectionState.CONNECTED:
                tasks.append(self._safe_operation(conn.disconnect))
                
        if tasks:
            await gather(*tasks)
            
    async def _check_connection(self, name: str, conn: BaseConnection) -> None:
        """检查单个连接的状态"""
        # 使用自定义检查方法（如果有）
        if self._connection_check and not self._connection_check(conn):
            logger.warning(f"Connection check failed: {name}")
            await self._safe_operation(conn.disconnect)
            return
            
        # 处理断开的连接
        if conn.state == ConnectionState.DISCONNECTED:
            if self._reconnect_strategy:
                await self._safe_operation(self._reconnect_strategy, conn)
                
    async def _monitor_connections(self) -> None:
        """监控所有连接的状态（考虑性能和并发）"""
        while self._running:
            async with self._connections_lock:
                connections = list(self._connections.items())
                
            # 并发检查所有连接
            tasks = [
                self._check_connection(name, conn)
                for name, conn in connections
            ]
            
            if tasks:
                await gather(*tasks)
                
            await asyncio.sleep(self._check_interval)
            
    def start_monitoring(self, check_interval: Optional[float] = None) -> None:
        """开始监控连接
        
        Args:
            check_interval: 可选，覆盖默认的检查间隔
        """
        if check_interval is not None:
            self._check_interval = check_interval
            
        if not self._running:
            self._running = True
            self._monitor_task = create_task(self._monitor_connections())
            logger.info(f"Started connection monitoring (interval: {self._check_interval}s)")
            
    def stop_monitoring(self) -> None:
        """停止监控连接"""
        if self._running:
            self._running = False
            if self._monitor_task:
                self._monitor_task.cancel()
            logger.info("Stopped connection monitoring")
            
    async def close(self) -> None:
        """关闭管理器（线程安全）"""
        self.stop_monitoring()
        await self.disconnect_all()
        async with self._connections_lock:
            self._connections.clear()
        logger.info("Connection manager closed")
