import abc
from dataclasses import dataclass
from typing import Any, Dict, Mapping

from snippet_generator.types import StrPath

@dataclass
class SnippetData:
  header: Dict[str, str]
  variables: Dict[str, str]
  body: str

class Loader(metaclass=abc.ABCMeta):
  def __init__(self, config: Mapping[str, Any]) -> None:
    self.config = config
  @abc.abstractmethod
  def load(self, path: StrPath) -> SnippetData: ...
