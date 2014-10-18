from decimal import Decimal as D


HTML_MIMETYPES = [
    'text/html',
    'application/xhtml',
    'application/xhtml+xml'
]


def split_accept_header(accept_header):
    """Split accept header into accept header value's data and return generator

    One can iterate over the result of this function's call, at it returns
    a generator - or transform the result into a python list:

        >>> list(split_accept_header('text/html, application/xml;q=0.8'))
        ['text/html', 'application/xml;q=0.8']

    This function can be used, for example, with ``parse_accept_value``:

        >>> values = split_accept_header('text/html, application/xml;q=0.8')
        >>> for value in values:
        ...     print(parse_accept_value(value))
        ...
        {'mimetype': 'text/html', 'options': {}}
        {'mimetype': 'application/xml', 'options': {'q': '0.8'}}

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
    if accept_value is None:
        raise TypeError(
            'parse_accept_value() argument must be a string, '
            'not \'%s\'' % type(accept_value)
        )

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


class MediaRange(object):
    """Represent a media-range of an HTTP Accept header.

    RFC 2616, section 14.1 defines Accept header as a list of ``media-range``
    elements (either ``*/*``, ``type/*``, or ``type/subtype``) with parameters.

    A MediaRange is composed of a mimetype and a list of options, such as ``q``
    (reserved key), or any custom key. An HTTP server may use one, both, or
    none of any information from a media-range.

    A MediaRange can be compared and sorted in a list of MediaRange objects.

    This class can be easily combined with ``parse_accept_value`` to be
    instantiated:

        >>> info = parse_accept_value('text/html;q=0.8;level=1')
        >>> mimetype = info.get('mimetype')
        >>> options = info.get('options', {})
        >>> media = MediaRange(mimetype, **options)
        >>> media.mimetype
        'text/html'
        >>> media.quality
        0.8
        >>> media.options
        {'q': '0.8', 'level': '1'}

    """
    def __init__(self, mimetype, **options):
        """Build with a mimetype and options.

        The specific parameter ``q`` is saved into the ``quality`` attribute,
        while all options are kept in ``options`` attribute (including ``q``).

        If the ``q`` parameter does not exist, the default value 1.0 is assumed
        but the ``options`` attribute won't contain it.

        """
        self.mimetype = mimetype
        self._quality = D(options.get('q', 1.0)) if 'q' in options else D(1.0)
        self._raw_options = options
        self._options = {
            key: value
            for key, value in options.items()
            if 'q' != key
        }

    def __eq__(self, other):
        """Return if other is considered equal to self.

        They are equal if they have the same ``mimetype``, ``quality`` and
        ``options``.

        """
        if (not hasattr(other, 'mimetype')
            or not hasattr(other, 'quality')
            or not hasattr(other, 'options')):
            return False

        return (
            self.mimetype == other.mimetype
            and self.quality == other.quality
            and self.options == other.options
        )

    def __ne__(self, other):
        """Return if other is not considered equal to self.

        They are not equal if other has not the same ``mimetype`` nor
        ``quality`` values nor ``options``.

        """
        if (not hasattr(other, 'mimetype')
            or not hasattr(other, 'quality')
            or not hasattr(other, 'options')):
            return True

        return (
            self.mimetype != other.mimetype
            or self.quality != other.quality
            or self.options != other.options
        )

    def __lt__(self, other):
        """Return if self's quality is lower than other's quality.

        This method will only be able to compare with other with a ``quality``
        attribute. One may use duck typing to compare two instances of
        different classes without error.

        """
        if not hasattr(other, 'quality'):
            raise TypeError('unorderable types: %s < %s'
                            % (type(self), type(other)))

        return self.quality < other.quality

    def __le__(self, other):
        """Return if self's quality is lower or equal than other's quality.

        This method will only be able to compare with other with a ``quality``
        attribute. One may use duck typing to compare two instances of
        different classes without error.

        """
        if not hasattr(other, 'quality'):
            raise TypeError('unorderable types: %s <= %s'
                            % (type(self), type(other)))

        return self.quality <= other.quality

    def __gt__(self, other):
        """Return if self's quality is greater than other's quality.

        This method will only be able to compare with other with a ``quality``
        attribute. One may use duck typing to compare two instances of
        different classes without error.

        """
        if not hasattr(other, 'quality'):
            raise TypeError('unorderable types: %s > %s'
                            % (type(self), type(other)))

        return self.quality > other.quality

    def __ge__(self, other):
        """Return if self's quality is greater or equal than other's quality.

        This method will only be able to compare with other with a ``quality``
        attribute. One may use duck typing to compare two instances of
        different classes without error.

        """
        if not hasattr(other, 'quality'):
            raise TypeError('unorderable types: %s >= %s'
                            % (type(self), type(other)))

        return self.quality >= other.quality

    @property
    def quality(self):
        """Read-only quality parameter."""
        return self._quality

    @property
    def options(self):
        """Read-only options parameter.

        This attribute does not contains the ``q`` parameter.

        """
        return self._options

    def set_options(self, key, value):
        """Set an option's value.
        """
        if key == 'q':
            if self._quality != value:
                fixed_decimal_value = D(value)
                self._quality = fixed_decimal_value
                self._raw_options['q'] = fixed_decimal_value
        else:
            self._raw_options[key] = value
            self._options[key] = value

    def to_http(self, explicit_quality=False):
        """Return the string value of the media-range suitable for HTTP Accept.

        The ``q`` parameter will be always displayed first in the list of
        parameters. By default, if the ``q`` is not from the source options,
        it won't appear in the result. This behavior can be changed by using
        ``explicit_quality=True``::

            >>> MediaRange('text/html', q=1.0).to_http()
            'text/html;q=1.0'
            >>> MediaRange('text/html').to_http()
            'text/html'
            >>> MediaRange('text/html').to_http(explicit_quality=True)
            'text/html;q=1.0'
            >>> MediaRange('text/html', aaa=1).to_http(explicit_quality=True)
            'text/html;q=1.0;aaa=1'

        """
        # Manage to have always `q` as first parameter
        if explicit_quality or 'q' in self._raw_options:
            base = ['q=%0.1f' % self.quality]
        else:
            base = []

        options = [
            '='.join([key, value])
            for key, value in sorted(self._options.items())
        ]

        return ';'.join(
            [self.mimetype] + base + options
        )


class HeaderAccept(list):
    """Smart list of MediaRange with specific behaviors

    HeaderAccept overrides the contains list's behavior to be able to
    compare properly two (or kind of) MediaRange.

    One can use it like this:

        >>> accept_html = MediaRange('text/html', q=1.0)
        >>> accept_text = MediaRange('text/*', q=0.9)
        >>> accept_wildcard = MediaRange('*/*', q=0.8)
        >>> accepts = HeaderAccept([
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
        MediaRange, but as long as it implements an __eq__ method,
        it might be compared with any other MediaRange-like object
        contained into self.

        If ``value`` doesn't have ``mimetype`` or ``quality`` attributes,
        this method will try to unpack a two-value iterable (tuple or list),
        and then compare with any item's mimetype and item's quality.

        Finally, if none of these can be done, the value will be compare with
        any item's mimetype.

        """
        if (hasattr(value, 'mimetype')
            and hasattr(value, 'quality')
            and hasattr(value, 'options')):
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
        except ValueError:
            # Can not unpack value... too bad but we can ignore this case.
            pass
        else:
            d_quality = D(quality)  # We don't need to catch errors here
            return any(
                mimetype == item.mimetype and d_quality == item.quality
                for item in self
            )

        # Guess the value is a string to compare with any item's mimetype
        return any(
            value == item.mimetype
            for item in self
        )

    def append(self, x):
        """Override append to update max_quality on list update."""
        if not hasattr(x, 'quality') or not hasattr(x, 'mimetype'):
            raise TypeError(
                'append() only accept object with '
                'a \'quality\' and a \'mimetype\' attribute, '
                'not \'%s\'' % type(x)
            )

        if self.max_quality < x.quality:
            self.max_quality = x.quality

        return super(HeaderAccept, self).append(x)

    def to_http(self):
        """Return the HTTP Header string value of the Accept header list"""
        return ','.join(
            value.to_http() for value in sorted(self, reverse=True)
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
            MediaRange(mimetype, q=self.max_quality)
            for mimetype in mimetypes_compare
        ))
