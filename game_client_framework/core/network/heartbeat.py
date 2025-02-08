"""心跳机制实现模块

此模块提供了心跳机制的基础实现，支持：
- 可配置的心跳间隔
- 自动心跳管理
- 心跳超时检测
- 资源优化管理
- 自定义心跳逻辑
- 状态回调机制
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List, Callable, Dict, Any
import asyncio
import time

from game_client_framework.exceptions import (
    HeartbeatError,
    HeartbeatStateError,
    HeartbeatTimeoutError
)
from game_client_framework.utils.logger import logger

class HeartbeatState(Enum):
    """心跳状态枚举
    
    Attributes:
        STOPPED: 心跳停止
        RUNNING: 心跳运行中
        PAUSED: 心跳暂停
        ERROR: 心跳错误
    """
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()
    ERROR = auto()

@dataclass
class HeartbeatConfig:
    """心跳配置
    
    Attributes:
        enabled (bool): 是否启用心跳
        interval (float): 心跳间隔（秒）
        timeout (float): 心跳超时时间（秒）
        max_missed (int): 允许的最大丢失次数
        auto_reconnect (bool): 是否自动重连
        custom_data (Dict): 自定义配置数据
    """
    enabled: bool = True
    interval: float = 30.0
    timeout: float = 10.0
    max_missed: int = 3
    auto_reconnect: bool = True
    custom_data: Dict[str, Any] = None
    
    def __post_init__(self):
        """验证配置参数"""
        if self.interval <= 0:
            raise HeartbeatConfigError("interval must be > 0")
        if self.timeout <= 0:
            raise HeartbeatConfigError("timeout must be > 0")
        if self.max_missed <= 0:
            raise HeartbeatConfigError("max_missed must be > 0")
        self.custom_data = self.custom_data or {}

class BaseHeartbeat(ABC):
    """心跳抽象基类
    
    提供心跳功能的基本框架，具体的心跳实现由子类完成。
    
    特性:
        - 状态管理
        - 生命周期回调
        - 错误处理
        - 自动重连机制
        - 自定义心跳逻辑
        
    Example:
        ```python
        class GameHeartbeat(BaseHeartbeat):
            async def _create_heartbeat_packet(self) -> bytes:
                # 创建游戏特定的心跳包
                return b'\\x01\\x02\\x03'
                
            async def _verify_heartbeat_response(self, data: bytes) -> bool:
                # 验证心跳响应
                return data == b'\\x03\\x02\\x01'
                
            async def _on_error(self, error: Exception) -> None:
                # 处理错误
                logger.error(f"Game heartbeat error: {error}")
        ```
    """
    def __init__(self, config: Optional[HeartbeatConfig] = None):
        """初始化心跳
        
        Args:
            config: 心跳配置，如果不提供则使用默认配置
        """
        self.config = config or HeartbeatConfig()
        self._state = HeartbeatState.STOPPED
        self._task: Optional[asyncio.Task] = None
        self._missed_count = 0
        self._last_beat_time = 0.0
        self._last_error: Optional[Exception] = None
        self._lock = asyncio.Lock()
        
        # 回调函数
        self._callbacks: Dict[str, List[Callable[..., Any]]] = {
            'before_start': [],     # 启动前
            'after_start': [],      # 启动后
            'before_stop': [],      # 停止前
            'after_stop': [],       # 停止后
            'on_beat': [],          # 心跳时
            'on_response': [],      # 收到响应时
            'on_error': [],         # 发生错误时
            'on_state_change': [],  # 状态变更时
        }
        
    def add_callback(self, event: str, callback: Callable[..., Any]) -> None:
        """添加回调函数
        
        Args:
            event: 事件类型
            callback: 回调函数
            
        Raises:
            ValueError: 未知的事件类型
        """
        if event in self._callbacks:
            self._callbacks[event].append(callback)
        else:
            raise ValueError(f"Unknown event type: {event}")
            
    async def _trigger_callbacks(self, event: str, *args, **kwargs) -> None:
        """触发回调函数"""
        for callback in self._callbacks.get(event, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(*args, **kwargs)
                else:
                    callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in heartbeat callback ({event}): {e}")
                
    @property
    def state(self) -> HeartbeatState:
        """当前心跳状态"""
        return self._state
        
    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._state == HeartbeatState.RUNNING
        
    @property
    def last_error(self) -> Optional[Exception]:
        """最后一次错误"""
        return self._last_error
        
    async def start(self) -> None:
        """启动心跳
        
        Raises:
            HeartbeatStateError: 心跳已经在运行
        """
        async with self._lock:
            if not self.config.enabled:
                return
                
            if self._task and not self._task.done():
                raise HeartbeatStateError("Heartbeat is already running")
                
            await self._trigger_callbacks('before_start')
            self._missed_count = 0
            self._last_error = None
            self._state = HeartbeatState.RUNNING
            self._task = asyncio.create_task(self._heartbeat_loop())
            await self._trigger_callbacks('after_start')
            
    async def stop(self) -> None:
        """停止心跳"""
        async with self._lock:
            if not self._task:
                return
                
            await self._trigger_callbacks('before_stop')
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
            self._state = HeartbeatState.STOPPED
            await self._trigger_callbacks('after_stop')
            
    async def pause(self) -> None:
        """暂停心跳"""
        if self._state != HeartbeatState.RUNNING:
            return
        self._state = HeartbeatState.PAUSED
        await self._trigger_callbacks('on_state_change', HeartbeatState.PAUSED)
        
    async def resume(self) -> None:
        """恢复心跳"""
        if self._state != HeartbeatState.PAUSED:
            return
        self._state = HeartbeatState.RUNNING
        await self._trigger_callbacks('on_state_change', HeartbeatState.RUNNING)
            
    async def _heartbeat_loop(self) -> None:
        """心跳循环"""
        while True:
            try:
                if self._state == HeartbeatState.PAUSED:
                    await asyncio.sleep(1)
                    continue
                    
                # 发送心跳
                await self._trigger_callbacks('on_beat')
                packet = await self._create_heartbeat_packet()
                await self._send_heartbeat(packet)
                self._last_beat_time = time.time()
                
                # 等待响应
                try:
                    response = await asyncio.wait_for(
                        self._wait_heartbeat_response(),
                        timeout=self.config.timeout
                    )
                    
                    if await self._verify_heartbeat_response(response):
                        await self._trigger_callbacks('on_response')
                        self._missed_count = 0
                    else:
                        raise HeartbeatError("Invalid heartbeat response")
                        
                except asyncio.TimeoutError:
                    self._missed_count += 1
                    logger.warning(f"Heartbeat timeout, missed count: {self._missed_count}")
                    if self._missed_count >= self.config.max_missed:
                        raise HeartbeatTimeoutError(f"Missed {self._missed_count} heartbeats")
                
                # 等待下一次心跳
                await asyncio.sleep(self.config.interval)
                
            except asyncio.CancelledError:
                break
                
            except Exception as e:
                self._last_error = e
                self._state = HeartbeatState.ERROR
                await self._trigger_callbacks('on_error', e)
                await self._on_error(e)
                
                if self.config.auto_reconnect:
                    logger.info("Attempting to restart heartbeat...")
                    await asyncio.sleep(self.config.interval)
                    self._state = HeartbeatState.RUNNING
                else:
                    break
    
    @abstractmethod
    async def _create_heartbeat_packet(self) -> bytes:
        """创建心跳包
        
        Returns:
            bytes: 心跳包数据
        """
        pass
        
    @abstractmethod
    async def _send_heartbeat(self, packet: bytes) -> None:
        """发送心跳包
        
        Args:
            packet: 心跳包数据
        """
        pass
        
    @abstractmethod
    async def _wait_heartbeat_response(self) -> bytes:
        """等待心跳响应
        
        Returns:
            bytes: 心跳响应数据
        """
        pass
        
    @abstractmethod
    async def _verify_heartbeat_response(self, response: bytes) -> bool:
        """验证心跳响应
        
        Args:
            response: 心跳响应数据
            
        Returns:
            bool: 响应是否有效
        """
        pass
        
    @abstractmethod
    async def _on_error(self, error: Exception) -> None:
        """处理心跳错误
        
        Args:
            error: 错误信息
        """
        pass