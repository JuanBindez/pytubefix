"""Library specific exception definitions."""
from typing import Pattern, Union
import logging


logger = logging.getLogger(__name__)

class PytubeFixError(Exception):
    """Base pytubefix exception that all others inherit.

    This is done to not pollute the built-in exceptions, which *could* result
    in unintended errors being unexpectedly and incorrectly handled within
    implementers code.
    """
### MISC Errors ###

class MaxRetriesExceeded(PytubeFixError):
    """Maximum number of retries exceeded."""


class HTMLParseError(PytubeFixError):
    """HTML could not be parsed"""


class ExtractError(PytubeFixError):
    """Data extraction based exception."""


class RegexMatchError(ExtractError):
    """Regex pattern did not return any matches."""

    def __init__(self, caller: str, pattern: Union[str, Pattern]):
        """
        :param str caller:
            Calling function
        :param str pattern:
            Pattern that failed to match
        """
        super().__init__(
            f"{caller}: could not find match for {pattern}")


        self.caller = caller
        self.pattern = pattern


### Video Unavailable Errors ###
# There are really 3 types of errors thrown
# 1. VideoUnavailable - This is the base error type for all video errors. 
#   Or a catchall if neither the user or developer cares about the specific error.
# 2. Known Error Type, Extra info useful for user
# 3. Unknown Error Type, Important to Developer

## 1. VideoUnavailable ##

class VideoUnavailable(PytubeFixError):
    """
    Base video error.

    This is the base error type for all video errors.

    Call this if you can't group the error by known error type and it is not important to the developer.
    """

    def __init__(self, video_id: str):
        """
        :param str video_id:
            A YouTube video identifier.
        """
        self.video_id = video_id
        super().__init__(self.error_string)

    @property
    def error_string(self):
        return f'{self.video_id} is unavailable'

## 2. Known Error Type, Extra info useful for user ##

class VideoPrivate(VideoUnavailable):
    def __init__(self, video_id: str):
        """
        :param str video_id:
            A YouTube video identifier.
        """
        self.video_id = video_id
        super().__init__(self.video_id)

    @property
    def error_string(self):
        return f'{self.video_id} is a private video'


class MembersOnly(VideoUnavailable):
    """Video is members-only.

    YouTube has special videos that are only viewable to users who have
    subscribed to a content creator.
    ref: https://support.google.com/youtube/answer/7544492?hl=en
    """

    def __init__(self, video_id: str):
        """
        :param str video_id:
            A YouTube video identifier.
        """
        self.video_id = video_id
        super().__init__(self.video_id)

    @property
    def error_string(self):
        return f'{self.video_id} is a members-only video'


class VideoRegionBlocked(VideoUnavailable):
    def __init__(self, video_id: str):
        """
        :param str video_id:
            A YouTube video identifier.
        """
        self.video_id = video_id
        super().__init__(self.video_id)

    @property
    def error_string(self):
        return f'{self.video_id} is not available in your region'

class BotDetection(VideoUnavailable):
    def __init__(self, video_id: str):
        """
        :param str video_id:
            A YouTube video identifier.
        """
        self.video_id = video_id
        super().__init__(self.video_id)

    @property
    def error_string(self):
        return (
            f'{self.video_id} This request was detected as a bot. Use `use_po_token=True` to view. '
            f'See more details at https://github.com/JuanBindez/pytubefix/pull/209')


class PoTokenRequired(VideoUnavailable):
    def __init__(self, video_id: str, client_name: str):
        """
        :param str video_id:
            A YouTube video identifier.
        :param str client_name:
            A YouTube client identifier.
        """
        self.video_id = video_id
        self.client_name = client_name
        super().__init__(self.video_id)

    @property
    def error_string(self):
        return (
            f'{self.video_id} The {self.client_name} client requires PoToken to obtain functional streams, '
            f'See more details at https://github.com/JuanBindez/pytubefix/pull/209')


class LoginRequired(VideoUnavailable):
    def __init__(self, video_id: str, reason: str):
        """
        :param str video_id:
            A YouTube video identifier.
        """
        self.video_id = video_id
        self.reason = reason
        super().__init__(self.video_id)

    @property
    def error_string(self):
        return (
            f'{self.video_id} requires login to view, YouTube reason: {self.reason}')

# legacy livestream error types still supported

class RecordingUnavailable(VideoUnavailable):
    def __init__(self, video_id: str):
        """
        :param str video_id:
            A YouTube video identifier.
        """
        self.video_id = video_id
        super().__init__(self.video_id)

    @property
    def error_string(self):
        return f'{self.video_id} does not have a live stream recording available'


class LiveStreamError(VideoUnavailable):
    """Video is a live stream."""

    def __init__(self, video_id: str):
        """
        :param str video_id:
            A YouTube video identifier.
        """
        self.video_id = video_id
        super().__init__(self.video_id)

    @property
    def error_string(self):
        return f'{self.video_id} is streaming live and cannot be loaded'


class LiveStreamOffline(VideoUnavailable):
    """The live will start soon"""

    def __init__(self, video_id: str, reason: str):
        """
        :param str video_id:
            A YouTube video identifier.
        :param str reason:
            reason for the error
        """
        self.video_id = video_id
        self.reason = reason
        super().__init__(self.video_id)

    @property
    def error_string(self):
        return f'{self.video_id} {self.reason}'

# legacy age restricted error types still supported

class AgeRestrictedError(VideoUnavailable):
    """Video is age restricted, and cannot be accessed without OAuth."""

    def __init__(self, video_id: str):
        """
        :param str video_id:
            A YouTube video identifier.
        """
        self.video_id = video_id
        super().__init__(self.video_id)
    
    @property
    def error_string(self):
        return f"{self.video_id} is age restricted, and can't be accessed without logging in."


class AgeCheckRequiredError(VideoUnavailable):
    def __init__(self, video_id: str):
        """
        :param str video_id:
            A YouTube video identifier.
        """
        self.video_id = video_id
        super().__init__(self.video_id)

    @property
    def error_string(self):
        return f"{self.video_id} has age restrictions and cannot be accessed without confirmation."


class AgeCheckRequiredAccountError(VideoUnavailable):
    def __init__(self, video_id: str):
        """
        :param str video_id:
            A YouTube video identifier.
        """
        self.video_id = video_id
        super().__init__(self.video_id)

    @property
    def error_string(self):
        return (
            f"{self.video_id} may be inappropriate for "
            f"some users. Sign in to your primary account to confirm your age.")


## 3. Unknown Error Type, Important to Developer ##


class UnknownVideoError(VideoUnavailable):
    """Unknown video error."""

    def __init__(self, video_id: str, status: str = None, reason: str = None, developer_message: str = None):
        """
        :param str video_id:
            A YouTube video identifier.
        :param str status:
            The status code of the response.
        :param str reason:
            The reason for the error.
        :param str developer_message:
            The message from the developer.
        """
        self.video_id = video_id
        self.status = status
        self.reason = reason
        self.developer_message = developer_message

        logger.warning('Unknown Video Error')
        logger.warning(f'Video ID: {self.video_id}')
        logger.warning(f'Status: {self.status}')
        logger.warning(f'Reason: {self.reason}')
        logger.warning(f'Developer Message: {self.developer_message}')
        logger.warning(
            'Please open an issue at '
            'https://github.com/JuanBindez/pytubefix/issues '
            'and provide the above log output.'
        )

        super().__init__(self.video_id)

    @property
    def error_string(self):
        return f'{self.video_id} has an unknown error, check logs for more info [Status: {self.status}] [Reason: {self.reason}]'
