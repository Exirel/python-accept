# -*- coding: utf-8 -*-
from argparse import ArgumentParser


HTML_MIMETYPES = [
    'text/html',
    'application/xhtml',
    'application/xhtml+xml'
]


def split_accept_header(accept_header):
    """Split accept header into accept header value's data and return generator

    One can iterate over the result of this function's call, at it returns
    a generator - or transforme the result into a python list:

        >>> list(split_accept_header('text/html, application/xml;q=0.8'))
        ['text/html', 'application/xml;q=0.8']

    This function can be used, for example, with ``parse_accept_value``:

        >>> values = split_accept_header('text/html, application/xml;q=0.8')
        >>> for value in values:
        ...     # do something here with the value

    See ``parse_accept_value`` for more information.

    """
    return (value for value in accept_header.replace(' ', '').split(','))


def parse_accept_value(accept_value):
    """Split an accept header value into severals key into a dict.

    You can give a value like ``text/html``, or like ``application/xml;q=0.8``,
    and this function will returns a dict with two keys:

    * ``mimetype``: the parsed mimetype as a string
    * ``options``: a dict of {key: value} from the ``key=value`` part.

    For example:

        >>> parse_accept_value('text/html')
        {'mimetype': 'text/html', 'options': {}}
        >>> parse_accept_value('text/html;q=0.8')
        {'mimetype': 'text/html', 'options': {'q': '0.8'}}
        >>> parse_accept_value('text/html;q=0.8;level=1')
        {'mimetype': 'text/html', 'options': {'q': '0.8', 'level': '1'}}

    """
    values = accept_value.split(';')
    mimetype = values.pop(0).strip()
    args = dict(
        [part for part in value.replace(' ', '').split('=')]
        for value in values
    )
    return {
        'mimetype': mimetype,
        'options': args
    }


class HeaderAcceptValue(object):
    """Represent one value of an HTTP Request Accept header.

    An Accept header value is composed of a mimetype and a list of options,
    such as ``q`` (reserved key), or any custom key. An HTTP server may use
    one, both, or none of any information from an Accept value.

    To help with sorting and comparison, this class override behavior of some
    magical functions: __eq__, __ne__, and __cmp__. Still, an HeaderAcceptValue
    is not an hashable, as it is still mutable (even if this is not very
    useful, and should possibly forbidden).

    This class can be easily combined with ``parse_accept_value`` to be
    instantiated:

        >>> info = parse_accept_value('text/html;q=0.8;level=1')
        >>> mimetype = info.get('mimetype')
        >>> options = info.get('options', {})
        >>> value = HeaderAcceptValue(mimetype, **options)
        >>> value.mimetype
        'text/html'
        >>> value.quality
        0.8
        >>> value.options
        {'q': '0.8', 'level': '1'}

    """
    def __init__(self, mimetype, **options):
        self.mimetype = mimetype
        self.options = {}
        self.quality = None
        self.set_options(options)

    def set_options(self, options):
        quality = (
            value
            for key, value in options.iteritems()
            if key == 'q'
        )
        for value in quality:
            self.quality = float(value)
            break

        if self.quality is None:
            self.quality = 1.0

        self.options = options

    def __cmp__(self, other):
        if not hasattr(other, 'quality'):
            raise ValueError('Can not compare with %r' % type(other))

        if self.quality > other.quality:
            return 1
        elif self.quality < other.quality:
            return -1

        return 0

    def __eq__(self, other):
        if not hasattr(other, 'mimetype') or not hasattr(other, 'quality'):
            return False
        return (
            self.mimetype == other.mimetype and self.quality == other.quality
        )

    def __ne__(self, other):
        if not hasattr(other, 'mimetype') or not hasattr(other, 'quality'):
            return True
        return (
            self.mimetype != other.mimetype or self.quality != other.quality
        )


class HeaderAcceptList(list):
    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)
        self.sort()  # Sort from lowest to highest quality onlty to...
        self.reverse()  # ... reverse the order of course!
        self.max_quality = max(item.quality for item in self)

    def __contains__(self, value):
        """Override contains to compare with a mimetype and a quality

        The comparison is done with an equality between the value provided
        and any item in self. The ``value`` might not be an instance of
        HeaderAcceptValue, but as long as it implements an __eq__ method,
        it might be compared with any other HeaderAcceptValue-like object
        contained into self.

        If ``value`` doesn't have ``mimetype`` or ``quality`` attributes,
        this method will try to unpack a two-value iterable (tuple or list),
        and then compare with any item's mimetype and item's quality.

        Finally, if none of these can be done, the value will be compare with
        any item's mimetype.

        """
        if hasattr(value, 'mimetype') and hasattr(value, 'quality'):
            return any(
                # Will call value.__eq__(item)
                # If value does not override __eq__
                # this should always returns False
                value == item
                for item in self
            )

        # Try with a (mimetype, quality) value
        try:
            mimetype, quality = value
            return any(
                mimetype == item.mimetype and quality == item.quality
                for item in self
            )
        except ValueError:
            # Can not unpack value... too bad.
            pass

        # Guess the value is a string to compare with any item's mimetype
        return any(
            value == item.mimetype
            for item in self
        )

    def is_from_browser(self):
        top_accepts = [
            item for item in self if item.quality == self.max_quality
        ]
        return self.is_html_accepted(strict=True) or len(top_accepts) > 1

    def is_html_accepted(self, strict=False):
        mimetypes_compare = HTML_MIMETYPES

        if not strict:
            mimetypes_compare = HTML_MIMETYPES + [
                'text/*', 'application/*', '*/*'
            ]

        return any(accept_value in self for accept_value in (
            HeaderAcceptValue(mimetype, q=self.max_quality)
            for mimetype in mimetypes_compare
        ))


if __name__ == '__main__':
    parser = ArgumentParser(
        description='Show info of an Accept HTTP Header'
    )
    parser.add_argument('header')

    arguments = parser.parse_args()
    print arguments.header
    accepts = HeaderAcceptList(
        HeaderAcceptValue(
            info.get('mimetype'), **info.get('options', {})
        )
        for info in (
        parse_accept_value(value)
        for value in split_accept_header(arguments.header)
    ))

    for accept in accepts:
        print accept.mimetype, accept.quality, accept.options

    print (
        'text/html in accepts: ',
        HeaderAcceptValue('text/html', q='1.0') in accepts
    )
    print '0 in accepts: ', accepts[0] in accepts
    print 'accepts HTML: ', accepts.is_html_accepted()
    print 'accepts HTML (strict): ', accepts.is_html_accepted(strict=True)
    print 'is from browser: ', accepts.is_from_browser()
