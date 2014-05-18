# -*- coding: utf-8 -*-
from argparse import ArgumentParser


def split_accept_header(accept_header):
    return (value.strip() for value in accept_header.split(','))


def parse_accept_value(accept_value):
    values = accept_value.split(';')
    mimetype = values.pop(0).strip()
    args = dict(
        [part.strip() for part in value.split('=')]
        for value in values
    )
    return {
        'mimetype': mimetype,
        'options': args
    }


class HeaderAcceptValue(object):
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
            return 0

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


class HeaderAccept(list):
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

    def is_accepted(self, mimetype, strict=False):
        result = mimetype in self
        if strict:
            return result

        partial_mimetype = '%s/*' % mimetype.split('/')[0]
        return result or any(
            item.mimetype in [partial_mimetype, '*/*']
            for item in self
        )

    def is_html_accepted(self, strict=False):
        html_type = [
            'text/html',
            'application/xhtml',
            'application/xhtml+xml'
        ]
        if not strict:
            html_type += [
                'text/*',
                '*/*',
            ]

        return any(
            item.mimetype in html_type
            for item in self
            if item.quality == self.max_quality
        )


if __name__ == '__main__':
    parser = ArgumentParser(
        description='Show info of an Accept HTTP Header'
    )
    parser.add_argument('header')

    arguments = parser.parse_args()
    print arguments.header
    accepts = HeaderAccept(
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
