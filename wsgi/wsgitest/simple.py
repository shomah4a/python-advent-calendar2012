#-*- coding:utf-8 -*-
import sys
from wsgiref import simple_server



def hello(environ, start_response):
    u'''
    Hello, world を返す
    '''

    start_response('200 OK', [('Content-Type', 'text/plain')])

    return ['Hello, World']



def main():

    server = simple_server.make_server('', 8080, hello)

    server.serve_forever()

