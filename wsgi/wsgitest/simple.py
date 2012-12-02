#-*- coding:utf-8 -*-
import sys
import cgi
from wsgiref import simple_server



def hello(environ, start_response):
    u'''
    Hello, world を返す
    '''

    # ステータスコードとコンテントタイプだけ返す
    start_response('200 OK', [('Content-Type', 'text/plain')])

    # 本文
    return ['Hello, World']



def spam(environ, start_response):
    u'''
    spam を返す
    '''

    start_response('200 OK', [('Content-Type', 'text/plain')])

    return ['spam!']



def url_mapping(environ, start_response):
    u'''
    url マッピングをしてみよう
    '''

    # 呼び出された時のパス (mod_wsgi とか使うときに必要)
    script_path = environ['SCRIPT_NAME']

    # このスクリプトに渡されたパス情報
    path = environ['PATH_INFO']

    if path == '/fib':
        return fib(environ, start_response)
    else:
        return hello(environ, start_reponse)



def calc_fib(value):
    u'''
    フィボナッチを計算する
    '''

    x, y = 0, 1

    for x in xrange(value):
        x, y = y, x + y

    return x



def fib(environ, start_response):
    u'''
    フィボナッチを計算して返す
    '''

    fs = cgi.FieldStorage(environ=environ, fp=environ['wsgi.input'])
    value = fs.getfirst('value', '0')

    val = int(value)

    result = calc_fib(val)

    start_response('200 OK', [('Content-Type', 'text/plain')])

    return [str(result)]



def mapping(patterns, default=None):
    u'''
    patterns に登録してあるマッピング情報絵振り分ける

    :param dist patterns: パスをキー、 WSGI アプリケーションを値とする辞書
    :param app default: パスにないときに呼ぶアプリケーション
    '''

    def internal(environ, start_response):

        path = environ['PATH_INFO']

        if path in patterns:
            return patterns[path](environ, start_response)
        elif default is not None:
            return default(environ, start_response)


        start_response('404 NotFound', [('Content-Type', 'text/plain')])

        return ['{0} not found'.format(path)]


    return internal



def empty(app):
    u'''
    何もしないミドルウェア
    '''

    def internal(environ, start_response):

        return app(environ, start_response)

    return internal


def run(app):

    server = simple_server.make_server('', 8080, app)
    server.serve_forever()



main = lambda: run(hello)

main_fib = lambda: run(fib)

main_map = lambda: run(mapping({'/fib':fib}, hello))



