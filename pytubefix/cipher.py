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
import json
import logging
import re
import time

from pytubefix.exceptions import RegexMatchError, InterpretationError
from pytubefix.jsinterp import JSInterpreter, extract_player_js_global_var
from pytubefix.sig_nsig.node_runner import NodeRunner

MAX_RETRIES = 3
RETRY_DELAY = 0.5

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

    @staticmethod
    def _is_empty_response_error(exc: Exception) -> bool:
        """Check if the exception is caused by an empty Node.js response."""
        return isinstance(exc, json.JSONDecodeError) or (
            isinstance(exc, Exception)
            and "Expecting value" in str(exc)
            and "char 0" in str(exc)
        )

    def _call_with_retry(self, runner, args, label="call"):
        """Call NodeRunner with retry logic for empty response errors."""
        last_exc = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return runner.call(args)
            except Exception as e:
                if self._is_empty_response_error(e) and attempt < MAX_RETRIES:
                    logger.warning(
                        f"{label}: empty response on attempt {attempt}/{MAX_RETRIES}, "
                        f"retrying in {RETRY_DELAY}s..."
                    )
                    last_exc = e
                    time.sleep(RETRY_DELAY * attempt)
                    # Reinitialize the runner in case the Node.js process died
                    try:
                        runner.load_function(
                            self.nsig_function_name if "nsig" in label
                            else self.sig_function_name
                        )
                    except Exception:
                        pass
                    continue
                raise
        raise last_exc

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
                nsig = None
                for param in self._nsig_param_val:
                    if isinstance(param, list):
                        nsig = self._call_with_retry(
                            self.runner_nsig, [*param, n], label="nsig"
                        )
                    else:
                        nsig = self._call_with_retry(
                            self.runner_nsig, [param, n], label="nsig"
                        )
                    if isinstance(nsig, str) and 'error' not in nsig and '_w8_' not in nsig:
                        break
            else:
                nsig = self._call_with_retry(
                    self.runner_nsig, [n], label="nsig"
                )
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
                if isinstance(self._sig_param_val, list):
                    sig = self._call_with_retry(
                        self.runner_sig, [*self._sig_param_val, ciphered_signature],
                        label="sig"
                    )
                else:
                    sig = self._call_with_retry(
                        self.runner_sig, [self._sig_param_val, ciphered_signature],
                        label="sig"
                    )
            else:
                sig = self._call_with_retry(
                    self.runner_sig, [ciphered_signature], label="sig"
                )
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
            # New obfuscated patterns (2025+)
            # YouTube uses: sigFunc(num1,num2, wrapperFunc(..., N.s))
            #   TCE player:    BR(32,868,decodeURIComponent(e.s))
            #   Regular player: M_(15,7873,Zk(90,2163,N.s))
            r'(?P<sig>[a-zA-Z0-9$_]+)\((?P<param>\d+),(?P<param2>\d+),(?:[a-zA-Z0-9$_]+\(\d+,\d+,|decodeURIComponent\()[a-zA-Z0-9$_.]+\.s\)\)',
            r'(?P<sig>[a-zA-Z0-9$_]+)\((?P<param>\d+),(?P<param2>\d+),(?:[a-zA-Z0-9$_]+\(\d+,\d+,|decodeURIComponent\()[a-zA-Z0-9$_]+\)\),[a-zA-Z0-9$_]+\[',
            # Classic patterns
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
                groups = function_match.groupdict()
                if "param2" in groups and groups.get("param2"):
                    self._sig_param_val = [int(groups['param']), int(groups['param2'])]
                elif "param" in groups and groups.get("param"):
                    self._sig_param_val = int(groups['param'])
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
            # Strategy 1 (most reliable): Find _w8_ in global array, locate function
            global_obj, varname, code = extract_player_js_global_var(js)
            if global_obj and varname and code:
                logger.debug(f"Global Obj name is: {varname}")
                global_obj = JSInterpreter(js).interpret_expression(code, {}, 100)
                logger.debug("Successfully interpreted global object")
                for k, val in enumerate(global_obj):
                    if val.endswith('_w8_'):
                        logger.debug(f"_w8_ found in index {k}")
                        nsig_patterns = [
                            r'''(?xs)
                                [;\n](?:
                                    (?P<f>function\s+)|
                                    (?:var\s+)?
                                )(?P<funcname>[a-zA-Z0-9_$]+)\s*(?(f)|=\s*function\s*)
                                \(\s*(?:[a-zA-Z0-9_$]+\s*,\s*)?(?P<argname>[a-zA-Z0-9_$]+)(?:\s*,\s*[a-zA-Z0-9_$]+)*\s*\)\s*\{
                                (?:(?!(?<!\{)\};(?![\]\)])).)*
                                \}\s*catch\(\s*[a-zA-Z0-9_$]+\s*\)\s*
                                \{\s*(?:return\s+|[\w=]+)%s\[%d\]\s*\+\s*(?P=argname)\s*[\};].*?\s*return\s+[^}]+\}[;\n]
                            '''  % (re.escape(varname), k),
                            # Relaxed: function referencing varname[k]
                            r'''(?xs)
                                [;\n](?:
                                    (?P<f>function\s+)|
                                    (?:var\s+)?
                                )(?P<funcname>[a-zA-Z0-9_$]+)\s*(?(f)|=\s*function\s*)
                                \([^)]*\)\s*\{
                                (?:(?!(?<!\{)\};).)*?
                                %s\[%d\]
                                (?:(?!(?<!\{)\};).)*?
                                \}[;\n]
                            ''' % (re.escape(varname), k),
                        ]
                        for np_ in nsig_patterns:
                            func_name = re.search(np_, js)
                            if func_name:
                                n_func = func_name.group("funcname")
                                logger.debug(f"Nfunc name (strategy 1 - _w8_): {n_func}")
                                self._nsig_param_val = self._extract_nsig_param_val(js, n_func)
                                return n_func

            # Strategy 2: var XX = [YY] with 2-3 char names (fast, common)
            pattern = r"var\s*[a-zA-Z0-9$_]{2,3}\s*=\s*\[(?P<funcname>[a-zA-Z0-9$_]{2,})\]"
            func_name = re.search(pattern, js)
            if func_name:
                n_func = func_name.group("funcname")
                logger.debug(f"Nfunc name (strategy 2): {n_func}")
                return n_func

            # Strategy 2.5: Multi-branch XOR nsig function (2025+ obfuscation)
            # YouTube now embeds the nsig transformation inside a multi-purpose
            # function that uses XOR-controlled branching:
            #   SX=function(r,p,I,S){var a=p^r; ... SX(a^CONST1,a^CONST2,I) ...}
            # The function calls itself recursively with XOR'd constants to reach
            # the nsig transformation branch.
            logger.debug('Trying multi-branch XOR nsig detection (strategy 2.5)')
            xor_func_pattern = re.compile(
                r'([a-zA-Z0-9_$]+)\s*=\s*function\s*\(r\s*,\s*p\s*,\s*I(?:\s*,\s*S)?\)\s*\{'
                r'var\s+a\s*=\s*p\s*\^\s*r\b'
            )
            for xfm in xor_func_pattern.finditer(js):
                candidate = xfm.group(1)
                func_start = xfm.start()
                # Check for self-recursive call with XOR'd constants
                chunk = js[func_start:func_start + 500]
                recursive = re.search(
                    rf'{re.escape(candidate)}\(a\^(\d+)\s*,\s*a\^(\d+)\s*,',
                    chunk
                )
                if not recursive:
                    continue

                # Get the full function body to validate nsig characteristics
                depth = 0
                func_end = func_start
                for i in range(func_start, min(func_start + 50000, len(js))):
                    if js[i] == '{':
                        depth += 1
                    elif js[i] == '}':
                        depth -= 1
                        if depth == 0:
                            func_end = i + 1
                            break
                func_body = js[func_start:func_end]

                # Validate nsig characteristics: must have try/catch AND null
                # (the big transformation array) AND substantial v[a^ references
                has_try = 'try{' in func_body or 'try {' in func_body
                has_null = func_body.count('null') >= 2
                va_refs = len(re.findall(r'v\[a\^', func_body))

                if has_try and has_null and va_refs > 20:
                    c1 = int(recursive.group(1))
                    c2 = int(recursive.group(2))
                    a_val = c1 ^ c2

                    # Generate control parameter pairs (r, p) that route to the
                    # nsig transformation branch. Try several r values where
                    # common branch conditions like (r>>1&6)>=5 are satisfied.
                    self._nsig_param_val = []
                    for r_val in [13, 14, 15, 12, 29, 30, 31, 28]:
                        self._nsig_param_val.append([r_val, a_val ^ r_val])

                    logger.debug(
                        f"Nfunc name (strategy 2.5 - XOR multi-branch): {candidate}, "
                        f"constants={c1},{c2}, a={a_val}"
                    )
                    return candidate

            # Strategy 3: Broader var=[func], validate it's nsig (has try/catch)
            logger.debug('Trying broader patterns with nsig validation')
            for match in re.finditer(r"var\s*[a-zA-Z0-9$_]+\s*=\s*\[(?P<funcname>[a-zA-Z0-9$_]+)\]", js):
                candidate = match.group("funcname")
                func_def = re.search(
                    r'(?:function\s+%s|(?:var\s+)?%s\s*=\s*function)\s*\(' % (
                        re.escape(candidate), re.escape(candidate)), js)
                if not func_def:
                    continue
                func_start = func_def.start()

                # Properly scope the try/catch check to the actual function body
                # by counting braces, instead of blindly scanning 2000 chars ahead
                depth = 0
                func_end = func_start
                for i in range(func_start, min(func_start + 10000, len(js))):
                    if js[i] == '{':
                        depth += 1
                    elif js[i] == '}':
                        depth -= 1
                        if depth == 0:
                            func_end = i + 1
                            break
                func_body = js[func_start:func_end]

                # Require minimum function body size (nsig functions are large)
                if len(func_body) < 200:
                    continue

                if 'try{' in func_body or 'try {' in func_body or 'catch(' in func_body:
                    logger.debug(f"Nfunc name (strategy 3): {candidate}")
                    self._nsig_param_val = self._extract_nsig_param_val(js, candidate)
                    return candidate

            raise RegexMatchError(
                caller="get_throttling_function_name", pattern=f"multiple in {js_url}"
            )
        except RegexMatchError:
            raise
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
