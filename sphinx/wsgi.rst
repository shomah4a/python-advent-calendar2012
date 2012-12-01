===================
 WSGI でなんかやる
===================


WSGI とは
=========

WSGI とは Web Server Gateway Interface の略で `PEP333 <http://www.python.org/dev/peps/pep-0333/>`_ ( `日本語訳 <http://knzm.readthedocs.org/en/latest/pep-0333-ja.html>`_ ) で定義されているものです。

Python3 においては `PEP3333 <http://www.python.org/dev/peps/pep-3333/>`_ があります。
文字列周りの定義が変わった以外は PEP333 と変わらないのでまあ適当に。

去年の `Advent Calendar <http://d.hatena.ne.jp/shomah4a/20111225/1324813404>`_ でなんか書いた気がするのでそれはそれで。

`PEP444 <http://www.python.org/dev/peps/pep-0444/>`_ なんてのもありましたが、本当にそんなのもありましたねーで終わりそうなのでスルーしてあげるのが大人の優しさです。

WSGI について詳しいことは `gihyo.jp <http://gihyo.jp/dev/feature/01/wsgi>`_ に書いた記事を見てくださいめんどくさいので。

とりあえず WSGI についてはサーバとアプリケーションとミドルウェアについてわかっていれば大丈夫です。頑張ってください。

で、今年は去年と同じ事をしても仕方がないのでなんか作ってみることにします。


Hello, World
============

WSGI で Hello, World します。

WSGI のアプリは大体以下のような定義っぽいです。

- environ, start_response という引数を受け取る

  - environ は環境変数の辞書
  - start_response は callable なオブジェクト

- 処理の中で start_response にレスポンスコードとレスポンスヘッダを渡して呼び出す
- 返り値は iterate すると文字列を取り出せる iterable オブジェクト


返した iterable を iterate して取得した文字列はレスポンスボディとして使われます。

Hello, World するアプリは以下のような感じです。

.. code-block:: python

   def hello(environ, start_response):
       u'''
       Hello, world を返す
       '''

       # ステータスコードとコンテントタイプだけ返す
       start_response('200 OK', [('Content-Type', 'text/plain')])

       # 本文
       return ['Hello, World']


で、作ったので動かしましょう。

動かすには wsgiref.simple_server というモジュールが標準ライブラリにあるのでこれを使います。


.. code-block:: python

   def run(app):
       server = simple_server.make_server('', 8080, app)
       server.serve_forever()


   if __name__ == '__main__':
       run(hello)


で、これを動かしたらブラウザで http://localhost:8080/ にでもアクセスすると "Hello, World" と挨拶を返してくれることでしょう。

動きましたね? 動きましたよね?

では次行きます。


パラメータを受け取ってみる
==========================

Hello, World が動いたら次はなんかパラメータを受け取って処理します。

パラメータは `environ['QUERY_STRING']` に URL の ? 以降のクエリ文字列が入っています。

POST やその他のメソッドで渡されるリクエストボディは `environ['wsgi.input']` に file-like オブジェクトがあるのでそれから読みましょう。

と書いておいてなんですが、ぶっちゃけ文字列とかファイルっぽいオブジェクトを渡されてもめんどいので標準モジュールにある `cgi.FieldStorage <http://docs.python.jp/2/library/cgi.html>`_ を使います。

以下のように書くとクエリ文字列か application/x-www-form-urlencoded なリクエストボディにある `'param'` というパラメータの値を撮ってきて返します。

パラメータがないときは `'default value'` を返します。

多分リクエストボディがないときに `fp` を渡すとよくなかったと思うのでなんか対策したほうがいいかもしれないっすね。

.. code-block:: python

   fs = cgi.FieldStorage(environ=environ, fp=environ['wsgi.input'])
   value = fs.getfirst('param', 'default value')


これを使ってなんとなく書いてみたのが以下のフィボナッチ数を計算して返す WSGI アプリケーションです。


