from decimal import Decimal

from pytest import raises  # IGNORE:E0611

from http_accept import MediaRange


def test_MediaRange():
    """Assert MediaRange object's basic behavior"""
    accept_value = MediaRange(mimetype='text/html')

    assert accept_value.mimetype == 'text/html'
    assert accept_value.quality == Decimal('1.0')  # Default value
    assert accept_value.options == {}


def test_MediaRange_with_quality():
    """Assert MediaRange object's behavior with q options"""
    accept_value = MediaRange(mimetype='text/html', q='0.8')

    assert accept_value.mimetype == 'text/html'
    assert accept_value.quality == Decimal('0.8')
    assert accept_value.options == {}  # q does not appear in options


def test_MediaRange_with_parameters():
    """Assert MediaRange object's behavior with q options"""
    accept_value = MediaRange(mimetype='text/html', level='1')

    assert accept_value.mimetype == 'text/html'
    assert accept_value.quality == Decimal('1.0')
    assert accept_value.options == {'level': '1'}


def test_MediaRange_equals():
    """Assert MediaRange object's behavior on equality and identity.

    Since the MediaRange object has its own mechanic to compare two objects,
    assertion are added on identity. Even if a MediaRange equals another one,
    it does not mean they are the same object. If this behavior changes one
    day, this test will fail as expected for such major change.

    """
    accept_html = MediaRange(mimetype='text/html')
    accept_html_bis = MediaRange(mimetype='text/html')
    accept_html_low = MediaRange(mimetype='text/html', q='0.8')
    accept_xhtml = MediaRange(mimetype='application/xml+xhtml')

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


def test_MediaRange_sort():
    """Assert sorting list of MediaRange objects"""
    accept_html = MediaRange(mimetype='text/html')
    accept_xml = MediaRange(
        mimetype='application/xml', q='0.9'
    )
    accept_text_wildcard = MediaRange(mimetype='text/*', q='0.8')
    accept_wildcard = MediaRange(mimetype='*/*', q='0.8')

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

    # Same with reversed sort
    assert sorted(values, reverse=True) == [
        accept_html,
        accept_xml,
        accept_text_wildcard, accept_wildcard  # Last position
    ]

    # Can not be compared with object without quality
    with raises(TypeError):
        sorted([1, 2, accept_html])


def test_MediaRange_compare():
    """Assert <, <=, > and >= compare only quality, not mimetype"""
    accept_html = MediaRange(mimetype='text/html')
    accept_xml = MediaRange(
        mimetype='application/xml', q='0.9'
    )
    accept_wildcard = MediaRange(
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

    with raises(TypeError):
        accept_xml < 1.0

    with raises(TypeError):
        accept_xml <= 1.0

    with raises(TypeError):
        accept_xml > 1.0

    with raises(TypeError):
        accept_xml >= 1.0


def test_MediaRange_to_http():
    """Assert value.to_http() returns expected string value"""
    accept_html = MediaRange(mimetype='text/html')
    accept_xml = MediaRange(mimetype='application/xml', q='0.9')
    accept_text_level = MediaRange(
        mimetype='text/plain', level='1', version='1.0'
    )

    assert accept_html.to_http() == 'text/html'
    assert accept_html.to_http(explicit_quality=True) == 'text/html;q=1.0'
    assert accept_xml.to_http() == 'application/xml;q=0.9'
    assert accept_text_level.to_http() == 'text/plain;level=1;version=1.0'
    assert accept_text_level.to_http(explicit_quality=True) == 'text/plain;q=1.0;level=1;version=1.0'
