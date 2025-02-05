from abc import ABC, abstractmethod
from typing import Any, Dict, Callable, Optional, Type, TypeVar
import inspect
from dataclasses import dataclass
from ...exceptions import GCFError, BusinessError
from ...utils.logger import logger

T = TypeVar('T')

@dataclass
class HandlerContext:
    """处理器上下文"""
    header: Dict[str, Any]  # 消息头
    message: Any           # 消息体
    handler: Any          # 处理器实例
    method: Callable      # 处理方法

class HandlerError(GCFError):
    """处理器相关错误"""
    def __init__(self, message: str, context: Optional[HandlerContext] = None):
        self.context = context
        super().__init__(message)

class HandlerBase(ABC):
    """处理器基类"""
    @abstractmethod
    async def handle(self, header: Dict[str, Any], message: Any) -> Any:
        """处理消息"""
        pass

class ProtocolHandler:
    """协议处理器"""
    def __init__(self):
        self._handlers: Dict[Type[Any], HandlerBase] = {}
        self._type_handlers: Dict[Type[Any], Callable] = {}
        
    def register(self, message_type: Type[T], handler: Optional[HandlerBase] = None) -> Optional[Callable[[HandlerBase], HandlerBase]]:
        """注册消息处理器
        
        可以作为装饰器使用:
        @handler.register(LoginRequest)
        class LoginHandler(HandlerBase):
            async def handle(self, header, message):
                pass
                
        或直接注册:
        handler.register(LoginRequest, LoginHandler())
        """
        def decorator(handler_cls: Type[HandlerBase]) -> HandlerBase:
            if not issubclass(handler_cls, HandlerBase):
                raise HandlerRegistrationError(f"处理器必须继承HandlerBase: {handler_cls}")
                
            handler_instance = handler_cls()
            self._handlers[message_type] = handler_instance
            return handler_instance
            
        if handler is not None:
            if not isinstance(handler, HandlerBase):
                raise HandlerRegistrationError(f"处理器必须是HandlerBase的实例: {handler}")
            self._handlers[message_type] = handler
            return None
            
        return decorator
        
    def register_function(self, message_type: Type[T]) -> Callable[[Callable], Callable]:
        """注册处理函数
        
        @handler.register_function(LoginRequest)
        async def handle_login(header, message):
            pass
        """
        def decorator(func: Callable) -> Callable:
            if not inspect.iscoroutinefunction(func):
                raise HandlerRegistrationError(f"处理函数必须是异步函数: {func}")
                
            sig = inspect.signature(func)
            if len(sig.parameters) != 2:
                raise HandlerRegistrationError(f"处理函数必须接受两个参数(header, message): {func}")
                
            self._type_handlers[message_type] = func
            return func
            
        return decorator
        
    async def handle(self, header: Dict[str, Any], message: Any) -> Any:
        """处理消息"""
        message_type = type(message)
        
        # 1. 查找类处理器
        handler = self._handlers.get(message_type)
        if handler is not None:
            try:
                context = HandlerContext(header, message, handler, handler.handle)
                return await handler.handle(header, message)
            except Exception as e:
                raise HandlerError(f"处理器异常: {str(e)}", context) from e
                
        # 2. 查找函数处理器
        func = self._type_handlers.get(message_type)
        if func is not None:
            try:
                context = HandlerContext(header, message, None, func)
                return await func(header, message)
            except Exception as e:
                raise HandlerError(f"处理函数异常: {str(e)}", context) from e
                
        raise HandlerNotFoundError(f"未找到消息处理器: {message_type}")
        
    def get_handler(self, message_type: Type[T]) -> Optional[HandlerBase]:
        """获取消息处理器"""
        return self._handlers.get(message_type)
        
    def get_handler_function(self, message_type: Type[T]) -> Optional[Callable]:
        """获取消息处理函数"""
        return self._type_handlers.get(message_type)
