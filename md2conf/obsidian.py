"""Markdown extension for Obsidian-style wiki links."""

from __future__ import annotations

import os
import re
import xml.etree.ElementTree as etree
from urllib.parse import quote

from markdown import Markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor

# ``[[Page]]`` and ``[[Page|label]]`` style links used by Obsidian.
# Placeholders used by md2conf such as ``[[_TOC_]]`` or ``[[_LISTING_]]``
# must remain untouched, hence the negative lookahead.
_OBSIDIAN_LINK_RE = r"\[\[(?!_TOC_|_LISTING_)([^\]|]+)(?:\|([^\]]+))?\]\]"


class ObsidianWikiLinkInlineProcessor(InlineProcessor):
    """Converts Obsidian wiki links into HTML anchors."""

    def handleMatch(self, m: re.Match[str], data: str) -> tuple[etree.Element, int, int]:  # type: ignore[override]
        target = m.group(1)
        text = m.group(2) or target

        # Split out an optional anchor ``[[Page#Heading]]``
        if "#" in target:
            path, anchor = target.split("#", 1)
        else:
            path, anchor = target, None

        # Append Markdown extension if not present
        if not os.path.splitext(path)[1]:
            path = f"{path}.md"

        href = quote(path, safe="/")
        if anchor:
            href += "#" + quote(anchor)

        el = etree.Element("a")
        el.set("href", href)
        el.text = text
        return el, m.start(0), m.end(0)


class ObsidianWikiLinkExtension(Extension):
    def extendMarkdown(self, md: Markdown) -> None:
        md.inlinePatterns.register(
            ObsidianWikiLinkInlineProcessor(_OBSIDIAN_LINK_RE, md),
            "obsidian-wikilink",
            75,
        )


def makeExtension(**kwargs: object) -> ObsidianWikiLinkExtension:  # pragma: no cover - entry point
    return ObsidianWikiLinkExtension(**kwargs)
