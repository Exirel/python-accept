from pytest import raises  # IGNORE:E0611

from http_accept import split_accept_header


def test_split_accept_header():
    """Assert split_accept_header basic behavior

    Input: 'text/html'
    Output: ['text/html']

    """
    accept_header = 'text/html'
    result = split_accept_header(accept_header)

    assert next(result) == 'text/html'
    with raises(StopIteration):
        next(result)


def test_split_accept_header_with_q():
    """Assert split_accept_header behavior with quality option

    Input: 'text/html;q=1.0'
    Output: ['text/html;q=1.0']

    """
    accept_header = 'text/html;q=1.0'
    result = split_accept_header(accept_header)

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
    result = split_accept_header(accept_header)

    assert next(result) == 'text/html'
    assert next(result) == 'application/xml'
    with raises(StopIteration):
        next(result)

    # Same with space
    accept_header = 'text/html, application/xml'
    result = split_accept_header(accept_header)

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
    result = split_accept_header(accept_header)

    assert next(result) == 'text/html'
    assert next(result) == 'application/xml;q=0.8'
    with raises(StopIteration):
        next(result)

    # Same with space
    accept_header = 'text/html, application/xml; q=0.8'
    result = split_accept_header(accept_header)

    assert next(result) == 'text/html'
    assert next(result) == 'application/xml;q=0.8'
    with raises(StopIteration):
        next(result)
