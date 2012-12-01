#-*- coding:utf-8 -*-

from __future__ import absolute_import

from paste import urlmap

from . import simple


def map():

    # デフォルトのアプリケーションを渡す
    mapping = urlmap.URLMap(simple.hello)

    # /fib に来たらフィボナッチな感じ
    mapping['/fib'] = simple.fib

    simple.run(mapping)
