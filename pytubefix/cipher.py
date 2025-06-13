"""
This module contains all the logic needed to find the signature functions.

YouTube's strategy to restrict downloading videos is to send a ciphered version
of the signature to the client, along with the decryption algorithm obfuscated
in JavaScript. For the clients to play the videos, JavaScript must take the
ciphered version, cycle it through a series of "transform functions," and then
signs the media URL with the output.

This module is responsible for (1) finding these "transformations
functions" (2) sends them to be interpreted by jsinterp.py
"""
import logging
import re

from pytubefix.exceptions import RegexMatchError, InterpretationError
from pytubefix.jsinterp import JSInterpreter, extract_player_js_global_var

logger = logging.getLogger(__name__)


class Cipher:
    def __init__(self, js: str, js_url: str):

        self.js_url = js_url

        self.signature_function_name = get_initial_function_name(js, js_url)
        self.throttling_function_name = get_throttling_function_name(js, js_url)

        self.calculated_n = None

        self.js_interpreter = JSInterpreter(js)

    def get_throttling(self, n: str):
        """Interpret the function that throttles download speed.
        :param str n:
            Contains the parameter that must be transformed.
        :rtype: str
        :returns:
            Returns the transformed value "n".
        """
        try:
            return self.js_interpreter.call_function(self.throttling_function_name, n)
        except:
            raise InterpretationError(js_url=self.js_url)

    def get_signature(self, ciphered_signature: str) -> str:
        """interprets the function that signs the streams.
            The lack of this signature generates the 403 forbidden error.
        :param str ciphered_signature:
           Contains the signature that must be transformed.
        :rtype: str
        :returns:
           Returns the correct stream signature.
        """
        try:
            return self.js_interpreter.call_function(self.signature_function_name, ciphered_signature)
        except:
            raise InterpretationError(js_url=self.js_url)


def get_initial_function_name(js: str, js_url: str) -> str:
    """Extract the name of the function responsible for computing the signature.
    :param str js:
        The contents of the base.js asset file.
    :param str js_url:
        Full base.js url
    :rtype: str
    :returns:
        Function name from regex match
    """

    function_patterns = [
        r'(?P<sig>[a-zA-Z0-9_$]+)\s*=\s*function\(\s*(?P<arg>[a-zA-Z0-9_$]+)\s*\)\s*{\s*(?P=arg)\s*=\s*(?P=arg)\.split\(\s*[a-zA-Z0-9_\$\"\[\]]+\s*\)\s*;\s*[^}]+;\s*return\s+(?P=arg)\.join\(\s*[a-zA-Z0-9_\$\"\[\]]+\s*\)',
        r'(?:\b|[^a-zA-Z0-9_$])(?P<sig>[a-zA-Z0-9_$]{2,})\s*=\s*function\(\s*a\s*\)\s*{\s*a\s*=\s*a\.split\(\s*""\s*\)(?:;[a-zA-Z0-9_$]{2}\.[a-zA-Z0-9_$]{2}\(a,\d+\))?',
        r'\b(?P<var>[a-zA-Z0-9_$]+)&&\((?P=var)=(?P<sig>[a-zA-Z0-9_$]{2,})\(decodeURIComponent\((?P=var)\)\)',
        # Old patterns
        r'\b[cs]\s*&&\s*[adf]\.set\([^,]+\s*,\s*encodeURIComponent\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\(',
        r'\b[a-zA-Z0-9]+\s*&&\s*[a-zA-Z0-9]+\.set\([^,]+\s*,\s*encodeURIComponent\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\(',
        r'\bm=(?P<sig>[a-zA-Z0-9$]{2,})\(decodeURIComponent\(h\.s\)\)',
        # Obsolete patterns
        r'("|\')signature\1\s*,\s*(?P<sig>[a-zA-Z0-9$]+)\(',
        r'\.sig\|\|(?P<sig>[a-zA-Z0-9$]+)\(',
        r'yt\.akamaized\.net/\)\s*\|\|\s*.*?\s*[cs]\s*&&\s*[adf]\.set\([^,]+\s*,\s*(?:encodeURIComponent\s*\()?\s*(?P<sig>[a-zA-Z0-9$]+)\(',
        r'\b[cs]\s*&&\s*[adf]\.set\([^,]+\s*,\s*(?P<sig>[a-zA-Z0-9$]+)\(',
        r'\bc\s*&&\s*[a-zA-Z0-9]+\.set\([^,]+\s*,\s*\([^)]*\)\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\('
    ]
    logger.debug("looking for signature cipher name")
    for pattern in function_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(js)
        if function_match:
            sig = function_match.group('sig')
            logger.debug("finished regex search, matched: %s", pattern)
            logger.debug(f'Signature cipher function name: {sig}')
            return sig

    raise RegexMatchError(
        caller="get_initial_function_name", pattern=f"multiple in {js_url}"
    )


