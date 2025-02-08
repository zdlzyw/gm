"""协议基类测试模块"""

import unittest
from typing import Any, Dict, Type, Tuple
from game_client_framework.core.protocol.base import (
    BaseProtocol,
    HeaderField,
    ProtocolConfig,
    ProtocolError,
    EncodeError,
    DecodeError
)

class TestHeaderField(unittest.TestCase):
    """测试包头字段定义"""
    
    def test_valid_field(self):
        """测试有效的字段定义"""
        field = HeaderField('test', 4, 'int')
        self.assertEqual(field.name, 'test')
        self.assertEqual(field.size, 4)
        self.assertEqual(field.type, 'int')
        self.assertEqual(field.byte_order, 'little')  # 默认值
        
    def test_valid_field_with_byte_order(self):
        """测试带字节序的字段定义"""
        field = HeaderField('test', 2, 'int', 'big')
        self.assertEqual(field.byte_order, 'big')
        
    def test_valid_bytes_field(self):
        """测试字节类型字段"""
        field = HeaderField('test', 8, 'bytes')
        self.assertEqual(field.type, 'bytes')

class TestProtocolConfig(unittest.TestCase):
    """测试协议配置"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = ProtocolConfig()
        self.assertEqual(config.max_packet_size, 65535)
        self.assertFalse(config.debug)
        
    def test_custom_config(self):
        """测试自定义配置"""
        config = ProtocolConfig(max_packet_size=1024, debug=True)
        self.assertEqual(config.max_packet_size, 1024)
        self.assertTrue(config.debug)

class TestProtocolBase(unittest.TestCase):
    """测试协议基类功能"""
    
    class TestProtocol(BaseProtocol):
        """测试用协议实现"""
        
        def __init__(self):
            super().__init__()
            # 注册测试用的包头字段
            self.register_header_field(HeaderField('msg_id', 2, 'int'))
            self.register_header_field(HeaderField('length', 4, 'int'))
            self.register_header_field(HeaderField('version', 1, 'int'))
            self.register_header_field(HeaderField('token', 4, 'bytes'))
            
        def is_complete_packet(self, header: Dict[str, Any], remaining: bytes) -> bool:
            """检查包是否完整"""
            total_len = header.get('length', 0)
            return len(remaining) >= total_len - self._header_size
            
        def decode_message(self, message_type: Type[Any], data: bytes) -> Any:
            """解码消息（测试用）"""
            return data
            
        def encode_message(self, message: Any) -> Tuple[Dict[str, Any], bytes]:
            """编码消息（测试用）"""
            if not isinstance(message, (bytes, bytearray)):
                message = str(message).encode('utf-8')
            return {
                'msg_id': 1,
                'length': len(message) + self._header_size,
                'version': 1,
                'token': b'test'
            }, message
    
    def setUp(self):
        """测试准备"""
        self.protocol = self.TestProtocol()
        
    def test_register_header_field(self):
        """测试注册包头字段"""
        # 测试已注册的字段
        self.assertEqual(len(self.protocol._header_fields), 4)
        self.assertEqual(self.protocol._header_size, 11)  # 2+4+1+4
        
        # 测试重复注册
        with self.assertRaises(ProtocolError):
            self.protocol.register_header_field(HeaderField('msg_id', 2, 'int'))
            
        # 测试无效的字段大小
        with self.assertRaises(ProtocolError):
            self.protocol.register_header_field(HeaderField('test', 0, 'int'))
            
        # 测试无效的字段类型
        with self.assertRaises(ProtocolError):
            self.protocol.register_header_field(HeaderField('test', 4, 'invalid'))
            
        # 测试过大的整数字段
        with self.assertRaises(ProtocolError):
            self.protocol.register_header_field(HeaderField('test', 9, 'int'))
            
    def test_encode_decode_header(self):
        """测试包头编解码"""
        # 准备测试数据
        header = {
            'msg_id': 1,
            'length': 100,
            'version': 1,
            'token': b'test'
        }
        
        # 编码
        encoded = self.protocol.encode_header(header)
        self.assertEqual(len(encoded), 11)  # 2+4+1+4
        
        # 解码
        decoded, remaining = self.protocol.decode_header(encoded + b'remaining')
        self.assertEqual(decoded['msg_id'], 1)
        self.assertEqual(decoded['length'], 100)
        self.assertEqual(decoded['version'], 1)
        self.assertEqual(decoded['token'], b'test')
        self.assertEqual(remaining, b'remaining')
        
    def test_encode_decode_errors(self):
        """测试编解码错误处理"""
        # 测试缺少字段
        with self.assertRaises(EncodeError):
            self.protocol.encode_header({'msg_id': 1})  # 缺少其他必需字段
            
        # 测试数据不足
        with self.assertRaises(DecodeError):
            self.protocol.decode_header(b'too short')
            
        # 测试字节字段长度不匹配
        with self.assertRaises(EncodeError):
            header = {
                'msg_id': 1,
                'length': 100,
                'version': 1,
                'token': b'toolong'  # 应该是4字节
            }
            self.protocol.encode_header(header)
            
    def test_complete_packet_check(self):
        """测试包完整性检查"""
        header = {
            'msg_id': 1,
            'length': 20,  # 总长度20字节
            'version': 1,
            'token': b'test'
        }
        
        # 数据充足
        self.assertTrue(
            self.protocol.is_complete_packet(header, b'a' * 9)  # 20-11=9字节
        )
        
        # 数据不足
        self.assertFalse(
            self.protocol.is_complete_packet(header, b'a' * 8)  # 少1字节
        )
        
    def test_message_encoding(self):
        """测试消息编解码"""
        # 编码消息
        header, body = self.protocol.encode_message("test message")
        self.assertEqual(header['msg_id'], 1)
        self.assertEqual(header['version'], 1)
        self.assertEqual(header['token'], b'test')
        self.assertTrue(isinstance(body, bytes))
        
        # 解码消息
        decoded = self.protocol.decode_message(bytes, body)
        self.assertEqual(decoded, body)

if __name__ == '__main__':
    unittest.main()
