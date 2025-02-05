from abc import ABC, abstractmethod
import asyncio
from typing import Optional
from dataclasses import dataclass
from ...exceptions import HeartbeatError
from ...utils.logger import logger

@dataclass
class HeartbeatConfig:
    """心跳配置"""
    enabled: bool = False           # 是否启用心跳
    interval: float = 30.0         # 心跳间隔（秒）
    timeout: float = 10.0          # 心跳超时时间（秒）
    max_missed: int = 3           # 允许连续丢失的心跳次数

class BaseHeartbeat(ABC):
    """心跳抽象基类
    
    提供心跳功能的基本框架，具体的心跳实现由子类完成。
    """
    def __init__(self, config: HeartbeatConfig):
        self.config = config
        self._task: Optional[asyncio.Task] = None
        self._missed_count: int = 0
        
    async def start(self) -> None:
        """启动心跳"""
        if not self.config.enabled:
            return
            
        if self._task:
            self._task.cancel()
            
        self._missed_count = 0
        self._task = asyncio.create_task(self._heartbeat_loop())
        
    async def stop(self) -> None:
        """停止心跳"""
        if self._task:
            self._task.cancel()
            self._task = None
            
    async def _heartbeat_loop(self) -> None:
        """心跳循环
        
        处理基本的心跳逻辑：
        1. 按照指定间隔发送心跳
        2. 检查心跳响应
        3. 处理心跳超时
        4. 处理连续失败
        """
        while True:
            try:
                # 发送心跳
                await self._send_heartbeat()
                
                # 等待响应
                try:
                    await asyncio.wait_for(
                        self._wait_response(),
                        timeout=self.config.timeout
                    )
                    # 心跳成功，重置计数
                    self._missed_count = 0
                    
                except asyncio.TimeoutError:
                    # 心跳超时
                    self._missed_count += 1
                    logger.warning(
                        f"Heartbeat timeout, missed count: {self._missed_count}"
                    )
                    
                    if self._missed_count >= self.config.max_missed:
                        raise HeartbeatError(
                            f"Missed {self._missed_count} heartbeats"
                        )
                
                # 等待下一次心跳
                await asyncio.sleep(self.config.interval)
                
            except asyncio.CancelledError:
                # 心跳被取消
                break
            except Exception as e:
                # 其他错误，通知上层处理
                logger.error(f"Heartbeat error: {e}")
                await self._on_error(e)
                break
    
    @abstractmethod
    async def _send_heartbeat(self) -> None:
        """发送心跳包
        
        由子类实现具体的心跳包发送逻辑
        """
        pass
        
    @abstractmethod
    async def _wait_response(self) -> None:
        """等待心跳响应
        
        由子类实现具体的响应等待逻辑
        """
        pass
        
    @abstractmethod
    async def _on_error(self, error: Exception) -> None:
        """处理心跳错误
        
        由子类实现具体的错误处理逻辑
        """
        pass
