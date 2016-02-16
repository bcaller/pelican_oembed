# Copyright (c) 2016 Ben Caller

from markdown.extensions import Extension
from pyembed.core import PyEmbed
from pyembed.markdown.pattern import PyEmbedPattern


class CachingPyEmbedPattern(PyEmbedPattern):
    def __init__(self, cache, pyembed, md):
        super(CachingPyEmbedPattern, self).__init__(pyembed, md)
        self.cache = cache

    def handleMatch(self, m):
        url = m.group(4)
        if self.cache and url in self.cache:
            # found in the cache
            return self.md.htmlStash.store(self.pyembed.renderer.render(url, self.cache[url].copy()))
        else:
            return super(CachingPyEmbedPattern, self).handleMatch(m)


class CachingPyEmbedMarkdownExtension(Extension):
    def __init__(self, renderer, cache=None):
        super(CachingPyEmbedMarkdownExtension, self).__init__()
        self.renderer = renderer
        self.cache = cache

    def extendMarkdown(self, md, md_globals):
        pyembed = PyEmbed(renderer=self.renderer)
        if self.cache is None:
            md.inlinePatterns.add('pyembed', PyEmbedPattern(pyembed, md), '_begin')
        else:
            md.inlinePatterns.add('pyembed', CachingPyEmbedPattern(self.cache, pyembed, md), '_begin')
