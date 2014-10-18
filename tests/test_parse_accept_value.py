from pytest import raises  # IGNORE:E0611

from http_accept import parse_accept_value


def test_parse_accept_value():
    """Assert parse_accept_value basic behavior"""
    test_value = 'text/html'
    expected = {'mimetype': 'text/html', 'options': {}}
    assert parse_accept_value(test_value) == expected


def test_parse_accept_value_none():
    """Assert parse_accept_value raise a TypeError with None"""
    with raises(TypeError):
        parse_accept_value(None)


def test_parse_accept_value_empty():
    """Assert parse_accept_value with an empty input string"""
    test_value = ''
    expected = {'mimetype': '', 'options': {}}
    assert parse_accept_value(test_value) == expected


def test_parse_accept_value_with_quality():
    """Assert parse_accept_value behavior with quality option"""
    test_value = 'text/html;q=0.8'
    expected = {'mimetype': 'text/html', 'options': {'q': '0.8'}}
    assert parse_accept_value(test_value) == expected

    # Same with spaces
    test_value = 'text/html ; q=0.8'
    expected = {'mimetype': 'text/html', 'options': {'q': '0.8'}}
    assert parse_accept_value(test_value) == expected


def test_parse_accept_value_with_options():
    """Assert parse_accept_value behavior with custom options"""
    test_value = 'text/html;version=2.4.5;custom=7814'
    expected = {
        'mimetype': 'text/html',
        'options': {'version': '2.4.5', 'custom': '7814'}
    }
    assert parse_accept_value(test_value) == expected

    # Same with spaces
    test_value = 'text/html ; version=2.4.5 ; custom=7814'
    expected = {
        'mimetype': 'text/html',
        'options': {'version': '2.4.5', 'custom': '7814'}
    }
    assert parse_accept_value(test_value) == expected
