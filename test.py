# -*- coding: utf-8 -*-
"""Unit-test (using py.test) for accept package."""

import http_accept

from pytest import raises  # IGNORE:E0611
from http_accept import HeaderAcceptValue


def test_split_accept_header():
    """Assert split_accept_header basic behavior

    Input: 'text/html'
    Output: ['text/html']

    """
    accept_header = 'text/html'
    result = http_accept.split_accept_header(accept_header)

    assert next(result) == 'text/html'
    with raises(StopIteration):
        next(result)


def test_split_accept_header_with_q():
    """Assert split_accept_header behavior with quality option

    Input: 'text/html;q=1.0'
    Output: ['text/html;q=1.0']

    """
    accept_header = 'text/html;q=1.0'
    result = http_accept.split_accept_header(accept_header)

    assert next(result) == 'text/html;q=1.0'
    with raises(StopIteration):
        next(result)


def test_split_accept_header_multiple_values():
    """Assert split_accept_header behavior with multiple Accept values

    Input: 'text/html,application/xml'
    Output: ['text/html', 'application/xml']

    Spaces are ignored.

    """
    accept_header = 'text/html,application/xml'
    result = http_accept.split_accept_header(accept_header)

    assert next(result) == 'text/html'
    assert next(result) == 'application/xml'
    with raises(StopIteration):
        next(result)

    # Same with space
    accept_header = 'text/html, application/xml'
    result = http_accept.split_accept_header(accept_header)

    assert next(result) == 'text/html'
    assert next(result) == 'application/xml'
    with raises(StopIteration):
        next(result)


def test_split_accept_header_multiple_values_and_quality():
    """Assert split_accept_header behavior with multiple Accept values and
    options

    Input: 'text/html,application/xml;q=0.8'
    Output: ['text/html', 'application/xml;q=0.8']

    Spaces are ignored.

    """
    accept_header = 'text/html,application/xml;q=0.8'
    result = http_accept.split_accept_header(accept_header)

    assert next(result) == 'text/html'
    assert next(result) == 'application/xml;q=0.8'
    with raises(StopIteration):
        next(result)

    # Same with space
    accept_header = 'text/html, application/xml; q=0.8'
    result = http_accept.split_accept_header(accept_header)

    assert next(result) == 'text/html'
    assert next(result) == 'application/xml;q=0.8'
    with raises(StopIteration):
        next(result)


# -----------------------------------------------------------------------------


def test_parse_accept_value():
    """Assert parse_accept_value basic behavior"""
    test_value = 'text/html'
    expected = {'mimetype': 'text/html', 'options': {}}
    assert http_accept.parse_accept_value(test_value) == expected


def test_parse_accept_value_none():
    """Assert parse_accept_value raise a TypeError with None"""
    with raises(TypeError):
        http_accept.parse_accept_value(None)


def test_parse_accept_value_empty():
    """Assert parse_accept_value with an empty input string"""
    test_value = ''
    expected = {'mimetype': '', 'options': {}}
    assert http_accept.parse_accept_value(test_value) == expected


def test_parse_accept_value_with_quality():
    """Assert parse_accept_value behavior with quality option"""
    test_value = 'text/html;q=0.8'
    expected = {'mimetype': 'text/html', 'options': {'q': '0.8'}}
    assert http_accept.parse_accept_value(test_value) == expected

    # Same with spaces
    test_value = 'text/html ; q=0.8'
    expected = {'mimetype': 'text/html', 'options': {'q': '0.8'}}
    assert http_accept.parse_accept_value(test_value) == expected


def test_parse_accept_value_with_options():
    """Assert parse_accept_value behavior with custom options"""
    test_value = 'text/html;version=2.4.5;custom=7814'
    expected = {
        'mimetype': 'text/html',
        'options': {'version': '2.4.5', 'custom': '7814'}
    }
    assert http_accept.parse_accept_value(test_value) == expected

    # Same with spaces
    test_value = 'text/html ; version=2.4.5 ; custom=7814'
    expected = {
        'mimetype': 'text/html',
        'options': {'version': '2.4.5', 'custom': '7814'}
    }
    assert http_accept.parse_accept_value(test_value) == expected


# -----------------------------------------------------------------------------


