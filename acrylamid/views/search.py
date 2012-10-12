# -*- encoding: utf-8 -*-
#
# Copyright 2012 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see acrylamid/__init__.py

import io

from os.path import exists

from acrylamid.views import View

from acrylamid.helpers import joinurl
from acrylamid.lib.html import HTMLParser, unescape
from acrylamid.lib.search import JavaScriptIndex, IndexBuilder, languages


class Strip(HTMLParser):

    def __init__(self, *args):

        for func in ('starttag', 'endtag', 'startendtag', 'comment'):
            self.__dict__['handle_' + func] = lambda *args, **kw: None

        return HTMLParser.__init__(self, *args)

    def handle_entityref(self, name):
        word = self.result.pop()
        word += unescape(name)
        self.result.append(word)


class Search(View):

    priority = 25.0

    def init(self):

        self.js_index = JavaScriptIndex()
        self.indexer = IndexBuilder('en', options={})

    def load(self, path, docs):

        try:
            with io.open(path, encoding='utf-8') as fp:
                self.indexer.load(fp, 'json')
        except (IOError, ValueError):
            pass

        # delete all entries for files that will be rebuilt
        self.indexer.prune(docs)

    def generate(self, request):

        path = joinurl(self.conf['output_dir'], self.path, 'index.js')
        docs = filter(lambda entry: entry.has_changed, request['entrylist'])

        if exists(path) and not docs:
            event.skip(path)
            raise StopIteration

        self.load(path, docs)

        # for doc in docs:
        for doc in request['entrylist'][12:14]:
            self.indexer.feed(doc.filename, doc.title, ''.join(Strip(doc.content).result))

        dump = io.BytesIO()
        self.indexer.dump(dump, 'json')
        dump.seek(0)
        print dump.read()

        raise RuntimeError
        # yield io.StringIO(), joinurl(self.conf['output_dir'], self.path, 'index.html')
