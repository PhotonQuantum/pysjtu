from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from lxml.html import HtmlElement, fromstring


@dataclass(frozen=True)
class ProfileField:
    name: str
    xpath: str
    post_parse: Optional[Callable[[str], Any]] = lambda x: x

    def parse(self, el: HtmlElement) -> Any:
        raw_fields = el.xpath(self.xpath)
        if not raw_fields:
            return None
        raw_field = raw_fields[0].text

        raw_text = raw_field.strip() if isinstance(raw_field, str) else None
        if not raw_text:
            return None

        # noinspection PyArgumentList
        return self.post_parse(raw_text.strip())


def parse(fields: List[ProfileField], src: str) -> Dict[str, Any]:
    el = fromstring(src)
    return {field.name: field.parse(el) for field in fields}
