# -*- coding: utf-8 -*-
"""Unit-test (using py.test) for accept package."""

import accept

from pytest import raises  # IGNORE:E0611


def test_split_accept_header():
    """Assert split_accept_header basic behavior"""
    accept_header = 'text/html'
    result = accept.split_accept_header(accept_header)

    assert result.next() == 'text/html'
    with raises(StopIteration):
        result.next()


def test_split_accept_header_with_q():
    """Assert split_accept_header behavior with quality option"""
    accept_header = 'text/html;q=1.0'
    result = accept.split_accept_header(accept_header)

    assert result.next() == 'text/html;q=1.0'
    with raises(StopIteration):
        result.next()


def test_split_accept_header_multiple_values():
    """Assert split_accept_header behavior with multiple Accept values"""
    accept_header = 'text/html,application/xml'
    result = accept.split_accept_header(accept_header)

    assert result.next() == 'text/html'
    assert result.next() == 'application/xml'
    with raises(StopIteration):
        result.next()

    # Same with space
    accept_header = 'text/html, application/xml'
    result = accept.split_accept_header(accept_header)

    assert result.next() == 'text/html'
    assert result.next() == 'application/xml'
    with raises(StopIteration):
        result.next()


def test_split_accept_header_multiple_values_and_quality():
    """Assert split_accept_header behavior with multiple Accept values and
    options

    """
    accept_header = 'text/html,application/xml;q=0.8'
    result = accept.split_accept_header(accept_header)

    assert result.next() == 'text/html'
    assert result.next() == 'application/xml;q=0.8'
    with raises(StopIteration):
        result.next()

    # Same with space
    accept_header = 'text/html, application/xml;q=0.8'
    result = accept.split_accept_header(accept_header)

    assert result.next() == 'text/html'
    assert result.next() == 'application/xml;q=0.8'
    with raises(StopIteration):
        result.next()


# -----------------------------------------------------------------------------

def test_parse_accept_value():
    """Assert parse_accept_value basic behavior"""
    test_value = 'text/html'
    expected = {'mimetype': 'text/html', 'options': {}}
    assert accept.parse_accept_value(test_value) == expected


def test_parse_accept_value_with_quality():
    """Assert parse_accept_value behavior with quality option"""
    test_value = 'text/html;q=0.8'
    expected = {'mimetype': 'text/html', 'options': {'q': '0.8'}}
    assert accept.parse_accept_value(test_value) == expected

    # Same with spaces
    test_value = 'text/html ; q=0.8'
    expected = {'mimetype': 'text/html', 'options': {'q': '0.8'}}
    assert accept.parse_accept_value(test_value) == expected


def test_parse_accept_value_with_options():
    """Assert parse_accept_value behavior with custom options"""
    test_value = 'text/html;version=2.4.5;custom=7814'
    expected = {
        'mimetype': 'text/html',
        'options': {'version': '2.4.5', 'custom': '7814'}
    }
    assert accept.parse_accept_value(test_value) == expected

    # Same with spaces
    test_value = 'text/html ; version=2.4.5 ; custom=7814'
    expected = {
        'mimetype': 'text/html',
        'options': {'version': '2.4.5', 'custom': '7814'}
    }
    assert accept.parse_accept_value(test_value) == expected


# -----------------------------------------------------------------------------


def test_HeaderAcceptValue():
    """Assert HeaderAcceptValue object's basic behavior"""
    accept_value = accept.HeaderAcceptValue(mimetype='text/html')

    assert accept_value.mimetype == 'text/html'
    assert accept_value.quality == 1.0  # Default value
    assert accept_value.options == {}


def test_HeaderAcceptValue_with_quality():
    """Assert HeaderAcceptValue object's behavior with q options"""
    accept_value = accept.HeaderAcceptValue(mimetype='text/html', q='0.8')

    assert accept_value.mimetype == 'text/html'
    assert accept_value.quality == 0.8  # Default value
    assert accept_value.options == {'q': '0.8'}


def test_HeaderAcceptValue_equals():
    """Assert HeaderAcceptValue object's behavior on equality"""
    accept_html = accept.HeaderAcceptValue(mimetype='text/html')
    accept_html_bis = accept.HeaderAcceptValue(mimetype='text/html')
    accept_html_low = accept.HeaderAcceptValue(mimetype='text/html', q='0.8')
    accept_xhtml = accept.HeaderAcceptValue(mimetype='application/xml+xhtml')

    # IS/IS NOT
    assert accept_html is accept_html
    assert accept_html is not accept_html_bis
    assert accept_html is not accept_html_low
    assert accept_html is not accept_xhtml

    # X EQUAL Y
    assert accept_html == accept_html
    assert accept_html == accept_html_bis
    assert not (accept_html == accept_html_low)
    assert not (accept_html == accept_xhtml)

    # X NOT EQUAL Y
    assert not (accept_html != accept_html)
    assert not (accept_html != accept_html_bis)
    assert accept_html != accept_html_low
    assert accept_html != accept_xhtml

    not_equal = object()  # Does not have mimetype nor quality attribute
    assert not (accept_html == not_equal)
    assert accept_html != not_equal


def test_HeaderAcceptValue_sort():
    """Assert sorting list of HeaderAcceptValue objects"""
    accept_html = accept.HeaderAcceptValue(mimetype='text/html')
    accept_xml = accept.HeaderAcceptValue(
        mimetype='application/xml', q='0.9'
    )
    accept_text_wildcard = accept.HeaderAcceptValue(mimetype='text/*', q='0.8')
    accept_wildcard = accept.HeaderAcceptValue(mimetype='*/*', q='0.8')

    values = [accept_html, accept_xml, accept_text_wildcard]

    # Sort from the lowest to the highest quality
    assert sorted(values) == [accept_text_wildcard, accept_xml, accept_html]

    values = [
        accept_html,
        accept_text_wildcard, accept_wildcard,  # Middle position
        accept_xml
    ]

    # Order is kept when ordering elements of the same quality
    assert sorted(values) == [
        accept_text_wildcard, accept_wildcard,  # First position
        accept_xml,
        accept_html
    ]

    # Can not be compared with object without quality
    with raises(ValueError):
        sorted([1, 2, accept_html])

    class Fake(object):
        quality = 0.8

    fake_type = Fake()

    assert sorted([fake_type, accept_html]) == [fake_type, accept_html]
    assert sorted([accept_html, fake_type]) == [fake_type, accept_html]


def test_HeaderAcceptValue_compare():
    """Assert <, <=, > and >= compare only quality, not mimetype"""
    accept_html = accept.HeaderAcceptValue(mimetype='text/html')
    accept_xml = accept.HeaderAcceptValue(
        mimetype='application/xml', q='0.9'
    )
    accept_wildcard = accept.HeaderAcceptValue(
       mimetype='application/*', q='0.9'
    )

    # Specific comparison
    assert accept_html > accept_xml
    assert accept_html >= accept_xml
    assert not (accept_html < accept_xml)
    assert not (accept_html <= accept_xml)

    # Symetric operation
    assert accept_xml < accept_html
    assert accept_xml <= accept_html
    assert not (accept_xml > accept_html)
    assert not (accept_xml >= accept_html)

    # Not-strict comparison
    assert accept_wildcard >= accept_xml
    assert accept_wildcard <= accept_xml

    # Symetric operation
    assert accept_xml <= accept_wildcard
    assert accept_xml >= accept_wildcard
