from decimal import Decimal

from pytest import raises  # IGNORE:E0611

from http_accept import HeaderAccept, MediaRange


def test_HeaderAccept():
    accept_html = MediaRange('text/html', q='0.8')
    accept_xml = MediaRange('application/xml', q='0.5')
    accepts = HeaderAccept([accept_html, accept_xml])

    assert accepts.max_quality == Decimal('0.8')
    assert len(accepts) == 2
    assert list(accepts) == [accept_html, accept_xml]


def test_HeaderAccept_append():
    accept_html = MediaRange('text/html', q='0.8')
    accept_xml = MediaRange('application/xml', q='1.0')
    accepts = HeaderAccept([accept_html])

    assert accepts.max_quality == Decimal('0.8')
    assert len(accepts) == 1

    accepts.append(accept_xml)
    assert accepts.max_quality == 1.0
    assert len(accepts) == 2

    with raises(TypeError):
        accepts.append(object())


def test_HeaderAccept_contains():
    accept_html = MediaRange('text/html', q='0.8')
    accept_xml = MediaRange('application/xml', q='0.5')
    accepts = HeaderAccept([accept_html, accept_xml])

    same_accept_html = MediaRange(
        accept_html.mimetype, q=accept_html.quality
    )
    not_same_accept_html = MediaRange(
        accept_html.mimetype, q='0.1'
    )

    assert accept_html in accepts
    assert accept_xml in accepts
    assert same_accept_html in accepts
    assert not_same_accept_html not in accepts


def test_HeaderAccept_contains_tuple():
    accept_html = MediaRange('text/html', q='0.8')
    accept_xml = MediaRange('application/xml', q='0.5')
    accepts = HeaderAccept([accept_html, accept_xml])

    assert ('text/html', '0.8') in accepts
    assert ('application/xml', '0.5') in accepts
    assert ('text/html', Decimal('0.8')) in accepts
    assert ('application/xml', Decimal('0.5')) in accepts

    # Mimetype exists but not the same quality
    assert ('text/html', '0.5') not in accepts
    assert ('text/html', Decimal('0.5')) not in accepts


def test_HeaderAccept_contains_mimetype():
    accept_html = MediaRange('text/html', q='0.8')
    accept_xml = MediaRange('application/xml', q='0.5')
    accepts = HeaderAccept([accept_html, accept_xml])

    assert 'text/html' in accepts
    assert 'application/xml' in accepts
    assert 'text/plain' not in accepts


def test_HeaderAccept_to_http():
    """Assert value.to_http() returns expected string value"""
    accept_html = MediaRange(mimetype='text/html')
    accept_xml = MediaRange(mimetype='application/xml', q='0.9')
    accept_text = MediaRange(
        mimetype='text/plain', level='1', version='1.0'
    )
    expected = 'text/html,text/plain;level=1;version=1.0,application/xml;q=0.9'

    accepts = HeaderAccept([accept_html, accept_xml, accept_text])
    assert accepts.to_http() == expected


def test_HeaderAccept_get_max_quality_accept():
    accept_html = MediaRange('text/html', q='0.8')
    accept_xml = MediaRange('application/xml', q='0.5')
    accepts = HeaderAccept([accept_html, accept_xml])

    result = accepts.get_max_quality_accept()

    assert list(result) == [accept_html]
    assert isinstance(result, HeaderAccept)
    assert accept_html in result
    assert accept_xml not in result


def test_HeaderAccept_is_html_accepted():
    accept_html = MediaRange('text/html', q='0.8')
    accept_xhtml = MediaRange('application/xhtml', q='0.8')
    accept_xhtml_xml = MediaRange(
        'application/xhtml+xml', q='0.8'
    )
    accept_xml = MediaRange('application/xml', q='0.5')

    accepts = HeaderAccept([accept_html, accept_xml])
    accepts_xhtml = HeaderAccept([accept_xhtml, accept_xml])
    accepts_xhtml_xml = HeaderAccept([accept_xhtml_xml, accept_xml])

    assert accepts.is_html_accepted(strict=True) is True
    assert accepts_xhtml.is_html_accepted(strict=True) is True
    assert accepts_xhtml_xml.is_html_accepted(strict=True) is True

    accepts = HeaderAccept([accept_xml])
    assert accepts.is_html_accepted(strict=True) is False


def test_HeaderAccept_is_html_accepted_wildcard():
    accept_text_wildcard = MediaRange('text/*', q='0.8')
    accept_application_wildcard = MediaRange(
        'application/*', q='0.8'
    )
    accept_wildcard = MediaRange('*/*', q='0.8')

    accepts = HeaderAccept([
        accept_text_wildcard, accept_application_wildcard, accept_wildcard
    ])
    assert accepts.is_html_accepted(strict=True) is False
    assert accepts.is_html_accepted() is True
