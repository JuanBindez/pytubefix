import os
import pytest
from unittest import mock
from unittest.mock import MagicMock, mock_open, patch

from pytubefix import Caption, CaptionQuery, captions


def test_float_to_srt_time_format():
    caption1 = Caption(
        {"url": "url1", "name": {"simpleText": "name1"}, "languageCode": "en", "vssId": ".en"}
    )
    assert caption1.float_to_srt_time_format(3.89) == "00:00:03,890"


def test_caption_query_sequence():
    caption1 = Caption(
        {"url": "url1", "name": {"simpleText": "name1"}, "languageCode": "en", "vssId": ".en"}
    )
    caption2 = Caption(
        {"url": "url2", "name": {"simpleText": "name2"}, "languageCode": "fr", "vssId": ".fr"}
    )
    caption_query = CaptionQuery(captions=[caption1, caption2])
    assert len(caption_query) == 2
    assert caption_query["en"] == caption1
    assert caption_query["fr"] == caption2
    with pytest.raises(KeyError):
        assert caption_query["nada"] is not None


def test_caption_query_get_by_language_code_when_exists():
    caption1 = Caption(
        {"url": "url1", "name": {"simpleText": "name1"}, "languageCode": "en", "vssId": ".en"}
    )
    caption2 = Caption(
        {"url": "url2", "name": {"simpleText": "name2"}, "languageCode": "fr", "vssId": ".fr"}
    )
    caption_query = CaptionQuery(captions=[caption1, caption2])
    assert caption_query["en"] == caption1


def test_caption_query_get_by_language_code_when_not_exists():
    caption1 = Caption(
        {"url": "url1", "name": {"simpleText": "name1"}, "languageCode": "en", "vssId": ".en"}
    )
    caption2 = Caption(
        {"url": "url2", "name": {"simpleText": "name2"}, "languageCode": "fr", "vssId": ".fr"}
    )
    caption_query = CaptionQuery(captions=[caption1, caption2])
    with pytest.raises(KeyError):
        assert caption_query["hello"] is not None
        # assert not_found is not None  # should never reach here


@mock.patch("pytubefix.captions.Caption.generate_srt_captions")
def test_download(srt):
    open_mock = mock_open()
    with patch("builtins.open", open_mock):
        srt.return_value = ""
        caption = Caption(
            {
                "url": "url1",
                "name": {"simpleText": "name1"},
                "languageCode": "en",
                "vssId": ".en"
            }
        )
        caption.download("title")
        assert (
            open_mock.call_args_list[0][0][0].split(os.path.sep)[-1] == "title (en).srt"
        )


@mock.patch("pytubefix.captions.Caption.generate_srt_captions")
def test_download_with_prefix(srt):
    open_mock = mock_open()
    with patch("builtins.open", open_mock):
        srt.return_value = ""
        caption = Caption(
            {
                "url": "url1",
                "name": {"simpleText": "name1"},
                "languageCode": "en",
                "vssId": ".en"
            }
        )
        caption.download("title", filename_prefix="1 ")
        assert (
            open_mock.call_args_list[0][0][0].split(os.path.sep)[-1]
            == "1 title (en).srt"
        )


@mock.patch("pytubefix.captions.Caption.generate_srt_captions")
def test_download_with_output_path(srt):
    open_mock = mock_open()
    captions.target_directory = MagicMock(return_value="/target")
    with patch("builtins.open", open_mock):
        srt.return_value = ""
        caption = Caption(
            {
                "url": "url1",
                "name": {"simpleText": "name1"},
                "languageCode": "en",
                "vssId": ".en"
            }
        )
        file_path = caption.download("title", output_path="blah")
        assert file_path == os.path.join("/target","title (en).srt")
        captions.target_directory.assert_called_with("blah")


@mock.patch("pytubefix.captions.Caption.xml_captions")
def test_download_xml_and_trim_extension(xml):
    open_mock = mock_open()
    with patch("builtins.open", open_mock):
        xml.return_value = ""
        caption = Caption(
            {
                "url": "url1",
                "name": {"simpleText": "name1"},
                "languageCode": "en",
                "vssId": ".en"
            }
        )
        caption.download("title.xml", srt=False)
        assert (
            open_mock.call_args_list[0][0][0].split(os.path.sep)[-1] == "title (en).xml"
        )


def test_repr():
    caption = Caption(
        {"url": "url1", "name": {"simpleText": "name1"}, "languageCode": "en", "vssId": ".en"}
    )
    assert str(caption) == '<Caption lang="name1" code="en">'

    caption_query = CaptionQuery(captions=[caption])
    assert repr(caption_query) == '{\'en\': <Caption lang="name1" code="en">}'


@mock.patch("pytubefix.request.get")
def test_xml_captions(request_get):
    request_get.return_value = "test"
    caption = Caption(
        {"url": "url1", "name": {"simpleText": "name1"}, "languageCode": "en", "vssId": ".en"}
    )
    assert caption.xml_captions == "test"


@mock.patch("pytubefix.captions.request")
def test_generate_srt_captions(request):

    clean_text = lambda x: x.replace(' ', '').replace('\n', '')

    xml_data = '''
    <?xml version="1.0" encoding="utf-8" ?>
        <timedtext format="3">
    <body>
    <p t="10200" d="940">K-pop!</p>
    <p t="13400" d="2800">That is so awkward to watch.</p>
    <p t="16200" d="2080">YouTube Rewind 2018.</p>
    <p t="18480" d="3520">The most disliked video
    in the history of YouTube.</p>
    <p t="22780" d="2220">In 2018, we made something
    you didn’t like.</p>
    <p t="25100" d="2470">So in 2019, let’s see what
    you DID like.</p>
    <p t="27580" d="1400">Because you’re better at this
    than we are.</p>
    <p t="45110" d="1310">This is my outfit!</p>
    </body>
</timedtext>
    '''.strip()

    request.get.return_value = xml_data

    caption = Caption(
        {"url": "url1", "name": {"simpleText": "name1"}, "languageCode": "en", "vssId": ".en"}
    )

    expected_output = '''
        1
00:00:10,200 --> 00:00:11,140
K-pop!
2
00:00:13,400 --> 00:00:16,200
That is so awkward to watch.
3
00:00:16,200 --> 00:00:18,280
YouTube Rewind 2018.
4
00:00:18,480 --> 00:00:22,000
The most disliked video
    in the history of YouTube.
5
00:00:22,780 --> 00:00:25,000
In 2018, we made something
    you didn’t like.
6
00:00:25,100 --> 00:00:27,570
So in 2019, let’s see what
    you DID like.
7
00:00:27,580 --> 00:00:28,980
Because you’re better at this
    than we are.
8
00:00:45,110 --> 00:00:46,420
This is my outfit!
'''

    assert clean_text(caption.generate_srt_captions()) == clean_text(expected_output)
