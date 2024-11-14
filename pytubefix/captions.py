import math
import os
import time
import json

from xml.etree import ElementTree
from html import unescape
from typing import Dict, Optional

from pytubefix import request
from pytubefix.helpers import safe_filename, target_directory


class Caption:
    """Container for caption tracks."""

    def __init__(self, caption_track: Dict):
        """Construct a :class:`Caption <Caption>`.

        :param dict caption_track:
            Caption track data extracted from ``watch_html``.
        """
        self.url = caption_track.get("baseUrl")

        # Certain videos have runs instead of simpleText
        #  this handles that edge case
        name_dict = caption_track['name']
        if 'simpleText' in name_dict:
            self.name = name_dict['simpleText']
        else:
            for el in name_dict['runs']:
                if 'text' in el:
                    self.name = el['text']

        # Use "vssId" instead of "languageCode", fix issue #779
        self.code = caption_track["vssId"]
        # Remove preceding '.' for backwards compatibility, e.g.:
        # English -> vssId: .en, languageCode: en
        # English (auto-generated) -> vssId: a.en, languageCode: en
        self.code = self.code.strip('.')

    @property
    def xml_captions(self) -> str:
        """Download the xml caption tracks."""
        return request.get(self.url)

    @property
    def json_captions(self) -> dict:
        """Download and parse the json caption tracks."""
        if 'ftm=' in self.url:
            json_captions_url = self.url.replace('fmt=srv3', 'fmt=json3')
        else:
            json_captions_url = f'{self.url}&fmt=json3'
        text = request.get(json_captions_url)
        parsed = json.loads(text)
        assert parsed['wireMagic'] == 'pb3', 'Unexpected captions format'
        return parsed

    def generate_srt_captions(self) -> str:
        """Generate "SubRip Subtitle" captions.

        Takes the xml captions from :meth:`~pytube.Caption.xml_captions` and
        recompiles them into the "SubRip Subtitle" format.
        """
        return self.xml_caption_to_srt(self.xml_captions)

    def save_captions(self, filename: str):
        """Generate and save "SubRip Subtitle" captions to a text file.

        Takes the xml captions from :meth:`~pytubefix.Caption.xml_captions` and
        recompiles them into the "SubRip Subtitle" format and saves it to a text file.

        :param filename: The name of the file to save the captions.
        """
        srt_captions = self.xml_caption_to_srt(self.xml_captions)

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(srt_captions)

    @staticmethod
    def float_to_srt_time_format(d: float) -> str:
        """Convert decimal durations into proper srt format.

        :rtype: str
        :returns:
            SubRip Subtitle (str) formatted time duration.

        float_to_srt_time_format(3.89) -> '00:00:03,890'
        """
        fraction, whole = math.modf(d)
        time_fmt = time.strftime("%H:%M:%S,", time.gmtime(whole))
        ms = f"{fraction:.3f}".replace("0.", "")
        return time_fmt + ms

    def xml_caption_to_srt(self, xml_captions: str) -> str:
        """Convert xml caption tracks to "SubRip Subtitle (srt)".

        :param str xml_captions:
            XML formatted caption tracks.
        """
        segments = []
        root = ElementTree.fromstring(xml_captions)

        i = 0
        for child in list(root.iter(root.tag))[0]:
            if child.tag in ['p', 'text']:
                caption = ''

                # I think it will be faster than `len(list(child)) == 0`
                if not list(child):
                    # instead of 'continue'
                    caption = child.text
                for s in list(child):
                    if s.tag == 's':
                        caption += f' {s.text}'
                if not caption:
                    continue
                caption = unescape(caption.replace(
                    "\n", " ").replace("  ", " "),)
                try:
                    if "d" in child.attrib:
                        duration = float(child.attrib["d"]) / 1000.0
                    else:
                        duration = float(child.attrib["dur"])
                except KeyError:
                    duration = 0.0

                if "t" in child.attrib:
                    start = float(child.attrib["t"]) / 1000.0
                else:
                    start = float(child.attrib["start"])

                end = start + duration
                sequence_number = i + 1  # convert from 0-indexed to 1.
                line = "{seq}\n{start} --> {end}\n{text}\n".format(
                    seq=sequence_number,
                    start=self.float_to_srt_time_format(start),
                    end=self.float_to_srt_time_format(end),
                    text=caption,
                )
                segments.append(line)
                i += 1
        return "\n".join(segments).strip()

    def download(
        self,
        title: str,
        srt: bool = True,
        output_path: Optional[str] = None,
        filename_prefix: Optional[str] = None,
    ) -> str:
        """Write the media stream to disk.

        :param title:
            Output filename (stem only) for writing media file.
            If one is not specified, the default filename is used.
        :type title: str
        :param srt:
            Set to True to download srt, false to download xml. Defaults to True.
        :type srt bool
        :param output_path:
            (optional) Output path for writing media file. If one is not
            specified, defaults to the current working directory.
        :type output_path: str or None
        :param filename_prefix:
            (optional) A string that will be prepended to the filename.
            For example a number in a playlist or the name of a series.
            If one is not specified, nothing will be prepended
            This is separate from filename so you can use the default
            filename but still add a prefix.
        :type filename_prefix: str or None

        :rtype: str
        """
        if title.endswith(".srt") or title.endswith(".xml"):
            filename = ".".join(title.split(".")[:-1])
        else:
            filename = title

        if filename_prefix:
            filename = f"{safe_filename(filename_prefix)}{filename}"

        filename = safe_filename(filename)

        filename += f" ({self.code})"
        filename += ".srt" if srt else ".xml"

        file_path = os.path.join(target_directory(output_path), filename)

        with open(file_path, "w", encoding="utf-8") as file_handle:
            if srt:
                file_handle.write(self.generate_srt_captions())
            else:
                file_handle.write(self.xml_captions)

        return file_path

    def __repr__(self):
        """Printable object representation."""
        return '<Caption lang="{s.name}" code="{s.code}">'.format(s=self)
