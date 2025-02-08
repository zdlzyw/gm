"""数据包模块

此模块定义了数据包的基础抽象类，用于：
1. 定义数据包的基本结构
2. 提供编码和解码接口
3. 支持自定义头部字段
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from game_client_framework.exceptions import (
    PacketError,
    PacketEncodeError,
    PacketDecodeError,
    PacketValidationError
)


class Packet(ABC):
    """数据包抽象基类
    
    定义了数据包的基本接口，包括：
    - 头部字段管理
    - 编码和解码
    - 数据验证
    
    子类需要实现：
    - encode(): 将数据包编码为字节串
    - decode(): 从字节串解码数据包
    - validate(): 验证数据包的有效性
    """
    
    def __init__(self):
        """初始化数据包"""
        self._header: Dict[str, Any] = {}
        self._body: Any = None
        
    @property
    def header(self) -> Dict[str, Any]:
        """获取头部字段"""
        return self._header
        
    @property
    def body(self) -> Any:
        """获取消息体"""
        return self._body
        
    @body.setter
    def body(self, value: Any):
        """设置消息体"""
        self._body = value
        
    def set_header(self, key: str, value: Any) -> None:
        """设置头部字段
        
        Args:
            key: 字段名
            value: 字段值
        """
        self._header[key] = value
        
    def get_header(self, key: str, default: Any = None) -> Any:
        """获取头部字段
        
        Args:
            key: 字段名
            default: 默认值
            
        Returns:
            字段值，如果字段不存在则返回默认值
        """
        return self._header.get(key, default)
        
    @abstractmethod
    def encode(self) -> bytes:
        """将数据包编码为字节串
        
        Returns:
            bytes: 编码后的字节串
            
        Raises:
            PacketEncodeError: 编码失败
        """
        raise NotImplementedError
        
    @abstractmethod
    def decode(self, data: bytes) -> None:
        """从字节串解码数据包
        
        Args:
            data: 要解码的字节串
            
        Raises:
            PacketDecodeError: 解码失败
        """
        raise NotImplementedError
        
    def validate(self) -> None:
        """验证数据包的有效性
        
        Raises:
            PacketValidationError: 验证失败
        """
        # 默认实现不做验证
        pass
