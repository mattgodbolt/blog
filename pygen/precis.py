#!/usr/bin/python

from markdown import markdown, Extension
from markdown.treeprocessors import Treeprocessor


class PrecisProcessor(Treeprocessor):
    def __init__(self, md):
        super().__init__()
        self.md = md

    def run(self, tree):
        count = 0
        kids = list(tree.getchildren())
        limit = 3
        if len(kids) < 5:
            limit = 5
        for thing in kids:
            if thing.tag == 'p':
                count += 1
            if count > limit:
                tree.remove(thing)
        return tree


class PrecisExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.treeprocessors.add("precis", PrecisProcessor(md), "<inline")
        md.registerExtension(self)
