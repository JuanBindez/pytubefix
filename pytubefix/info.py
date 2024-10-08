import sys
from pytubefix import __version__

os = sys.platform
python = sys.version
pytubefix = __version__


def info() -> dict:
    """
    Returns information about the current operating system, Python version, and Pytubefix version.
    
    This function gathers system-related information such as the operating system, Python version, 
    and the version of the Pytubefix library, and returns it in a dictionary format.
    
    This can be useful for debugging or logging purposes, as it allows developers to quickly 
    check the environment in which the code is being executed. It helps ensure that the correct 
    versions of Python and Pytubefix are being used, and can also assist in identifying any 
    compatibility issues between the system and the application.

    Returns:
        dict: A dictionary containing the following keys:
            - 'OS': The name of the operating system platform.
            - 'Python': The version of Python currently running.
            - 'Pytubefix': The version of the Pytubefix library.
    """

    message = {
        'OS': os,
        'Python': python,
        'Pytubefix': pytubefix
    }
    return message
