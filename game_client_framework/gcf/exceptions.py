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

class HeartbeatError(NetworkError):
    """心跳异常"""
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
