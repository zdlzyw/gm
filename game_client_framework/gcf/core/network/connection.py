from abc import ABC, abstractmethod
import asyncio
from typing import Optional, Any, Callable, Dict, List
from enum import Enum, auto
from ...exceptions import (
    ConnectionError,
    ConnectionStateError,
    ConnectionTimeoutError,
    ConnectionClosedError,
    SendError,
    ReceiveError
)
from ...utils.logger import logger

class ConnectionState(Enum):
    """连接状态"""
    DISCONNECTED = auto()  # 自动分配为 1
    CONNECTING = auto()    # 自动分配为 2
    CONNECTED = auto()     # 自动分配为 3
    DISCONNECTING = auto() # 自动分配为 4

# 回调函数类型定义
ConnectionCallback = Callable[[], None]
StateChangeCallback = Callable[[ConnectionState, ConnectionState], None]
DataCallback = Callable[[bytes], None]
ErrorCallback = Callable[[Exception], None]

class ConnectionStateManager:
    """状态管理器
    
    负责管理连接状态和状态变更回调
    """
    def __init__(self):
        self._state = ConnectionState.DISCONNECTED
        self._callbacks: List[StateChangeCallback] = []
        
    def set_state(self, new_state: ConnectionState) -> None:
        """设置新状态并触发回调"""
        if new_state != self._state:
            old_state = self._state
            self._state = new_state
            for callback in self._callbacks:
                try:
                    callback(old_state, new_state)
                except Exception as e:
                    logger.error(f"State change callback error: {e}", exc_info=True)
                    
    def add_listener(self, callback: StateChangeCallback) -> None:
        """添加状态变更监听器"""
        self._callbacks.append(callback)
        
    @property
    def state(self) -> ConnectionState:
        return self._state
        
    @property
    def is_connected(self) -> bool:
        return self._state == ConnectionState.CONNECTED

