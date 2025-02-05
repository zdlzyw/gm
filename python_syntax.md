# Python 语法说明

本文档解释了项目中使用的一些 Python 高级语法特性。

## 类型提示 (Type Hints)

类型提示使用 `->` 符号来标注函数返回值类型，使用冒号 `:` 来标注参数类型。

```python
def get_name() -> str:              # 函数返回字符串类型
    return "example"

def set_age(age: int) -> None:      # 接收整数参数，无返回值
    self._age = age

def get_data() -> Dict[str, Any]:   # 返回字典类型，键为字符串，值为任意类型
    return {"name": "test"}
```

## 枚举类型 (Enum)

使用 `Enum` 和 `auto()` 来定义枚举类型。`auto()` 会自动为枚举值分配数字。

```python
from enum import Enum, auto

class State(Enum):
    INIT = auto()      # 自动分配为 1
    RUNNING = auto()   # 自动分配为 2
    STOPPED = auto()   # 自动分配为 3

# 也可以手动指定值
class State(Enum):
    INIT = 1
    RUNNING = 2
    STOPPED = 3
```

## 泛型类型 (Generic Types)

使用方括号 `[]` 来指定容器类型中的元素类型。

```python
from typing import List, Dict, Optional, Any

# 列表类型
numbers: List[int] = [1, 2, 3]           # 整数列表
names: List[str] = ["a", "b", "c"]       # 字符串列表

# 字典类型
data: Dict[str, int] = {"age": 18}       # 键为字符串，值为整数的字典
config: Dict[str, Any] = {"name": "test", "age": 18}  # 值可以是任意类型

# 可选类型
name: Optional[str] = None    # 可以是字符串，也可以是 None
name: Optional[str] = "test"  # 可以是字符串，也可以是 None
```

## 抽象基类 (Abstract Base Class)

使用 `@abstractmethod` 装饰器来定义抽象方法。

```python
from abc import ABC, abstractmethod

class BaseClass(ABC):
    @abstractmethod
    def must_implement(self) -> None:
        """这个方法必须被子类实现"""
        pass
```

## 属性装饰器 (Property Decorator)

使用 `@property` 将方法转换为属性访问。

```python
class Person:
    def __init__(self):
        self._name = ""
        
    @property
    def name(self) -> str:
        """获取名称"""
        return self._name
        
    @name.setter
    def name(self, value: str) -> None:
        """设置名称"""
        self._name = value

# 使用方式
person = Person()
person.name = "test"    # 调用 setter
print(person.name)      # 调用 getter
```

## 数据类 (Dataclass)

使用 `@dataclass` 装饰器来简化数据类的定义。

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int
    label: str = ""    # 默认值

# 自动创建 __init__, __repr__ 等方法
point = Point(1, 2, "test")
```

## 异步编程 (Async/Await)

使用 `async/await` 进行异步编程。

```python
import asyncio

async def fetch_data() -> str:
    await asyncio.sleep(1)    # 异步等待
    return "data"

async def main():
    data = await fetch_data()
    print(data)

# 运行异步函数
asyncio.run(main())
```
