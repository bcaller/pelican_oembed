# Copyright (c) 2016 Ben Caller
import os
from collections import namedtuple
import markdown
import pytest
import vcr
from mock import mock_open, patch
from pyembed.markdown import PyEmbedMarkdown
from pelican_oembed.cachingmarkdownextension import CachingPyEmbedMarkdownExtension
from pelican_oembed.privacyrenderer import PrivacyRenderer

from sys import version_info
if version_info.major == 2:
    import __builtin__ as builtins  # pylint:disable=import-error
else:
    import builtins  # pylint:disable=import-error

PassThroughTest = namedtuple("PassThroughTest", "url id")
FormatTest = namedtuple("FormatTest", "format output id")
id_extractor = lambda y: [x.id for x in y]


@pytest.fixture
def md_no_config():
    renderer = PrivacyRenderer(dict())
    return markdown.Markdown(extensions=[CachingPyEmbedMarkdownExtension(renderer=renderer)])


@pytest.fixture
def pyembed_md():
    return markdown.Markdown(extensions=[PyEmbedMarkdown()])


@pytest.fixture
def default_expected_html():
    with open('test/expected.html', 'r') as f:
        return f.read()


@pytest.fixture
def url():
    return "https://www.youtube.com/watch?v=jNQXAC9IVRw"


pass_through_tests = [
    PassThroughTest('https://twitter.com/BarackObama/status/266031293945503744', 'rich'),
    PassThroughTest('https://www.flickr.com/photos/bees/2362225867/', 'photo')
]

format_tests = [
    FormatTest('*%(title)s', '*Me at the zoo', 'percent-string'),
    FormatTest(lambda p: '*' + p['title'], '*Me at the zoo', 'function'),
    FormatTest(None, default_expected_html(), 'default')
]


@pytest.fixture(params=pass_through_tests, ids=id_extractor(pass_through_tests))
def pass_through(request):
    return request.param


@pytest.fixture(params=format_tests, ids=id_extractor(format_tests))
def formatter(request):
    return request.param


# Tests


@vcr.use_cassette('test/cassettes/youtube.yml')
def test_video(md_no_config, default_expected_html, url):
    text = '[!embed](%s)' % url
    html = md_no_config.convert(text)

    assert html == '<p>' + default_expected_html + '</p>'


@vcr.use_cassette('test/cassettes/youtube.yml')
def test_format(formatter, url):
    text = '[!embed](%s)' % url
    renderer = PrivacyRenderer({
        'OEMBED_VIDEO_FORMAT': formatter.format
    })

    html = markdown.Markdown(extensions=[CachingPyEmbedMarkdownExtension(renderer=renderer)]).convert(text)

    assert html == '<p>%s</p>' % formatter.output


def test_use_pyembed_if_not_video(md_no_config, pyembed_md, pass_through):
    text = '[!embed](%s)' % pass_through.url
    cassette = 'test/cassettes/%s.yml' % pass_through.id
    with vcr.use_cassette(cassette):
        html_original = pyembed_md.convert(text)
    with vcr.use_cassette(cassette):
        html_this = md_no_config.convert(text)
    assert html_this == html_original


@vcr.use_cassette('CACHE_HIT_NO_REQUESTS', record_mode='none')
def test_cache_hit_no_requests(url, default_expected_html):
    cache = {
        url: {
            "type": "video", "title": "Me at the zoo",
            "width": 459, "height": 344, "thumbnail_width": 480, "thumbnail_height": 360,
            "thumbnail_url": "https://i.ytimg.com/vi/jNQXAC9IVRw/hqdefault.jpg",
            "html": "<iframe width=\"459\" height=\"344\" "
                    "src=\"https://www.youtube.com/embed/jNQXAC9IVRw?feature=oembed\" "
                    "frameborder=\"0\" allowfullscreen></iframe>"
        }
    }
    renderer = PrivacyRenderer({'_OEMBED_CACHE': cache})
    md = markdown.Markdown(extensions=[CachingPyEmbedMarkdownExtension(cache=cache, renderer=renderer)])
    html = md.convert('[!embed](%s)' % url)

    assert len(cache) == 1
    assert html == '<p>%s</p>' % default_expected_html


@vcr.use_cassette('test/cassettes/youtube.yml')
def test_cache_written(url):
    cache = dict()
    renderer = PrivacyRenderer({'_OEMBED_CACHE': cache})
    md = markdown.Markdown(extensions=[CachingPyEmbedMarkdownExtension(cache=cache, renderer=renderer)])
    md.convert('[!embed](%s)' % url)

    assert len(cache) == 1
    assert url in cache


@vcr.use_cassette('test/cassettes/thumbnail.yml', record_mode='none')
def test_thumbnail(url):
    cache = {
        url: {
            "type": "video",
            "thumbnail_url": "https://upload.wikimedia.org/wikipedia/en/4/48/Blank.JPG",
            "html": "<iframe blah></iframe>"
        }
    }
    renderer = PrivacyRenderer({
        'OUTPUT_PATH': 'test',
        '_OEMBED_CACHE': cache,
        'OEMBED_VIDEO_FORMAT': '%(thumbnail_url)s',
        'OEMBED_THUMBNAIL_SAVE_AS': 'x%s',
        'OEMBED_THUMBNAIL_URL': 'url/to/%s'
    })
    md = markdown.Markdown(extensions=[CachingPyEmbedMarkdownExtension(cache=cache, renderer=renderer)])

    with patch.object(builtins, 'open', mock_open()) as m:
        html = md.convert('[!embed](%s)' % list(cache.keys())[0])

    assert html == '<p>url/to/upload_wikimedia_org_wikipedia_en_4_48_Blank.JPG</p>'
    m.assert_called_with(os.path.join('test', 'xupload_wikimedia_org_wikipedia_en_4_48_Blank.JPG'), 'x+b')

# TODO test Pelican integration
