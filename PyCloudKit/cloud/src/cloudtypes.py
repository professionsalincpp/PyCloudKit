from typing import Any, Union
from abc import ABC
from .utils import *

class CloudObject(ABC):
    """
    CloudObject is an abstract class for all cloud objects.
    It has a value attribute and two methods: to_string and from_string.
    to_string converts the value into a string representation.
    from_string converts the string representation into the value.
    """
    def __init__(self, value: Any) -> None:
        self.value = value

    def to_string(self) -> str:
        raise NotImplementedError

    def from_string(self, value: str) -> None:
        raise NotImplementedError


class PyCloudObject(CloudObject):
    """
    PyCloudObject is a subclass of CloudObject.
    It using for default python types.
    """
    def __init__(self, value: Any) -> None:
        self.value = value

    def to_string(self) -> str:
        if isinstance(self.value, str):
            return f'"{self.value}"'
        return str(self.value)
    
    def from_string(self, value: str) -> None:
        self.value = eval(value)

    def __repr__(self) -> str:
        return self.to_string()

class ClassCloudObject(CloudObject):
    """
    ClassCloudObject is a subclass of CloudObject.
    It using for custom classes.
    """
    def __init__(self, value: object) -> None:
        super().__init__(value)
        
    def to_string(self) -> str:
        _class = self.value.__class__
        _dict = _class.__dict__
        return f"{_class.__name__}({_dict})"

    def from_string(self, value: str) -> None:
        _classstr = value.split('(')[0]
        _dictstr = value.split('(')[1].rstrip(')')
        _class = eval(f"{_classstr}")
        _dict = eval(f"{_dictstr}")
        self.value = _class(**_dict)
        _class.__dict__ = _dict

    def __repr__(self) -> str:
        return self.to_string()
    

class AnyCloudObject(CloudObject):
    """
    AnyCloudObject is a subclass of CloudObject.
    It using for any types.
    """
    def __init__(self, value: Any) -> None:
        super().__init__(value)

    def to_string(self) -> str:
        if is_py_object(self.value):
            return PyCloudObject(self.value).to_string()
        elif is_class_object(self.value):
            return ClassCloudObject(self.value).to_string()
        raise NotImplementedError

    def from_string(self, value: str) -> None:
        self.value = eval(value)