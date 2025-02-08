"""协议基类模块

此模块定义了网络协议的基础设施，提供了：

1. 包头字段定义：
   - 支持 int 和 bytes 类型
   - 支持大小端配置
   - 自动计算包头大小

2. 包头处理：
   - 字段注册和验证
   - 编码和解码
   - 类型安全的序列化

3. 错误处理：
   - 包头字段错误
   - 编解码错误
   - 序列化错误

4. 配置管理：
   - 最大包大小限制
   - 调试模式

使用此模块时，需要：
1. 继承 BaseProtocol 类
2. 注册所需的包头字段
3. 实现抽象方法
4. 处理相关异常

Example:
    ```python
    # 1. 定义协议
    class GameProtocol(BaseProtocol):
        def __init__(self):
            super().__init__()
            # 注册包头字段
            self.register_header_field(HeaderField('msg_id', 2, 'int'))
            self.register_header_field(HeaderField('length', 4, 'int'))
            
        def is_complete_packet(self, header, remaining):
            # 检查包是否完整
            return len(remaining) >= header['length']
            
        def decode_message(self, message_type, data):
            # 解码消息体
            return message_type.parse(data)
            
        def encode_message(self, message):
            # 编码消息体
            return {
                'msg_id': message.TYPE_ID,
                'length': len(data)
            }, message.serialize()
            
    # 2. 使用协议
    try:
        protocol = GameProtocol()
        header, body = protocol.encode_message(message)
        packet = protocol.encode_header(header) + body
        
    except EncodeError as e:
        logger.error(f"编码失败: {e}")
        
    except ProtocolError as e:
        logger.error(f"协议错误: {e}")
    ```
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, Literal, Type
import struct
from game_client_framework.exceptions import (
    GCFError,
    PacketError,
    PacketEncodeError,
    PacketDecodeError
)

@dataclass
class HeaderField:
    """包头字段定义
    
    Attributes:
        name: 字段名
        size: 字段大小（字节）
        type: 字段类型，支持 'int' 或 'bytes'
        byte_order: 字节序，'big' 或 'little'，仅对 'int' 类型有效
    """
    name: str
    size: int
    type: Literal['int', 'bytes']
    byte_order: Literal['big', 'little'] = 'little'

class ProtocolError(PacketError):
    """协议相关错误的基类"""
    pass

class EncodeError(PacketEncodeError):
    """编码错误"""
    pass

class DecodeError(PacketDecodeError):
    """解码错误"""
    pass

@dataclass
class ProtocolConfig:
    """协议配置
    
    Attributes:
        max_packet_size: 最大包大小（字节）
        debug: 是否开启调试模式
    """
    max_packet_size: int = 65535  # 默认最大包大小
    debug: bool = False           # 默认关闭调试

class BaseProtocol(ABC):
    """协议基类
    
    此类提供了网络协议的基础功能：
    1. 包头字段管理
       - 字段注册和验证
       - 自动计算包头大小
       - 类型安全的序列化
       
    2. 编解码接口
       - 包头编解码
       - 消息体编解码
       - 包完整性检查
       
    3. 错误处理
       - 字段验证错误
       - 编解码错误
       - 类型错误
       
    使用此类时，需要：
    1. 继承此类
    2. 在 __init__ 中注册所需的包头字段
    3. 实现以下抽象方法：
       - is_complete_packet: 检查包是否完整
       - decode_message: 解码消息体
       - encode_message: 编码消息体
       
    Example:
        ```python
        class GameProtocol(BaseProtocol):
            def __init__(self):
                super().__init__()
                # 注册包头字段
                self.register_header_field(HeaderField('msg_id', 2, 'int'))
                self.register_header_field(HeaderField('length', 4, 'int'))
                self.register_header_field(HeaderField('version', 1, 'int'))
                
            def is_complete_packet(self, header, remaining):
                # 检查包是否完整
                total_len = header['length']
                return len(remaining) >= total_len - self._header_size
                
            def decode_message(self, message_type, data):
                # 解码消息体
                return message_type.parse(data)
                
            def encode_message(self, message):
                # 编码消息体
                body = message.serialize()
                return {
                    'msg_id': message.TYPE_ID,
                    'length': len(body) + self._header_size,
                    'version': message.VERSION
                }, body
        ```
        
    Attributes:
        config (ProtocolConfig): 协议配置
        _header_fields (Dict[str, HeaderField]): 包头字段定义字典
        _header_size (int): 包头总大小（字节）
    """
    
    def __init__(self, config: Optional[ProtocolConfig] = None):
        """初始化协议
        
        Args:
            config: 协议配置，如果为 None 则使用默认配置
        """
        self.config = config or ProtocolConfig()
        self._header_fields: Dict[str, HeaderField] = {}
        self._header_size: int = 0
        
    def register_header_field(self, field: HeaderField) -> None:
        """注册包头字段
        
        Args:
            field: 包头字段定义
            
        Raises:
            ProtocolError: 字段已存在或字段定义无效
        """
        # 1. 检查字段是否已存在
        if field.name in self._header_fields:
            raise ProtocolError(f"字段 {field.name} 已被注册")
            
        # 2. 检查字段定义
        if field.size <= 0:
            raise ProtocolError(f"字段 {field.name} 的大小必须大于0")
            
        if field.type not in ('int', 'bytes'):
            raise ProtocolError(f"字段 {field.name} 的类型必须是 'int' 或 'bytes'")
            
        if field.type == 'int' and field.size > 8:
            raise ProtocolError(f"整数字段 {field.name} 的大小不能超过8字节")
            
        # 3. 注册字段
        self._header_fields[field.name] = field
        self._header_size = sum(f.size for f in self._header_fields.values())
        
    def _pack_int(self, value: int, size: int, byte_order: str) -> bytes:
        """打包整数
        
        Args:
            value: 要打包的整数
            size: 字节数
            byte_order: 字节序
            
        Returns:
            打包后的字节串
            
        Raises:
            EncodeError: 打包失败
        """
        try:
            # 1. 选择格式字符串
            if size == 1:
                fmt = 'B'  # unsigned char
            elif size == 2:
                fmt = 'H'  # unsigned short
            elif size == 4:
                fmt = 'I'  # unsigned int
            elif size == 8:
                fmt = 'Q'  # unsigned long long
            else:
                raise EncodeError(f"不支持的整数大小: {size}")
                
            # 2. 添加字节序
            if byte_order == 'little':
                fmt = '<' + fmt
            else:
                fmt = '>' + fmt
                
            # 3. 打包
            return struct.pack(fmt, value)
            
        except struct.error as e:
            raise EncodeError(f"整数打包失败: {e}")
            
    def _unpack_int(self, data: bytes, byte_order: str) -> int:
        """解包整数
        
        Args:
            data: 要解包的字节串
            byte_order: 字节序
            
        Returns:
            解包后的整数
            
        Raises:
            DecodeError: 解包失败
        """
        try:
            # 1. 选择格式字符串
            size = len(data)
            if size == 1:
                fmt = 'B'
            elif size == 2:
                fmt = 'H'
            elif size == 4:
                fmt = 'I'
            elif size == 8:
                fmt = 'Q'
            else:
                raise DecodeError(f"不支持的整数大小: {size}")
                
            # 2. 添加字节序
            if byte_order == 'little':
                fmt = '<' + fmt
            else:
                fmt = '>' + fmt
                
            # 3. 解包
            return struct.unpack(fmt, data)[0]
            
        except struct.error as e:
            raise DecodeError(f"整数解包失败: {e}")
            
    def encode_header(self, fields: Dict[str, Any]) -> bytes:
        """编码包头
        
        Args:
            fields: 包头字段值字典
            
        Returns:
            编码后的包头数据
            
        Raises:
            EncodeError: 编码失败
        """
        try:
            result = bytearray()
            
            # 1. 检查必需字段
            for name, field in self._header_fields.items():
                if name not in fields:
                    raise EncodeError(f"缺少必需的包头字段: {name}")
                    
                value = fields[name]
                
                # 2. 根据类型编码
                if field.type == 'int':
                    result.extend(self._pack_int(value, field.size, field.byte_order))
                else:  # bytes
                    if len(value) != field.size:
                        raise EncodeError(f"字段 {name} 的大小不匹配: 期望 {field.size}，实际 {len(value)}")
                    result.extend(value)
                    
            return bytes(result)
            
        except Exception as e:
            if not isinstance(e, EncodeError):
                raise EncodeError(f"包头编码失败: {e}")
            raise
            
    def decode_header(self, data: bytes) -> Tuple[Dict[str, Any], bytes]:
        """解码包头
        
        Args:
            data: 要解码的数据
            
        Returns:
            (包头字段字典, 剩余数据)
            
        Raises:
            DecodeError: 解码失败
        """
        try:
            # 1. 检查数据长度
            if len(data) < self._header_size:
                raise DecodeError(f"数据不足: 需要 {self._header_size} 字节，实际 {len(data)} 字节")
                
            # 2. 解码各个字段
            result = {}
            pos = 0
            
            for name, field in self._header_fields.items():
                field_data = data[pos:pos + field.size]
                
                if field.type == 'int':
                    result[name] = self._unpack_int(field_data, field.byte_order)
                else:  # bytes
                    result[name] = field_data
                    
                pos += field.size
                
            return result, data[pos:]
            
        except Exception as e:
            if not isinstance(e, DecodeError):
                raise DecodeError(f"包头解码失败: {e}")
            raise
            
    @abstractmethod
    def is_complete_packet(self, header: Dict[str, Any], remaining: bytes) -> bool:
        """判断是否是完整的数据包
        
        Args:
            header: 已解码的包头
            remaining: 剩余数据
            
        Returns:
            是否是完整的数据包
        """
        pass
        
    @abstractmethod
    def decode_message(self, message_type: Type[Any], data: bytes) -> Any:
        """解码消息体
        
        Args:
            message_type: 消息类型类
            data: 要解码的数据
            
        Returns:
            解码后的消息对象
            
        Raises:
            DecodeError: 解码失败
        """
        pass
        
    @abstractmethod
    def encode_message(self, message: Any) -> Tuple[Dict[str, Any], bytes]:
        """编码消息
        
        Args:
            message: 要编码的消息对象
            
        Returns:
            (包头字段字典, 消息体数据)
            
        Raises:
            EncodeError: 编码失败
        """
        pass