def test_HeaderAcceptValue():
    """Assert HeaderAcceptValue object's basic behavior"""
    accept_value = http_accept.HeaderAcceptValue(mimetype='text/html')

    assert accept_value.mimetype == 'text/html'
    assert accept_value.quality == 1.0  # Default value
    assert accept_value.options == {}


def test_HeaderAcceptValue_with_quality():
    """Assert HeaderAcceptValue object's behavior with q options"""
    accept_value = http_accept.HeaderAcceptValue(mimetype='text/html', q='0.8')

    assert accept_value.mimetype == 'text/html'
    assert accept_value.quality == 0.8  # Default value
    assert accept_value.options == {'q': '0.8'}


def test_HeaderAcceptValue_equals():
    """Assert HeaderAcceptValue object's behavior on equality"""
    accept_html = http_accept.HeaderAcceptValue(mimetype='text/html')
    accept_html_bis = http_accept.HeaderAcceptValue(mimetype='text/html')
    accept_html_low = http_accept.HeaderAcceptValue(mimetype='text/html', q='0.8')
    accept_xhtml = http_accept.HeaderAcceptValue(mimetype='application/xml+xhtml')

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
    accept_html = http_accept.HeaderAcceptValue(mimetype='text/html')
    accept_xml = http_accept.HeaderAcceptValue(
        mimetype='application/xml', q='0.9'
    )
    accept_text_wildcard = http_accept.HeaderAcceptValue(mimetype='text/*', q='0.8')
    accept_wildcard = http_accept.HeaderAcceptValue(mimetype='*/*', q='0.8')

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
    with raises(TypeError):
        sorted([1, 2, accept_html])

    class Fake(object):
        quality = 0.8

    fake_type = Fake()

    assert sorted([fake_type, accept_html]) == [fake_type, accept_html]
    assert sorted([accept_html, fake_type]) == [fake_type, accept_html]


