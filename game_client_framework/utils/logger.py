"""日志模块

提供了一个简单但功能完整的日志系统，支持：
- 日志级别控制
- 内存缓存
- 观察者模式
- 日志过滤
- UI集成
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Any
import logging
import sys

class LogLevel(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

@dataclass
class LogEntry:
    """日志条目"""
    timestamp: float
    level: LogLevel
    message: str
    module: str
    details: Optional[Dict[str, Any]] = None

class LogHandler(logging.Handler):
    """自定义日志处理器，支持内存缓存和观察者模式"""
    def __init__(self, capacity: int = 1000):
        super().__init__()
        self.entries: List[LogEntry] = []
        self.capacity = capacity
        self.observers: List[callable] = []
    
    def emit(self, record: logging.LogRecord):
        """处理日志记录"""
        # 创建日志条目
        entry = LogEntry(
            timestamp=record.created,
            level=LogLevel(record.levelno),
            message=self.format(record),
            module=record.module,
            details=getattr(record, 'details', None)
        )
        
        # 添加到缓存
        self.entries.append(entry)
        if len(self.entries) > self.capacity:
            self.entries = self.entries[-self.capacity:]
        
        # 通知观察者
        for observer in self.observers:
            observer(entry)

class Logger:
    """简单的日志工具类，支持基本的日志记录和UI显示"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.logger = logging.getLogger('gcf')
            self.handler = LogHandler()
            self._setup_logger()
            self.initialized = True
    
    def _setup_logger(self):
        """设置日志"""
        if not self.logger.handlers:
            # 设置格式
            formatter = logging.Formatter(
                '[%(asctime)s][%(levelname)s][%(name)s] %(message)s',
                '%Y-%m-%d %H:%M:%S'
            )
            
            # 设置控制台输出
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            # 设置自定义处理器
            self.handler.setFormatter(formatter)
            self.logger.addHandler(self.handler)
            
            # 设置日志级别
            self.logger.setLevel(logging.DEBUG)
    
    def add_observer(self, observer: callable):
        """添加日志观察者"""
        self.handler.observers.append(observer)
    
    def get_entries(self, 
        level_filter: Optional[set[LogLevel]] = None,
        keyword_filter: Optional[str] = None
    ) -> List[LogEntry]:
        """获取过滤后的日志条目"""
        entries = self.handler.entries
        
        if level_filter:
            entries = [e for e in entries if e.level in level_filter]
            
        if keyword_filter:
            keyword = keyword_filter.lower()
            entries = [e for e in entries if keyword in e.message.lower()]
            
        return entries
    
    def _log(self, level: int, msg: str, *args, **kwargs):
        """统一的日志记录方法"""
        # 提取额外的详细信息
        details = kwargs.pop('details', None)
        if details:
            kwargs['extra'] = {'details': details}
            
        self.logger.log(level, msg, *args, **kwargs)
    
    # 便捷方法
    def debug(self, msg: str, *args, **kwargs):
        self._log(logging.DEBUG, msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        self._log(logging.INFO, msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        self._log(logging.WARNING, msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        """记录错误信息"""
        if isinstance(msg, Exception):
            # 如果msg是异常对象，格式化为错误消息
            error_msg = f"{type(msg).__name__}: {str(msg)}"
            details = {
                'error_type': type(msg).__name__,
                'error_message': str(msg)
            }
            if hasattr(msg, 'details'):
                details.update(msg.details)
            if hasattr(msg, 'cause') and msg.cause:
                details['cause'] = f"{type(msg.cause).__name__}: {str(msg.cause)}"
            self._log(logging.ERROR, error_msg, details=details, exc_info=True, **kwargs)
        else:
            self._log(logging.ERROR, msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        self._log(logging.CRITICAL, msg, *args, **kwargs)

# 全局日志实例
logger = Logger()