def get_throttling_function_name(js: str, js_url: str) -> str:
    """Extract the name of the function that computes the throttling parameter.

    :param str js:
        The contents of the base.js asset file.
    :param str js_url:
        Full base.js url
    :rtype: str
    :returns:
        The name of the function used to compute the throttling parameter.
    """

    logger.debug("looking for nsig name")
    try:
        # Extracts the function name based on the global array
        global_obj, varname, code = extract_player_js_global_var(js)
        if global_obj and varname and code:
            logger.debug(f"Global Obj name is: {varname}")
            global_obj = JSInterpreter(js).interpret_expression(code, {}, 100)
            logger.debug("Successfully interpreted global object")
            for k, v in enumerate(global_obj):
                if v.endswith('_w8_'):
                    logger.debug(f"_w8_ found in index {k}")
                    pattern = r'''(?xs)
                            [;\n](?:
                                (?P<f>function\s+)|
                                (?:var\s+)?
                            )(?P<funcname>[a-zA-Z0-9_$]+)\s*(?(f)|=\s*function\s*)
                            \((?P<argname>[a-zA-Z0-9_$]+)\)\s*\{
                            (?:(?!\};(?![\]\)])).)+
                            \}\s*catch\(\s*[a-zA-Z0-9_$]+\s*\)\s*
                            \{\s*return\s+%s\[%d\]\s*\+\s*(?P=argname)\s*\}\s*return\s+[^}]+\}[;\n]
                        '''  % (re.escape(varname), k)
                    func_name = re.search(pattern, js)
                    if func_name:
                        n_func = func_name.group("funcname")
                        logger.debug(f"Nfunc name is: {n_func}")
                        return n_func
    except:
        pass

    pattern = r'''(?x)
            (?:
                \.get\("n"\)\)&&\(b=|
                (?:
                    b=String\.fromCharCode\(110\)|
                    (?P<str_idx>[a-zA-Z0-9_$.]+)&&\(b="nn"\[\+(?P=str_idx)\]
                )
                (?:
                    ,[a-zA-Z0-9_$]+\(a\))?,c=a\.
                    (?:
                        get\(b\)|
                        [a-zA-Z0-9_$]+\[b\]\|\|null
                    )\)&&\(c=|
                \b(?P<var>[a-zA-Z0-9_$]+)=
            )(?P<nfunc>[a-zA-Z0-9_$]+)(?:\[(?P<idx>\d+)\])?\([a-zA-Z]\)
            (?(var),[a-zA-Z0-9_$]+\.set\((?:"n+"|[a-zA-Z0-9_$]+)\,(?P=var)\))'''

    logger.debug('Finding throttling function name')

    regex = re.compile(pattern)
    function_match = regex.search(js)
    if function_match:
        logger.debug("finished regex search, matched: %s", pattern)

        func = function_match.group('nfunc')
        idx = function_match.group('idx')

        logger.debug(f'func is: {func}')
        logger.debug(f'idx is: {idx}')

        logger.debug('Checking throttling function name')
        if idx:
            n_func_check_pattern = fr'var {re.escape(func)}\s*=\s*\[(.+?)];'
            n_func_found = re.search(n_func_check_pattern, js)

            if n_func_found:
                throttling_function = n_func_found.group(1)
                logger.debug(f'Throttling function name is: {throttling_function}')
                return throttling_function

            raise RegexMatchError(
                caller="get_throttling_function_name", pattern=f"{n_func_check_pattern} in {js_url}"
            )

    raise RegexMatchError(
        caller="get_throttling_function_name", pattern=f"{pattern} in {js_url}"
    )