class BaseConnection(ABC):
    """连接基类
    
    处理基础的连接功能，如连接、断开、发送和接收数据等
    提供生命周期回调机制，方便业务层处理连接事件
    """
    def __init__(self):
        # 状态管理
        self._state_manager = ConnectionStateManager()
        
        # 最后一次错误
        self._last_error: Optional[Exception] = None
        
        # 重连次数
        self._reconnect_count: int = 0
        
        # 回调函数字典
        self._callbacks: Dict[str, List[Callable]] = {
            'before_connect': [],    # 连接前
            'after_connect': [],     # 连接后
            'before_disconnect': [], # 断开前
            'after_disconnect': [],  # 断开后
            'before_send': [],       # 发送前
            'after_send': [],        # 发送后
            'on_receive': [],        # 接收到数据
            'on_error': []           # 发生错误
        }
        
    def _trigger_callback(self, name: str, *args, **kwargs) -> None:
        """触发指定回调"""
        for callback in self._callbacks.get(name, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Callback error: {e}", exc_info=True)
                
    # 回调注册方法
    def on_before_connect(self, callback: ConnectionCallback) -> None:
        """注册连接前回调"""
        self._callbacks['before_connect'].append(callback)
        
    def on_after_connect(self, callback: ConnectionCallback) -> None:
        """注册连接后回调"""
        self._callbacks['after_connect'].append(callback)
        
    def on_before_disconnect(self, callback: ConnectionCallback) -> None:
        """注册断开前回调"""
        self._callbacks['before_disconnect'].append(callback)
        
    def on_after_disconnect(self, callback: ConnectionCallback) -> None:
        """注册断开后回调"""
        self._callbacks['after_disconnect'].append(callback)
        
    def on_state_change(self, callback: StateChangeCallback) -> None:
        """注册状态变更回调"""
        self._state_manager.add_listener(callback)
        
    def on_before_send(self, callback: DataCallback) -> None:
        """注册发送前回调"""
        self._callbacks['before_send'].append(callback)
        
    def on_after_send(self, callback: DataCallback) -> None:
        """注册发送后回调"""
        self._callbacks['after_send'].append(callback)
        
    def on_receive(self, callback: DataCallback) -> None:
        """注册数据接收回调"""
        self._callbacks['on_receive'].append(callback)
        
    def on_error(self, callback: ErrorCallback) -> None:
        """注册错误回调"""
        self._callbacks['on_error'].append(callback)
        
    @property
    def state(self) -> ConnectionState:
        """获取当前连接状态"""
        return self._state_manager.state
    
    @property
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._state_manager.is_connected
    
    @property
    def last_error(self) -> Optional[Exception]:
        """获取最后一次错误"""
        return self._last_error
        
    async def connect(self, config: Any) -> bool:
        """建立连接
        
        Args:
            config: 连接配置，由具体实现类定义
            
        Returns:
            bool: 连接是否成功
            
        Raises:
            ConnectionStateError: 当前状态不允许连接
            ConnectionTimeoutError: 连接超时
            ConnectionError: 连接过程中发生错误
        """
        if self.state != ConnectionState.DISCONNECTED:
            error = ConnectionStateError(f"Cannot connect in {self.state} state")
            logger.log_error(error)
            raise error
            
        self._trigger_callback('before_connect')
        self._state_manager.set_state(ConnectionState.CONNECTING)
        logger.info(f"Connecting with config: {config}")
        
        try:
            await self._connect(config)
            self._state_manager.set_state(ConnectionState.CONNECTED)
            self._reconnect_count = 0
            logger.info("Connection established")
            self._trigger_callback('after_connect')
            return True
        except asyncio.TimeoutError as e:
            error = ConnectionTimeoutError("Connection timed out", cause=e)
            logger.log_error(error)
            self._state_manager.set_state(ConnectionState.DISCONNECTED)
            self._trigger_callback('on_error', error)
            raise error
        except Exception as e:
            error = ConnectionError("Failed to connect", cause=e)
            logger.log_error(error)
            self._state_manager.set_state(ConnectionState.DISCONNECTED)
            self._trigger_callback('on_error', error)
            raise error
            
    async def disconnect(self) -> None:
        """断开连接
        
        Raises:
            ConnectionStateError: 当前状态不允许断开
            ConnectionError: 断开过程中发生错误
        """
        if self.state not in (ConnectionState.CONNECTED, ConnectionState.CONNECTING):
            error = ConnectionStateError(f"Cannot disconnect in {self.state} state")
            logger.log_error(error)
            raise error
            
        self._trigger_callback('before_disconnect')
        self._state_manager.set_state(ConnectionState.DISCONNECTING)
        
        try:
            await self._disconnect()
        except Exception as e:
            error = ConnectionError("Failed to disconnect", cause=e)
            logger.log_error(error)
            self._trigger_callback('on_error', error)
            raise error
        finally:
            self._state_manager.set_state(ConnectionState.DISCONNECTED)
            self._trigger_callback('after_disconnect')
            
    async def send(self, data: bytes) -> bool:
        """发送数据
        
        Args:
            data: 要发送的数据
            
        Returns:
            bool: 发送是否成功
            
        Raises:
            ConnectionStateError: 未连接状态
            SendError: 发送数据时发生错误
        """
        if not self.is_connected:
            error = ConnectionStateError("Cannot send data when not connected")
            logger.log_error(error)
            raise error
            
        self._trigger_callback('before_send', data)
        try:
            logger.debug(f"Sending data: {data[:100]}...")  # 只记录前100字节
            await self._send(data)
            self._trigger_callback('after_send', data)
            return True
        except Exception as e:
            error = SendError("Failed to send data", cause=e)
            logger.log_error(error)
            await self._handle_error(error)
            raise error
            
    async def receive(self) -> bytes:
        """接收数据
        
        Returns:
            bytes: 接收到的数据
            
        Raises:
            ConnectionStateError: 未连接状态
            ReceiveError: 接收数据时发生错误
        """
        if not self.is_connected:
            error = ConnectionStateError("Cannot receive data when not connected")
            logger.log_error(error)
            raise error
            
        try:
            data = await self._receive()
            if data:
                self._trigger_callback('on_receive', data)
            return data
        except Exception as e:
            error = ReceiveError("Failed to receive data", cause=e)
            logger.log_error(error)
            await self._handle_error(error)
            raise error
            
    async def _handle_error(self, error: Exception) -> None:
        """处理错误
        
        Args:
            error: 错误对象
        """
        self._last_error = error
        self._trigger_callback('on_error', error)
        
        # 如果是连接已关闭的错误，断开连接
        if isinstance(error, ConnectionClosedError):
            await self.disconnect()
            
        # 重连逻辑由具体实现类处理
        if hasattr(self, '_config'):
            await self._handle_reconnect()
            
    async def _handle_reconnect(self) -> None:
        """处理重连
        
        由具体实现类重写此方法来实现重连逻辑
        """
        pass
        
    @abstractmethod
    async def _connect(self, config: Any) -> None:
        """实际的连接实现"""
        pass
        
    @abstractmethod
    async def _disconnect(self) -> None:
        """实际的断开连接实现"""
        pass
        
    @abstractmethod
    async def _send(self, data: bytes) -> None:
        """实际的发送数据实现"""
        pass
        
    @abstractmethod
    async def _receive(self) -> bytes:
        """实际的接收数据实现"""
        pass