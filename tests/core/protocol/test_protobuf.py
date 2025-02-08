"""Protobuf协议测试模块"""

import unittest
from typing import Dict, Any
from google.protobuf import message as pb_message
from game_client_framework.core.protocol.protobuf import ProtobufProtocol
from game_client_framework.core.protocol.base import HeaderField
from game_client_framework.exceptions import (
    PacketError,
    PacketEncodeError,
    PacketDecodeError
)

class TestMessage(pb_message.Message):
    """测试用消息类"""
    
    TYPE_ID = 1
    
    def __init__(self):
        super().__init__()
        self._data = b''
        
    def SerializeToString(self) -> bytes:
        """序列化"""
        return self._data
        
    def ParseFromString(self, data: bytes) -> None:
        """反序列化"""
        self._data = data

class GameProtocol(ProtobufProtocol):
    """测试用协议实现"""
    
    def __init__(self):
        super().__init__()
        # 注册包头字段
        self.register_header_field(HeaderField('msg_id', 2, 'int'))
        self.register_header_field(HeaderField('length', 4, 'int'))
        self.register_header_field(HeaderField('version', 1, 'int'))
        
    def is_complete_packet(self, header: Dict[str, Any], remaining: bytes) -> bool:
        """检查包是否完整"""
        total_len = header.get('length', 0)
        return len(remaining) >= total_len - self._header_size

class TestProtobufProtocol(unittest.TestCase):
    """测试Protobuf协议实现"""
    
    def setUp(self):
        """测试准备"""
        self.protocol = GameProtocol()
        
    def test_register_message(self):
        """测试消息注册"""
        # 注册消息类型
        self.protocol.register_message(TestMessage)
        
        # 测试重复注册
        with self.assertRaises(PacketError):
            self.protocol.register_message(TestMessage)
            
        # 测试注册无效的消息类型
        class InvalidMessage:
            pass
            
        with self.assertRaises(PacketError):
            self.protocol.register_message(InvalidMessage)
            
    def test_encode_decode_message(self):
        """测试消息编解码"""
        # 注册消息类型
        self.protocol.register_message(TestMessage)
        
        # 创建测试消息
        message = TestMessage()
        message._data = b'test data'
        
        # 编码消息
        header, body = self.protocol.encode_message(message)
        self.assertEqual(header['msg_id'], TestMessage.TYPE_ID)
        self.assertEqual(header['length'], len(body) + self.protocol._header_size)
        self.assertEqual(body, b'test data')
        
        # 解码消息
        decoded = self.protocol.decode_message(TestMessage, body)
        self.assertEqual(decoded._data, b'test data')
        
    def test_encode_errors(self):
        """测试编码错误处理"""
        # 测试未注册的消息类型
        message = TestMessage()
        with self.assertRaises(PacketError):
            self.protocol.encode_message(message)
            
        # 测试序列化失败
        self.protocol.register_message(TestMessage)
        message = TestMessage()
        message.SerializeToString = lambda: exec('raise Exception("序列化失败")')
        with self.assertRaises(PacketEncodeError):
            self.protocol.encode_message(message)
            
    def test_decode_errors(self):
        """测试解码错误处理"""
        # 注册消息类型
        self.protocol.register_message(TestMessage)
        
        # 测试反序列化失败
        message = TestMessage()
        message.ParseFromString = lambda data: exec('raise Exception("反序列化失败")')
        with self.assertRaises(PacketDecodeError):
            self.protocol.decode_message(TestMessage, b'invalid data')
            
    def test_complete_packet_check(self):
        """测试包完整性检查"""
        header = {
            'msg_id': 1,
            'length': 20,  # 总长度20字节
            'version': 1
        }
        
        # 数据充足
        self.assertTrue(
            self.protocol.is_complete_packet(header, b'a' * 13)  # 20-7=13字节
        )
        
        # 数据不足
        self.assertFalse(
            self.protocol.is_complete_packet(header, b'a' * 12)  # 少1字节
        )

if __name__ == '__main__':
    unittest.main()
