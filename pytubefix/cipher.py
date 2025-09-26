"""
This module contains all the logic needed to find the signature functions.

YouTube's strategy to restrict downloading videos is to send a ciphered version
of the signature to the client, along with the decryption algorithm obfuscated
in JavaScript. For the clients to play the videos, JavaScript must take the
ciphered version, cycle it through a series of "transform functions," and then
signs the media URL with the output.

This module is responsible for (1) finding these "transformations
functions" (2) sends them to be interpreted by nodejs
"""
import logging
import re

from pytubefix.exceptions import RegexMatchError, InterpretationError
from pytubefix.jsinterp import JSInterpreter, extract_player_js_global_var
from pytubefix.sig_nsig.node_runner import NodeRunner

logger = logging.getLogger(__name__)


class Cipher:
    def __init__(self, js: str, js_url: str):

        self.js_url = js_url
        self.js = js

        self._sig_param_val = None
        self._nsig_param_val = None
        self.sig_function_name = self.get_sig_function_name(js, js_url)
        self.nsig_function_name = self.get_nsig_function_name(js, js_url)

        self.runner_sig = NodeRunner(js)
        self.runner_sig.load_function(self.sig_function_name)

        self.runner_nsig = NodeRunner(js)
        self.runner_nsig.load_function(self.nsig_function_name)

        self.calculated_n = None

        self.js_interpreter = JSInterpreter(js)

    def get_nsig(self, n: str):
        """Interpret the function that transforms the signature parameter `n`.
            The lack of this signature generates the 403 forbidden error.
        :param str n:
            Contains the parameter that must be transformed.
        :rtype: str
        :returns:
            Returns the transformed value "n".
        """
        try:
            if self._nsig_param_val:
                for param in self._nsig_param_val:
                    nsig = self.runner_nsig.call([param, n])
                    if not isinstance(nsig, str):
                        continue
                    else:
                        break
            else:
                nsig = self.runner_nsig.call([n])
        except Exception as e:
            raise InterpretationError(js_url=self.js_url, reason=e)

        if 'error' in nsig or '_w8_' in nsig or not isinstance(nsig, str):
            raise InterpretationError(js_url=self.js_url, reason=nsig)
        return nsig

    def get_sig(self, ciphered_signature: str) -> str:
        """interprets the function that signs the streams.
            The lack of this signature generates the 403 forbidden error.
        :param str ciphered_signature:
           Contains the signature that must be transformed.
        :rtype: str
        :returns:
           Returns the correct stream signature.
        """
        try:
            if self._sig_param_val:
                sig = self.runner_sig.call([self._sig_param_val, ciphered_signature])
            else:
                sig = self.runner_sig.call([ciphered_signature])
        except Exception as e:
            raise InterpretationError(js_url=self.js_url, reason=e)

        if 'error' in sig or not isinstance(sig, str):
            raise InterpretationError(js_url=self.js_url, reason=sig)
        return sig


    def get_sig_function_name(self, js: str, js_url: str) -> str:
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
            r'\b(?P<var>[a-zA-Z0-9_$]+)&&\((?P=var)=(?P<sig>[a-zA-Z0-9_$]{2,})\((?:(?P<param>\d+),decodeURIComponent|decodeURIComponent)\((?P=var)\)\)',
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
                if "param" in function_match.groupdict():
                    param = function_match.group('param')
                    if param:
                        self._sig_param_val = int(param)
                return sig

        raise RegexMatchError(
            caller="get_initial_function_name", pattern=f"multiple in {js_url}"
        )

    def get_nsig_function_name(self, js: str, js_url: str):
        """Extract the name of the function that transforms the signature parameter `n`.

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
            pattern = r"var\s*[a-zA-Z0-9$_]{3}\s*=\s*\[(?P<funcname>[a-zA-Z0-9$_]{3})\]"
            func_name = re.search(pattern, js)
            if func_name:
                n_func = func_name.group("funcname")
                logger.debug(f"Nfunc name: {n_func}")
                return n_func
            else:
                # TODO: This should be removed if the previous regex continues to work.

                logger.debug(f'Failed to get Nfunc name. Pattern: {pattern}')
                logger.debug('Extracts the function name based on the global array')
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
                                    \(\s*(?:[a-zA-Z0-9_$]+\s*,\s*)?(?P<argname>[a-zA-Z0-9_$]+)(?:\s*,\s*[a-zA-Z0-9_$]+)*\s*\)\s*\{
                                    (?:(?!(?<!\{)\};(?![\]\)])).)*
                                    \}\s*catch\(\s*[a-zA-Z0-9_$]+\s*\)\s*
                                    \{\s*(?:return\s+|[\w=]+)%s\[%d\]\s*\+\s*(?P=argname)\s*[\};].*?\s*return\s+[^}]+\}[;\n]
                                '''  % (re.escape(varname), k)
                            func_name = re.search(pattern, js)
                            if func_name:
                                n_func = func_name.group("funcname")
                                logger.debug(f"Nfunc name is: {n_func}")
                                self._nsig_param_val = self._extract_nsig_param_val(js, n_func)
                                return n_func

                            raise RegexMatchError(
                                caller="get_throttling_function_name", pattern=f"{pattern} in {js_url}"
                            )
        except Exception as e:
            raise e


    @staticmethod
    def _extract_nsig_param_val(code: str, func_name: str) -> list:
        """Extract the control parameter from the signature function `n`.

        :param str code:
            The contents of the base.js asset file.
        :param str func_name:
            function name
        :rtype: list
        :returns:
            The list with the extracted values.
        """
        logger.debug('Looking for the control parameter')
        # base.js calls the function using the global object,
        # it looks like `rf[Y[6]](this, 1, h)`, `rf` is the function name and `Y[6]` usually contains `.call`,
        # `1` is the control parameter and `h` is the string to be transformed.
        pattern = re.compile(
            rf'(?<![A-Za-z0-9_$\.])' 
            rf'(?P<func>{re.escape(func_name)})\s*'
            r'\[\w\[\d+\]\]'
            r'\(\s*'
            r'(?P<arg1>[A-Za-z0-9_$]+)'
            r'(?:\s*,\s*(?P<arg2>[A-Za-z0-9_$]+))?'
            r'(?:\s*,\s*[^)]*)?'
            r'\s*\)',
            re.MULTILINE
        )

        results = []
        for m in pattern.finditer(code):
            chosen = m.group('arg2') if m.group('arg1') == 'this' and m.group('arg2') else m.group('arg1')
            results.append(chosen)

        logger.debug(f'Parameters found: {results}')
        return results