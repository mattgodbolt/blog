#!/usr/bin/python
import xml.etree.ElementTree

from markdown import Extension, Markdown
from markdown.treeprocessors import Treeprocessor


class PrecisProcessor(Treeprocessor):
    def __init__(self, md: Markdown):
        super().__init__()
        self.md = md

    def run(self, tree: xml.etree.ElementTree.Element) -> xml.etree.ElementTree.Element:
        """Process the markdown tree to include only the first few paragraphs.

        Args:
            tree: Element tree of the parsed Markdown content

        Returns:
            Modified element tree with only the first few paragraphs
        """
        count = 0
        kids: list[xml.etree.ElementTree.Element] = list(tree)
        limit = 3
        if len(kids) < 5:
            limit = 5
        for thing in kids:
            if thing.tag == "p":
                count += 1
            if count > limit:
                tree.remove(thing)
        return tree


class PrecisExtension(Extension):
    def extendMarkdown(self, md: Markdown) -> None:
        """Register the processor with the Markdown parser.

        Args:
            md: Markdown parser instance
        """
        md.treeprocessors.register(PrecisProcessor(md), "<inline", 5)
