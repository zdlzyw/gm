from abc import ABC, abstractmethod
from typing import Any

class Packet(ABC):
    """数据包抽象基类
    
    定义数据包必须实现的基本接口，作为规范约束。
    具体的包格式、编码方式等由业务开发者自行实现。
    """
    @abstractmethod
    def pack(self) -> bytes:
        """将数据打包为字节流
        
        Returns:
            bytes: 打包后的字节流
        """
        pass
    
    @abstractmethod
    def unpack(self, data: bytes) -> None:
        """从字节流解包数据
        
        Args:
            data: 要解包的字节流
        """
        pass
    
    @abstractmethod
    def get_type(self) -> Any:
        """获取数据包类型
        
        Returns:
            Any: 数据包类型（由业务开发者定义类型）
        """
        pass