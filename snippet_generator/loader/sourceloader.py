import abc
import re
from typing import Any, List, Mapping, Union

from snippet_generator.loader.loader import Loader, SnippetData
from snippet_generator.language import LanguageBase
from snippet_generator.types import StrPath


def _as_list(list_or_val: Union[List[Any], Any]) -> List[Any]:
  if isinstance(list_or_val, list):
    return list_or_val
  return [list_or_val]

class LoaderState(metaclass=abc.ABCMeta):
  def __init__(self, snippet: SnippetData, config: Mapping[str, Any]) -> None:
    self.snippet = snippet
    self.config = config
  @abc.abstractmethod
  def next_state(self, line: str) -> "LoaderState": ...
  @abc.abstractmethod
  def get_result(self) -> SnippetData: ...

class InitState(LoaderState):
  def next_state(self, line: str):
    if any(key in line for key in _as_list(self.config["header-signature"])):
      return HeaderState(self.get_result(), self.config)
    else:
      return self
  
  def get_result(self):
    return self.snippet

class HeaderState(LoaderState):
  def next_state(self, line: str):
    match = re.match(rf"^.*?([a-zA-Z0-9_-]+){self.config['header-separator']}(.*)$", line)
    if match is not None:
      key, value = match.groups()
      key = key.lower()
      self.snippet.header[key] = value
      return self
    if any(key in line for key in _as_list(self.config["variables-signature"])):
      return VariableState(self.get_result(), self.config)
    if any(key in line for key in _as_list(self.config["body-signature"])):
      return BodyState(self.get_result(), self.config)
    return self

  def get_result(self):
    return self.snippet

class VariableState(LoaderState):
  def next_state(self, line: str):
    match = re.match(rf"^.*?([a-zA-Z0-9_-]+){self.config['variables-separator']}(.*)$", line)
    if match is not None:
      key, value = match.groups()
      self.snippet.variables[key] = value      
      return self
    if any(key in line for key in _as_list(self.config["body-signature"])):
      return BodyState(self.get_result(), self.config)
    return self

  def get_result(self):
    return self.snippet

class BodyState(LoaderState):
  def __init__(self, snippet: SnippetData, config: Mapping[str, Any]) -> None:
    super().__init__(snippet, config)
    self.lines = []

  def next_state(self, line: str):
    if len(self.lines) == 0 and line == "":
      return self
    self.lines.append(line)
    return self

  def get_result(self):
    while len(self.lines) != 0 and len(self.lines[-1]) == 0:
      self.lines.pop()
    self.snippet.body = "\n".join(self.lines)
    return self.snippet

class SourceLoader(Loader):
  def __init__(self, config: Mapping[str, Any]) -> None:
    super().__init__(config)

  def load(self, path: StrPath) -> SnippetData:
    snippet = SnippetData({}, {}, "")
    
    state = InitState(snippet, self.config)
    with open(path, "r") as f:
      while True:
        line = f.readline()
        if line == "": break
        line = line[:-1]
        state = state.next_state(line)
    snippet = state.get_result()

    return snippet
