#-*- coding:utf-8 -*-

from __future__ import absolute_import

from weberror import evalexception

from . import simple

def main():

    simple.run(evalexception.EvalException(simple.fib))

