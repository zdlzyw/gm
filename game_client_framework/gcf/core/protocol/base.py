from abc import ABC, abstractmethod
from typing import Any, Dict, Type, Optional, NamedTuple, Tuple, List
from dataclasses import dataclass
import struct
from ...exceptions import GCFError, DataError, PacketError, PacketEncodeError, ValidationError
from ...utils.logger import logger

class ProtocolError(GCFError):
    """协议相关错误基类"""
    def __init__(self, stage: str, message: str, data: Optional[bytes] = None):
        self.stage = stage
        self.data = data
        super().__init__(f"{stage}: {message}")

class DecodeError(PacketError):
    """解码错误"""
    pass

class EncodeError(PacketError):
    """编码错误"""
    pass

class HeaderField(NamedTuple):
    """包头字段定义"""
    name: str           # 字段名
    size: int          # 字段大小（字节）
    type: str          # 字段类型 (int, bytes, str)
    endian: str = 'little'  # 字节序
    required: bool = True   # 是否必需

@dataclass
class ProtocolStats:
    """协议统计信息"""
    decoded_packets: int = 0    # 解码的包数量
    encoded_packets: int = 0    # 编码的包数量
    failed_packets: int = 0     # 失败的包数量
    total_bytes_in: int = 0     # 接收的总字节数
    total_bytes_out: int = 0    # 发送的总字节数
    last_packet_time: float = 0 # 最后一个包的处理时间

class ProtocolConfig:
    """协议配置"""
    def __init__(self):
        self.use_memory_view: bool = True  # 使用内存视图减少复制
        self.cache_types: bool = True      # 缓存消息类型
        self.debug_mode: bool = False      # 调试模式
        self.max_packet_size: int = 1024 * 1024  # 最大包大小（1MB）
        self.stats_enabled: bool = True    # 是否启用统计

class ProtocolBase(ABC):
    """协议基类"""
    def __init__(self, config: Optional[ProtocolConfig] = None):
        self.config = config or ProtocolConfig()
        self.stats = ProtocolStats()
        self._header_fields: Dict[str, HeaderField] = {}
        self._header_size: int = 0
        self._middlewares: List[Any] = []
        
    def register_header_field(self, field: HeaderField) -> None:
        """注册包头字段"""
        self._header_fields[field.name] = field
        self._header_size = sum(f.size for f in self._header_fields.values())
        
    def add_middleware(self, middleware: Any) -> None:
        """添加中间件"""
        self._middlewares.append(middleware)
        
    def _update_stats(self, is_encode: bool, size: int, success: bool) -> None:
        """更新统计信息"""
        if not self.config.stats_enabled:
            return
            
        if is_encode:
            if success:
                self.stats.encoded_packets += 1
                self.stats.total_bytes_out += size
            else:
                self.stats.failed_packets += 1
        else:
            if success:
                self.stats.decoded_packets += 1
                self.stats.total_bytes_in += size
            else:
                self.stats.failed_packets += 1
        self.stats.last_packet_time = time()
        
    def _decode_field(self, field: HeaderField, data: bytes, offset: int = 0) -> Tuple[Any, int]:
        """解码单个字段"""
        try:
            if field.type == 'int':
                value = int.from_bytes(data[offset:offset + field.size], field.endian)
                return value, offset + field.size
            elif field.type == 'bytes':
                return data[offset:offset + field.size], offset + field.size
            elif field.type == 'str':
                raw = data[offset:offset + field.size].rstrip(b'\x00')
                return raw.decode('utf-8'), offset + field.size
            else:
                raise DecodeError("字段解码", f"不支持的字段类型: {field.type}")
        except Exception as e:
            raise DecodeError("字段解码", f"解码字段 {field.name} 失败: {str(e)}")
            
    def _encode_field(self, field: HeaderField, value: Any) -> bytes:
        """编码单个字段"""
        try:
            if field.type == 'int':
                return value.to_bytes(field.size, field.endian)
            elif field.type == 'bytes':
                if len(value) > field.size:
                    raise EncodeError("字段编码", f"字段 {field.name} 数据过长")
                return value.ljust(field.size, b'\x00')
            elif field.type == 'str':
                encoded = value.encode('utf-8')
                if len(encoded) > field.size:
                    raise EncodeError("字段编码", f"字段 {field.name} 数据过长")
                return encoded.ljust(field.size, b'\x00')
            else:
                raise EncodeError("字段编码", f"不支持的字段类型: {field.type}")
        except Exception as e:
            raise EncodeError("字段编码", f"编码字段 {field.name} 失败: {str(e)}")
            
    def decode_header(self, data: bytes) -> Tuple[Dict[str, Any], bytes]:
        """解码包头（提供默认实现）"""
        if len(data) < self._header_size:
            raise DecodeError("包头解码", "数据不足以解析包头")
            
        try:
            header = {}
            offset = 0
            for field in self._header_fields.values():
                value, offset = self._decode_field(field, data, offset)
                header[field.name] = value
                
            return header, data[self._header_size:]
        except Exception as e:
            raise DecodeError("包头解码", str(e), data)
            
    def encode_header(self, header: Dict[str, Any]) -> bytes:
        """编码包头（提供默认实现）"""
        try:
            result = bytearray()
            for field in self._header_fields.values():
                value = header.get(field.name)
                if value is None and field.required:
                    raise EncodeError("包头编码", f"缺少必需字段: {field.name}")
                result.extend(self._encode_field(field, value or 0))
            return bytes(result)
        except Exception as e:
            raise EncodeError("包头编码", str(e))
            
    def create_debug_info(self, header: Dict[str, Any], data: bytes) -> str:
        """创建调试信息"""
        if not self.config.debug_mode:
            return ""
            
        info = ["=== 协议调试信息 ==="]
        info.append(f"包头: {header}")
        info.append(f"数据大小: {len(data)} 字节")
        info.append(f"十六进制: {data.hex()[:100]}...")
        info.append(f"统计信息: {self.stats}")
        return "\n".join(info)
        
    @abstractmethod
    def is_complete_packet(self, header: Dict[str, Any], remaining: bytes) -> bool:
        """判断是否是完整的数据包"""
        pass
        
    @abstractmethod
    def get_message_type(self, header: Dict[str, Any]) -> Optional[Type[Any]]:
        """根据包头获取消息类型"""
        pass
        
    @abstractmethod
    def decode_message(self, message_type: Type[Any], data: bytes) -> Any:
        """解码消息体"""
        pass
        
    @abstractmethod
    def encode_message(self, message: Any) -> Tuple[Dict[str, Any], bytes]:
        """编码消息
        返回: (包头字段, 消息体数据)
        """
        pass