.. code-block:: python

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
       フィボナッチを計算して返す WSGI アプリケーション
       '''

       fs = cgi.FieldStorage(environ=environ, fp=environ['wsgi.input'])

       # value というパラメータを取ってくる
       value = fs.getfirst('value', '0')

       val = int(value)

       result = calc_fib(val)

       start_response('200 OK', [('Content-Type', 'text/plain')])

       return [str(result)]


で、先ほどの `run` 関数に `fib` を渡してサーバを立ち上げ、 htt;//localhost:8080/ にアクセスすると `0` と表示されます。

このアプリケーション内では value というパラメータを見ているので http://localhost:8080/?value=10 としてパラメータを渡すと `37` と表示されるはずです。

ほら、パラメータを受け取ってそれに応じて処理するなにかができましたね。

数字以外を渡すとエラーになるのでまあなんとかしてあげてください。


URL マッピングしてみる
======================

さて、今までは普通のアプリを動かしていただけですが、ここで複数のアプリを動かしたいなーとか思ったとしましょう。

思いましたか? 思いましたね? 思ってくれないと先に進まないので念じてください。

そういう時は WSGI のミドルウェアを使います。

ミドルウェアとは

- サーバ側から見ると environ, start_response を受け取るアプリケーションとして振る舞う
- アプリケーション側から見ると environ, start_response を渡して呼び出すサーバとして振る舞う

というものです。

試しに何もしないミドルウェアを作ってみます。

.. code-block:: python

   def empty(app):
       u'''
       何もしないミドルウェア
       '''

       def internal(environ, start_response):

           return app(environ, start_response)


ただの高階関数です。

これを使って fib をラップするには


.. code-block:: python

   app = empty(fib)


とします。

この app は WSGI アプリケーションとして振舞うので `run` 関数に渡せばそのまま動きます。

が、何も変わりません。

何もしないミドルウェアなので当然です。


で、ミドルウェアとしては例えば URL マッピングを行うものがあるでしょう。

.. code-block:: python

   def url_mapping(environ, start_response):
       u'''
       url マッピングをしてみよう
       '''

       # 呼び出された時のパス (mod_wsgi とか使うときに必要)
       script_path = environ['SCRIPT_NAME']

       # このスクリプトに渡されたパス情報
       path = environ['PATH_INFO']

       if path == '/fib':
           # フィボナッチを計算する
           return fib(environ, start_response)
       else:
           # hello, world
           return hello(environ, start_reponse)

まあ大体こんな感じです。

これは高階関数として定義していないのでそのままアプケーションとして振る舞います。

ソースを見ればわかりますが、 /fib にアクセスされるとフィボナッチを、それ以外では Hello World を返すようなアプリケーションです。

まあお試しください。


ライブラリを使ってみる
======================

以上のようにマッピングとかかけますが、めんどくさいです。

そういう時はライブラリを使いましょう。

- `paste <http://pythonpaste.org/>`_
- `werkzeug <http://werkzeug.pocoo.org/>`_ (ゔぇるくつぉいくとか発音するらしい)

とかまあ色々あります。

ここではとりあえず weberror でも使ってみましょう。

weberror はその名の通りエラーハンドリングするためのミドルウェアが色々入っています。

例えば evalexception はエラー時のコンテキストを使って色々と評価できるので色々便利です。

以下のようのに fib を包んであげるだけです。

.. code-block:: python

   from weberror import evalexception

   def main():

       run(evalexception.EvalException(fib))


この状態でエラーが出るように数字以外の文字列を渡してみると


.. figure:: _static/weberror.png

   weberror の画像


ほら、こんな感じにエラーが出たスタックの状態で色々試せるんですよ。便利でしょ。

多分フレームワークには普通に備わってそうだけどね!

ただし、裏側で状態を持っているのでマルチスレッドなサーバでは使えないですがデバッグ用にはかなーり便利ですね。

paste でも werkzeug でも URL マッパーがあるので上記のようなしょぼいものを使わないでまともなものを使いましょう。


まとめ
======

以上のようにフレームワークを使わなくてもなんとなくアプリケーションが作れるんだぜって話でした多分。

まあここの話はコントローラあたりの話でしかないので model とか view には `SQLAlchemy <http://pythonpaste.org/>`_ とか `Zope Page Template <http://pypi.python.org/pypi/zope.pagetemplate>`_ とか使いましょうね。

何がしたいのかよくわからないけどなんかの参考になれば。
