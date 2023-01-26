import abc
from typing import Any, List, Mapping

from snippet_generator.loader.loader import SnippetData
from snippet_generator.types import StrPath

class SnippetTargetBase(metaclass=abc.ABCMeta):
  def __init__(self, config: Mapping[str, Any]) -> None:
    self.config = config
  @abc.abstractmethod
  def dumps(self, snippets: List[SnippetData], path: StrPath, config: Mapping[str, Any]): ...
