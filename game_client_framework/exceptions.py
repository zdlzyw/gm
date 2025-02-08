"""异常定义模块

此模块定义了框架中使用的所有异常类，包括：

1. 基础异常
   - GCFError: 所有异常的基类

2. IO相关异常
   - IOError: IO操作相关异常
   - FileError: 文件操作异常
   - FileNotFoundError: 文件不存在异常
   - FilePermissionError: 文件权限异常

3. 网络相关异常
   - NetworkError: 网络相关异常基类
   - ConnectionError: 连接相关异常
   - ConnectionStateError: 连接状态异常
   - ConnectionTimeoutError: 连接超时异常
   - ConnectionClosedError: 连接已关闭异常
   - SendError: 发送数据异常
   - ReceiveError: 接收数据异常

4. 心跳相关异常
   - HeartbeatError: 心跳错误基类
   - HeartbeatStateError: 心跳状态错误
   - HeartbeatTimeoutError: 心跳超时错误
   - HeartbeatConfigError: 心跳配置错误

5. 连接池相关异常
   - PoolError: 连接池相关异常基类
   - PoolEmptyError: 无可用连接异常
   - PoolAcquireTimeoutError: 获取连接超时异常
   - PoolConfigError: 连接池配置错误
   - PoolConnectionError: 连接池连接错误

6. 数据处理相关异常
   - DataError: 数据处理相关异常基类
   - ParseError: 解析错误
   - ValidationError: 数据验证错误
   - SerializationError: 序列化错误
   - DeserializationError: 反序列化错误

7. 数据包相关异常
   - PacketError: 数据包相关异常基类
   - PacketEncodeError: 数据包编码错误
   - PacketDecodeError: 数据包解码错误
   - PacketValidationError: 数据包验证错误

8. 业务逻辑相关异常
   - BusinessError: 业务逻辑相关异常基类
   - ConfigError: 配置相关异常
   - StateError: 状态相关异常
"""

from typing import Optional, Any

class GCFError(Exception):
    """框架基础异常类"""
    def __init__(
        self,
        message: str,
        cause: Optional[Exception] = None,
        **details: Any
    ):
        super().__init__(message)
        self.cause = cause
        self.details = details
        
    def __str__(self) -> str:
        result = [super().__str__()]
        if self.details:
            result.append(f"Details: {self.details}")
        if self.cause:
            result.append(f"Caused by: {self.cause}")
        return " | ".join(result)

# IO相关异常
class IOError(GCFError):
    """IO操作相关异常基类"""
    pass

class FileError(IOError):
    """文件操作异常"""
    pass

class FileNotFoundError(FileError):
    """文件不存在异常"""
    pass

class FilePermissionError(FileError):
    """文件权限异常"""
    pass

# 网络相关异常
class NetworkError(IOError):
    """网络相关异常基类"""
    pass

class ConnectionError(NetworkError):
    """连接相关异常"""
    pass

class ConnectionStateError(ConnectionError):
    """连接状态异常"""
    pass

class ConnectionTimeoutError(ConnectionError):
    """连接超时异常"""
    pass

class ConnectionClosedError(ConnectionError):
    """连接已关闭异常"""
    pass

class SendError(NetworkError):
    """发送数据异常"""
    pass

class ReceiveError(NetworkError):
    """接收数据异常"""
    pass

# 心跳相关异常
class HeartbeatError(Exception):
    """心跳错误基类"""
    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message)
        self.cause = cause

class HeartbeatStateError(HeartbeatError):
    """心跳状态错误
    
    当心跳状态转换不合法时抛出，例如：
    - 已经运行的心跳再次启动
    - 未运行的心跳请求停止
    - 状态转换不符合预期
    """
    pass

class HeartbeatTimeoutError(HeartbeatError):
    """心跳超时错误
    
    当连续多次未收到心跳响应时抛出
    """
    pass

class HeartbeatConfigError(HeartbeatError):
    """心跳配置错误
    
    当心跳配置参数无效时抛出
    """
    pass

# 连接池相关异常
class PoolError(NetworkError):
    """连接池相关异常的基类"""
    pass

class PoolEmptyError(PoolError):
    """连接池中没有可用连接，且无法创建新连接时抛出"""
    pass

class PoolAcquireTimeoutError(PoolError):
    """在指定时间内无法获取连接时抛出"""
    pass

class PoolConfigError(PoolError):
    """连接池配置错误时抛出"""
    pass

class PoolConnectionError(PoolError):
    """连接池中的连接出现错误时抛出"""
    pass

# 数据处理相关异常
class DataError(GCFError):
    """数据处理相关异常基类"""
    pass

class ParseError(DataError):
    """解析错误"""
    pass

class ValidationError(DataError):
    """数据验证错误"""
    pass

class SerializationError(DataError):
    """序列化错误"""
    pass

class DeserializationError(DataError):
    """反序列化错误"""
    pass

# 数据包相关异常
class PacketError(GCFError):
    """数据包相关异常的基类"""
    pass

class PacketEncodeError(PacketError):
    """数据包编码错误"""
    pass

class PacketDecodeError(PacketError):
    """数据包解码错误"""
    pass

class PacketValidationError(PacketError):
    """数据包验证错误"""
    pass

# 业务逻辑相关异常
class BusinessError(GCFError):
    """业务逻辑相关异常基类"""
    pass

class ConfigError(BusinessError):
    """配置相关异常"""
    pass

class StateError(BusinessError):
    """状态相关异常"""
    pass
