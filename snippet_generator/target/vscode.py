import abc
from ast import literal_eval
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, List, Mapping, Optional, Union
from snippet_generator.language import Language, get_languages

from snippet_generator.target.target import SnippetTargetBase, SnippetData
from snippet_generator.types import StrPath

def _eval_value(val: str, t: type):
  try:
    parsed = literal_eval(val)
    if isinstance(parsed, t):
      return parsed
  except:
    pass
  if t == str:
    return val
  if t == int:
    return int(val)
  if t == list:
    return val.split()
  if t == bool:
    return val.lower() != "false" and val != "0"
  raise Exception(f"parse error: {val}, {t}")  

def _as_list(list_or_val: Union[List[Any], Any]) -> List[Any]:
  if isinstance(list_or_val, list):
    return list_or_val
  return [list_or_val]

def _get_value(mapping: Mapping[str, Any], keys: Union[List[str], str]):
  for key in _as_list(keys):
    if key in mapping:
      return mapping[key]
  raise KeyError("not found", keys, mapping)

def _is_choice(val):
  return val[0] == "|" and val[-1] == "|" and "," in val

class VSCodeSnippet(SnippetTargetBase):
  def __init__(self, config: Mapping[str, Any], languages: Optional[List[Language]]=None) -> None:
    super().__init__(config)
    # TODO: ロジックをコンストラクタ内に置きたくない
    if languages is not None:
      self.languages = languages
    else:
      self.languages = get_languages()

  def dumps(self, snippets: Mapping[StrPath, SnippetData], path: StrPath):
    path = Path(path)
    if not path.exists():
      path.mkdir(parents=True)
    if path.is_file():
      raise Exception("already exists as a file", path)

    snippet_files = {}
    for snippet_path, snippet in snippets.items():

      def get_val(key, t, error=True):
        try:
          val = _get_value(snippet.header, self.config["snippet-keys"][key])
          return _eval_value(val, t)
        except Exception as e:
          if error:
            raise e
          else:
            return None

      snippet_obj = {}
      for key, t in [("prefix", list), ("description", str), ("isFileTemplate", bool)]:
        try:
          snippet_obj[key] = get_val(key, t)
        except:
          pass

      variables = {
        key: f'${{{ind + 1}:{key}}}' if not val else                       # tabstop
             f'${{{ind + 1}:{val}}}' if not _is_choice(val) else # placeholder
             f'${{{ind + 1}{val}}}'                              # choice
        for ind, (key, val) in 
        enumerate(snippet.variables.items())
      }
      # register cursor stop
      if "cursor" in self.config:
        for mark in _as_list(self.config["cursor"]):
          variables[mark] = "$0"
      
      cursor = 0
      body = snippet.body.replace("\\", "\\\\").replace("$", "\\$")
      while True:
        min_match_pos = len(body)
        min_arg = None
        for key in variables:
          position = body.find(key, cursor)
          if position == -1: continue
          if position < min_match_pos:
            min_match_pos, min_arg = position, key
        
        if min_arg is None: break

        body = body[:min_match_pos] + variables[min_arg] + body[(min_match_pos + len(min_arg)):]
        cursor = min_match_pos + len(variables[min_arg])

      snippet_obj["body"] = body

      name = get_val("name", str)
      language = get_val("language", str, error=False)
      if language is None:
        for _language in self.languages:
          if _language.match(snippet_path):
            language = _language.get_id()
            break
        if language is None:
          raise Exception("unknown language", snippet_path)
      
      if language not in snippet_files:
        snippet_files[language] = {}
      snippet_files[language][name] = snippet_obj

    package = self.config["package"]
    if "contributes" not in package:
      package["contributes"] = {}
    package["contributes"]["snippets"] = []
    for language, snippet_objs in snippet_files.items():
      filename = f'{language}.snippet.json'
      package["contributes"]["snippets"].append({
        "language": language,
        "path": filename
      })
      (path / filename).write_text(json.dumps(snippet_objs))
    (path / "package.json").write_text(json.dumps(package))
