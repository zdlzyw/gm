"""网络连接基类模块"""
from enum import Enum, auto
from typing import Optional, Tuple, Any, Callable, Dict, List
from abc import ABC, abstractmethod
import asyncio

from game_client_framework.exceptions import (
    ConnectionError,
    ConnectionStateError,
    ConnectionTimeoutError,
    ConnectionClosedError,
    SendError,
    ReceiveError
)
from game_client_framework.utils.logger import logger

class ConnectionState(Enum):
    """连接状态枚举，定义连接生命周期的不同阶段。
    - DISCONNECTED: 初始或完全断开状态
    - CONNECTING: 正在尝试建立连接
    - CONNECTED: 已成功建立连接
    - DISCONNECTING: 正在主动断开连接
    """
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    DISCONNECTING = auto()

# ------回调函数类型定义------
ConnectionCallback: Callable = Callable[[], None]
StateChangeCallback: Callable = Callable[[ConnectionState, ConnectionState], None]
DataCallback: Callable = Callable[[bytes], None]
ErrorCallback: Callable = Callable[[Exception], None]

class ConnectionStateManager:
    """连接状态管理器，负责状态变更和回调触发。

    属性：
        state (ConnectionState): 当前连接状态（只读）
        is_connected (bool): 是否处于已连接状态（只读）

    方法：
        set_state(new_state): 更新状态并触发回调
        add_state_change_listener(callback): 添加状态变更监听器
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
                    logger.error(e, "State change")
                    
    def add_state_change_listener(self, callback: StateChangeCallback) -> None:
        """添加状态变更监听器"""
        self._callbacks.append(callback)
        
    @property
    def state(self) -> ConnectionState:
        """当前连接状态（只读）"""
        return self._state
        
    @property
    def is_connected(self) -> bool:
        """是否处于已连接状态（只读）"""
        return self._state == ConnectionState.CONNECTED

class BaseConnection(ABC):
    """连接抽象基类，提供连接管理的基础实现。

    特性：
        - 状态管理
        - 生命周期回调（连接前后、发送前后等）
        - 错误处理和重连机制（需子类实现）

    子类必须实现：
        _connect(), _disconnect(), _send(), _receive()

    使用示例：
        class MyConn(BaseConnection):
            async def _connect(self, config):
                # 实现具体连接逻辑
    """
    def __init__(self):
        # 状态管理
        self._state_manager = ConnectionStateManager()
        
        # 最后一次错误
        self._last_error: Optional[Exception] = None
        
        # 重连次数
        self._reconnect_count: int = 0
        
        # 回调函数字典
        self._callbacks: Dict[str, List[Callable[...,Any]]] = {
            'before_connect': [],    # 连接前
            'after_connect': [],     # 连接后
            'before_disconnect': [], # 断开前
            'after_disconnect': [],  # 断开后
            'before_send': [],       # 发送前
            'after_send': [],        # 发送后
            'on_receive': [],        # 接收到数据
            'on_error': []           # 发生错误
        }
        
    def _trigger_callback(self, name: str, *args:Any, **kwargs:Any) -> None:
        """触发指定名称的回调，并捕获异常。

        Args：
            name: 回调类型（如 'before_connect'）
            *args: 传递给回调的位置参数
            **kwargs: 传递给回调的关键字参数
        """
        for callback in self._callbacks.get(name, []):
            try:
                logger.debug(f"Triggering callback '{name}': {callback.__name__}")
                callback(*args, **kwargs)
            except Exception as e:
                self._handle_callback_error(callback, e)

    def _register_callback(
        self,
        callback_type: str,
        callback: Callable[..., Any]
    ) -> None:
        """通用的回调注册方法（内部使用）"""
        if callback_type not in self._callbacks:
            raise ValueError(f"Invalid callback type: {callback_type}")
        self._callbacks[callback_type].append(callback)

    # 回调注册方法
    def on_before_connect(self, callback: ConnectionCallback) -> None:
        """注册连接前回调"""
        self._register_callback('before_connect', callback)
        
    def on_after_connect(self, callback: ConnectionCallback) -> None:
        """注册连接后回调"""
        self._register_callback('after_connect', callback)
        
    def on_before_disconnect(self, callback: ConnectionCallback) -> None:
        """注册断开前回调"""
        self._register_callback('before_disconnect', callback)
        
    def on_after_disconnect(self, callback: ConnectionCallback) -> None:
        """注册断开后回调"""
        self._register_callback('after_disconnect', callback)
        
    def on_state_change(self, callback: StateChangeCallback) -> None:
        """注册状态变更回调"""
        self._state_manager.add_state_change_listener(callback)
        
    def on_before_send(self, callback: DataCallback) -> None:
        """注册发送前回调"""
        self._register_callback('before_send', callback)
        
    def on_after_send(self, callback: DataCallback) -> None:
        """注册发送后回调"""
        self._register_callback('after_send', callback)
        
    def on_receive(self, callback: DataCallback) -> None:
        """注册数据接收回调"""
        self._register_callback('on_receive', callback)
        
    def on_error(self, callback: ErrorCallback) -> None:
        """注册错误回调"""
        self._register_callback('on_error', callback)
        
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
        """异步建立连接。

        Args：
            config: 连接配置，具体类型由子类定义

        Returns：
            bool: 是否连接成功

        Raises：
            ConnectionStateError: 当前状态不允许连接
            ConnectionTimeoutError: 连接超时
            ConnectionError: 其他连接错误
        """
        if self.state != ConnectionState.DISCONNECTED:
            error = ConnectionStateError(f"Cannot connect in {self.state} state")
            self._handle_connection_error('connect', error)
            raise error
            
        self._trigger_callback('before_connect')
        self._state_manager.set_state(ConnectionState.CONNECTING)
        logger.info(f"Connecting with config: {config}")
        
        try:
            await self._connect_impl(config)
            self._state_manager.set_state(ConnectionState.CONNECTED)
            self._reconnect_count = 0
            logger.info("Connection established")
            self._trigger_callback('after_connect')
            return True
        except asyncio.TimeoutError as e:
            error = ConnectionTimeoutError("Connection timed out", cause=e)
            logger.error(error)
            self._state_manager.set_state(ConnectionState.DISCONNECTED)
            self._handle_connection_error('connect', error)
            raise error
        except Exception as e:
            error = ConnectionError("Failed to connect", cause=e)
            logger.error(error)
            self._state_manager.set_state(ConnectionState.DISCONNECTED)
            self._handle_connection_error('connect', error)
            raise error
            
    async def disconnect(self) -> None:
        """断开连接
        
        Raises：
            ConnectionStateError: 当前状态不允许断开
            ConnectionError: 断开过程中发生错误
        """
        if self.state not in (ConnectionState.CONNECTED, ConnectionState.CONNECTING):
            error = ConnectionStateError(f"Cannot disconnect in {self.state} state")
            self._handle_connection_error('disconnect', error)
            raise error
            
        self._trigger_callback('before_disconnect')
        self._state_manager.set_state(ConnectionState.DISCONNECTING)
        
        try:
            await self._disconnect_impl()
        except Exception as e:
            error = ConnectionError("Failed to disconnect", cause=e)
            self._handle_connection_error('disconnect', error)
            raise error
        finally:
            self._state_manager.set_state(ConnectionState.DISCONNECTED)
            self._trigger_callback('after_disconnect')
            
    async def send(self, data: bytes) -> bool:
        """发送数据
        
        Args：
            data: 要发送的数据
            
        Returns：
            bool: 发送是否成功
            
        Raises：
            ConnectionStateError: 未连接状态
            SendError: 发送数据时发生错误
        """
        if not self.is_connected:
            error = ConnectionStateError("Cannot send data when not connected")
            self._handle_connection_error('send', error)
            raise error
            
        self._trigger_callback('before_send', data)
        try:
            logger.debug(f"Sending data: {data[:100]}...")  # 只记录前100字节
            await self._send_impl(data)
            self._trigger_callback('after_send', data)
            return True
        except Exception as e:
            error = SendError("Failed to send data", cause=e)
            self._handle_connection_error('send', error)
            raise error
            
    async def receive(self) -> bytes:
        """接收数据
        
        Returns：
            bytes: 接收到的数据
            
        Raises：
            ConnectionStateError: 未连接状态
            ReceiveError: 接收数据时发生错误
        """
        if not self.is_connected:
            error = ConnectionStateError("Cannot receive data when not connected")
            self._handle_connection_error('receive', error)
            raise error
            
        try:
            data = await self._receive_impl()
            if data:
                self._trigger_callback('on_receive', data)
            return data
        except Exception as e:
            error = ReceiveError("Failed to receive data", cause=e)
            await self._handle_connection_error('receive', error)
            raise error
            
    def _handle_callback_error(self, callback: Callable[..., Any], error: Exception) -> None:
        """统一处理回调错误"""
        logger.error(
            f"Callback '{callback.__name__}' failed",
            error,
            exc_info=True
        )

    async def _handle_connection_error(self, error: Exception, context: str) -> None:
        """统一处理连接错误"""
        self._last_error = error
        logger.error(f"{context} error occurred: {error}")
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
    async def _connect_impl(self, config: Any) -> None:
        """实际的连接实现"""
        pass
        
    @abstractmethod
    async def _disconnect_impl(self) -> None:
        """实际的断开连接实现"""
        pass
        
    @abstractmethod
    async def _send_impl(self, data: bytes) -> None:
        """实际的发送数据实现"""
        pass
        
    @abstractmethod
    async def _receive_impl(self) -> bytes:
        """实际的接收数据实现"""
        pass