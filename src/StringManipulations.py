from typing import List, Tuple
import re
from src import (
    ConfigurationHandler as cfg
)

def split_string_on_last_separator_before_cutoff_length(content: str, limit: int, separators_ordered_by_priority: List[str]=['\n']) -> Tuple[str, str]:
    if len(content) <= limit:
        return content, ''

    content_before_limit = content[:limit]
    for separator in separators_ordered_by_priority:
        locations_of_separators_in_content_before_limit = [
                m.start() for m in re.finditer(separator, content_before_limit)]

        if(not locations_of_separators_in_content_before_limit):
            continue

        return (
            content[:locations_of_separators_in_content_before_limit[-1]],
            content[locations_of_separators_in_content_before_limit[-1] + len(separator):]
                )

    return content[:limit], content[limit:]


def get_title_validity(title: str, ignore_patterns: List[str]) -> bool:
    any_match = any([re.search(x, title) for x in ignore_patterns])
    return not any_match

def apply_many_regex_transforms(string:str, substitutions: List[cfg.RegexSubstitutionPair]) -> str: 
    for pair in substitutions:
        string = re.sub(pair.pattern, pair.substitution, string)
    return string