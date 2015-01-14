import urllib

from six.moves.urllib.parse import (ParseResult, urlunparse,
                                    urlparse, parse_qsl)

from w3lib.url import safe_url_string


def unicode_to_str(text, encoding=None, errors='strict'):
    """Return the str representation of text in the given encoding. Unlike
    .encode(encoding) this function can be applied directly to a str
    object without the risk of double-decoding problems (which can happen if
    you don't use the default 'ascii' encoding)
    """

    if encoding is None:
        encoding = 'utf-8'
    if isinstance(text, unicode):
        return text.encode(encoding, errors)
    elif isinstance(text, str):
        return text
    else:
        raise TypeError('unicode_to_str must receive a unicode or str object, got %s' % type(text).__name__)


def parse_url(url, encoding=None):
    """Return urlparsed url from the given argument (which could be an already
    parsed url)
    """
    if isinstance(url, ParseResult):
        return url

    return urlparse(unicode_to_str(url, encoding))


def _unquotepath(path):
    for reserved in ('2f', '2F', '3f', '3F'):
        path = path.replace('%' + reserved, '%25' + reserved.upper())
    return urllib.unquote(path)


query_param_black_list = [
    'utm_source',
    'utm_medium',
    'utm_term',
    'utm_content',
    'utm_campaign',
    '_r',  # NY times
    'referrer',  # referrer
    'emc',  # NY times
    'partner',  # NY times
    'mbid',
    'ncid',  # Techcrunch
    'hn',  # http://www.wired.com/2014/04/no-exit/?hn=
    'ref',  # http://axioms.io/zen/2014-09-03-making-a-big-difference/?ref=hn
    'smid',  # http://www.nytimes.com/2014/11/04/science/a-tiny-stumble-a-life-upended.html?smid=tw-share
]


def canonicalize_url(url, keep_blank_values=True, keep_fragments=False,
                     encoding=None):
    """Canonicalize the given url by applying the following procedures:
    - sort query arguments, first by key, then by value
    - percent encode paths and query arguments. non-ASCII characters are
      percent-encoded using UTF-8 (RFC-3986)
    - normalize all spaces (in query arguments) '+' (plus symbol)
    - normalize percent encodings case (%2f -> %2F)
    - remove query arguments with blank values (unless keep_blank_values is True)
    - remove fragments (unless keep_fragments is True)
    The url passed can be a str or unicode, while the url returned is always a
    str.
    For examples see the tests in tests/test_utils_url.py
    """

    scheme, netloc, path, params, query, fragment = parse_url(url)
    keyvals = parse_qsl(query, keep_blank_values)
    keyvals = filter(lambda x: x[0] not in query_param_black_list, keyvals)
    keyvals.sort()
    query = urllib.urlencode(keyvals)
    path = safe_url_string(_unquotepath(path)) or '/'
    fragment = '' if not keep_fragments else fragment
    return urlunparse((scheme, netloc.lower(), path, params, query, fragment))