def test_HeaderAcceptValue_compare():
    """Assert <, <=, > and >= compare only quality, not mimetype"""
    accept_html = http_accept.HeaderAcceptValue(mimetype='text/html')
    accept_xml = http_accept.HeaderAcceptValue(
        mimetype='application/xml', q='0.9'
    )
    accept_wildcard = http_accept.HeaderAcceptValue(
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


def test_HeaderAcceptValue_to_http():
    """Assert value.to_http() returns expected string value"""
    accept_html = http_accept.HeaderAcceptValue(mimetype='text/html')
    accept_xml = http_accept.HeaderAcceptValue(mimetype='application/xml', q='0.9')
    accept_text_level = http_accept.HeaderAcceptValue(
        mimetype='text/plain', level='1', version='1.0'
    )

    assert accept_html.to_http() == 'text/html'
    assert accept_xml.to_http() == 'application/xml;q=0.9'
    assert accept_text_level.to_http() == 'text/plain;version=1.0;level=1'

# -----------------------------------------------------------------------------


def test_HeaderAcceptList():
    accept_html = http_accept.HeaderAcceptValue('text/html', q='0.8')
    accept_xml = http_accept.HeaderAcceptValue('application/xml', q='0.5')
    accepts = http_accept.HeaderAcceptList([accept_html, accept_xml])

    assert accepts.max_quality == 0.8
    assert len(accepts) == 2
    assert list(accepts) == [accept_html, accept_xml]


def test_HeaderAcceptList_append():
    accept_html = http_accept.HeaderAcceptValue('text/html', q='0.8')
    accept_xml = http_accept.HeaderAcceptValue('application/xml', q='1.0')
    accepts = http_accept.HeaderAcceptList([accept_html])

    assert accepts.max_quality == 0.8
    assert len(accepts) == 1

    accepts.append(accept_xml)
    assert accepts.max_quality == 1.0
    assert len(accepts) == 2

    with raises(TypeError):
        accepts.append(object())


def test_HeaderAcceptList_contains():
    accept_html = http_accept.HeaderAcceptValue('text/html', q='0.8')
    accept_xml = http_accept.HeaderAcceptValue('application/xml', q='0.5')
    accepts = http_accept.HeaderAcceptList([accept_html, accept_xml])

    same_accept_html = HeaderAcceptValue(
        accept_html.mimetype, q=accept_html.quality
    )
    not_same_accept_html = HeaderAcceptValue(
        accept_html.mimetype, q='0.1'
    )

    assert accept_html in accepts
    assert accept_xml in accepts
    assert same_accept_html in accepts
    assert not_same_accept_html not in accepts


def test_HeaderAcceptList_contains_tuple():
    accept_html = http_accept.HeaderAcceptValue('text/html', q='0.8')
    accept_xml = http_accept.HeaderAcceptValue('application/xml', q='0.5')
    accepts = http_accept.HeaderAcceptList([accept_html, accept_xml])

    assert ('text/html', '0.8') in accepts
    assert ('application/xml', '0.5') in accepts
    assert ('text/html', 0.8) in accepts
    assert ('application/xml', 0.5) in accepts
    assert ('text/html', '0.5') not in accepts
    assert ('text/html', 0.5) not in accepts


def test_HeaderAcceptList_contains_mimetype():
    accept_html = http_accept.HeaderAcceptValue('text/html', q='0.8')
    accept_xml = http_accept.HeaderAcceptValue('application/xml', q='0.5')
    accepts = http_accept.HeaderAcceptList([accept_html, accept_xml])

    assert 'text/html' in accepts
    assert 'application/xml' in accepts
    assert 'text/plain' not in accepts


def test_HeaderAcceptList_to_http():
    """Assert value.to_http() returns expected string value"""
    accept_html = http_accept.HeaderAcceptValue(mimetype='text/html')
    accept_xml = http_accept.HeaderAcceptValue(mimetype='application/xml', q='0.9')
    accept_text = http_accept.HeaderAcceptValue(
        mimetype='text/plain', level='1', version='1.0'
    )
    expected = 'text/html,text/plain;version=1.0;level=1,application/xml;q=0.9'

    accepts = http_accept.HeaderAcceptList([accept_html, accept_xml, accept_text])
    assert accepts.to_http() == expected


def test_HeaderAcceptList_get_max_quality_accept():
    accept_html = http_accept.HeaderAcceptValue('text/html', q='0.8')
    accept_xml = http_accept.HeaderAcceptValue('application/xml', q='0.5')
    accepts = http_accept.HeaderAcceptList([accept_html, accept_xml])

    result = accepts.get_max_quality_accept()

    assert list(result) == [accept_html]
    assert isinstance(result, http_accept.HeaderAcceptList)
    assert accept_html in result
    assert accept_xml not in result


def test_HeaderAcceptList_is_html_accepted():
    accept_html = http_accept.HeaderAcceptValue('text/html', q='0.8')
    accept_xhtml = http_accept.HeaderAcceptValue('application/xhtml', q='0.8')
    accept_xhtml_xml = http_accept.HeaderAcceptValue(
        'application/xhtml+xml', q='0.8'
    )
    accept_xml = http_accept.HeaderAcceptValue('application/xml', q='0.5')

    accepts = http_accept.HeaderAcceptList([accept_html, accept_xml])
    accepts_xhtml = http_accept.HeaderAcceptList([accept_xhtml, accept_xml])
    accepts_xhtml_xml = http_accept.HeaderAcceptList([accept_xhtml_xml, accept_xml])

    assert accepts.is_html_accepted(strict=True) is True
    assert accepts_xhtml.is_html_accepted(strict=True) is True
    assert accepts_xhtml_xml.is_html_accepted(strict=True) is True

    accepts = http_accept.HeaderAcceptList([accept_xml])
    assert accepts.is_html_accepted(strict=True) is False


def test_HeaderAcceptList_is_html_accepted_wildcard():
    accept_text_wildcard = http_accept.HeaderAcceptValue('text/*', q='0.8')
    accept_application_wildcard = http_accept.HeaderAcceptValue(
        'application/*', q='0.8'
    )
    accept_wildcard = http_accept.HeaderAcceptValue('*/*', q='0.8')

    accepts = http_accept.HeaderAcceptList([
        accept_text_wildcard, accept_application_wildcard, accept_wildcard
    ])
    assert accepts.is_html_accepted(strict=True) is False
    assert accepts.is_html_accepted() is True
