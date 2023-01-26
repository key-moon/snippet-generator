import abc
from dataclasses import dataclass
from pathlib import Path
import re
from typing import List, Optional
import fnmatch
from snippet_generator.types import StrPath
from snippet_generator.vscode import get_global_settings_path, get_vscode_installed_path
import json

class LanguageBase(metaclass=abc.ABCMeta):
  @abc.abstractmethod
  def get_id(self) -> str: ...

  @abc.abstractmethod
  def match(self, path: StrPath) -> bool: ...

@dataclass
class Language(LanguageBase):
  language_id: str
  extensions: List[str]
  filenames: List[str]
  filename_patterns: List[str]
  first_line: Optional[str]
  
  def get_id(self):
    return self.language_id

  def match(self, path: StrPath):
    path = Path(path)
    if path.suffix in self.extensions: return True
    if path.name in self.filenames: return True
    if any(fnmatch.fnmatch(path.name, pattern) for pattern in self.filename_patterns): return True
    
    if self.first_line is not None:
      with open(path) as f:
        if re.match(f.readline().strip("\n"), self.first_line): return True
    
    return False


def _from_settings_file(path: StrPath):
  if not Path(path).exists(): return
  settings = json.load(open(path, "r"))
  if not isinstance(settings, dict): return
  assocs = settings.get("files.associations")
  if not isinstance(assocs, dict): return
  for pattern, id in assocs.items():
    yield Language(id, [], [], [pattern], None)

def _from_extension(path: StrPath):
  package_path = Path(path) / "package.json"
  if not package_path.exists(): return
  package = json.load(open(package_path, "r"))
  if not isinstance(package, dict): return
  cont = package.get("contributes")
  if not isinstance(cont, dict): return
  languages = cont.get("languages")
  if not isinstance(languages, list): return
  for language in languages:
    if not isinstance(language, dict): continue
    yield Language(
      language.get("id", ""),
      language.get("extensions", []),
      language.get("filenames", []),
      language.get("filename_patterns", []),
      language.get("first_line", None),
    )

def get_languages(extensions_dir: Optional[StrPath]=None, installed_path: Optional[StrPath]=None, settings_paths: List[StrPath]=[]):
  if extensions_dir is None:
    extensions_dir = Path("~/.vscode/extensions").expanduser()
  if installed_path is None:
    installed_path = get_vscode_installed_path()
  languages = []
  
  settings_paths = [*settings_paths, get_global_settings_path()]
  for settings in settings_paths:
    languages.extend(_from_settings_file(settings))

  extensions = []
  extensions.extend((Path(extensions_dir)).iterdir())
  extensions.extend((Path(installed_path) / "resources" / "app" / "extensions").iterdir())
  for extension in extensions:
    languages.extend(_from_extension(extension))
  return languages
