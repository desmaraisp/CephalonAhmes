from typing import Tuple
import re

def split_string_on_last_separator_before_cutoff_length(content, limit, separators_ordered_by_priority=['\n']) -> Tuple[str, str]:
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



def Check_Title_Validity(title, ForumPage) -> Tuple[str, bool]:
    title = title.replace("PSA: ", "").strip()

    return title, not ("+" in title and ForumPage == "https://forums.warframe.com/forum/3-pc-update-notes.xml")

def remove_all_zero_width_spaces(string):
    return string.replace(
            u"\xa0", "")