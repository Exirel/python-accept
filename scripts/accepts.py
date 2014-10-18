#!/bin/python
from __future__ import print_function, unicode_literals

from argparse import ArgumentParser

from http_accept import parse_accept_value, split_accept_header
from http_accept import HeaderAcceptList, HeaderAcceptValue


if __name__ == '__main__':
    parser = ArgumentParser(
        description='Show info of an Accept HTTP Header'
    )
    parser.add_argument('header')
    arguments = parser.parse_args()

    accepts = HeaderAcceptList(
        HeaderAcceptValue(
            info.get('mimetype'), **info.get('options', {})
        )
        for info in (
        parse_accept_value(value)
        for value in split_accept_header(arguments.header)
    ))

    for accept in accepts:
        print(
            '%s %s %s' % (accept.mimetype, accept.quality, ';'.join(
                '='.join((key, value)) for key, value in accept.options.items()
            ))
        )
