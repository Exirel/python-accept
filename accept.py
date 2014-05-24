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
        """Build with a mimetype and save options

        The specific parameter ``q`` is saved into the ``quality`` attribute,
        while all options are kept in ``options`` attribute (including ``q``).

        """
        self.mimetype = mimetype
        self.quality = float(options.get('q', 1.0)) if 'q' in options else 1.0
        self.options = options

    def __cmp__(self, other):
        """Compare with other using quality attribute.

        This method will only be able to compare with other with a ``quality``
        attribute. One may use duck typing to compare two instances of
        different classes without error.

        One is greater than other if its quality is greater. The same way,
        it is lower than other if its quality is lower. Else, they are
        considered equal.

        If ``other`` does not have a ``quality`` attribute, a ValueError will
        be raised.

        Therefore, one will need to provide a compare method when using sorted
        on a list containing both HeaderAcceptValue instance and invalid one.

        """
        if not hasattr(other, 'quality'):
            raise ValueError('Can not compare with %r' % type(other))

        if self.quality > other.quality:
            return 1
        elif self.quality < other.quality:
            return -1

        return 0

    def __eq__(self, other):
        """Return True if other is considered equal to self.

        Both are equal if other has the same ``mimetype`` and ``quality``
        values. In any other cases, they won't be equal.

        """
        if not hasattr(other, 'mimetype') or not hasattr(other, 'quality'):
            return False
        return (
            self.mimetype == other.mimetype and self.quality == other.quality
        )

    def __ne__(self, other):
        """Return True if other is not considered equal to self.

        They are not equal if other has not the same ``mimetype`` nor
        ``quality`` values. In any other cases, they are considered equal.

        """
        if not hasattr(other, 'mimetype') or not hasattr(other, 'quality'):
            return True
        return (
            self.mimetype != other.mimetype or self.quality != other.quality
        )


class HeaderAcceptList(list):
    """Smart list for HeaderAcceptValue with specific behaviors

    HeaderAcceptList overrides the contains list's behavior to be able to
    compare properly two (kind of) HeaderAcceptValue.

    One can use it like this:

        >>> accept_html = HeaderAcceptValue('text/html', q=1.0)
        >>> accept_text = HeaderAcceptValue('text/*', q=0.9)
        >>> accept_wildcard = HeaderAcceptValue('*/*', q=0.8)
        >>> accepts = HeaderAcceptList([
        ...     accept_html, accept_text, accept_wildcard
        ... ])
        >>> accepts.max_quality
        1.0
        >>> 'text/html' in accepts
        True
        >>> accepts.is_html_accept()
        True

    """
    def __init__(self, *args, **kwargs):
        """Build the list and extract the max quality value"""
        list.__init__(self, *args, **kwargs)
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
                mimetype == item.mimetype and str(quality) == str(item.quality)
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

    def get_max_quality_accept(self):
        """Return a new instance of self's class with only max quality accepts

        This method can be used to retrieve only the top-level accepted
        mimetype in order to perform the first level of content negotiation.

        """
        return self.__class__(
            item
            for item in self
            if item.quality == self.max_quality
        )

    def is_html_accepted(self, strict=False):
        """Return True if HTML is an accepted type for this list."""
        mimetypes_compare = HTML_MIMETYPES

        if not strict:
            mimetypes_compare = HTML_MIMETYPES + [
                'text/*', 'application/*', '*/*'
            ]

        return any(accept_value in self for accept_value in (
            HeaderAcceptValue(mimetype, q=self.max_quality)
            for mimetype in mimetypes_compare
        ))
