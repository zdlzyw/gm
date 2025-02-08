"""协议模块

此模块提供了网络协议的基础设施，包括：

1. 协议基类 (BaseProtocol)
   - 包头字段管理
   - 数据编解码
   - 错误处理

2. Protobuf协议实现 (ProtobufProtocol)
   - 基于 Protocol Buffers 的消息序列化
   - 消息类型注册
   - 自定义包头格式

3. 数据包 (Packet)
   - 数据包基类
   - 编解码接口
   - 头部字段管理
"""

from game_client_framework.core.protocol.base import BaseProtocol
from game_client_framework.core.protocol.protobuf import ProtobufProtocol
from game_client_framework.core.protocol.packet import Packet

__all__ = [
    'BaseProtocol',
    'ProtobufProtocol',
    'Packet'
]
