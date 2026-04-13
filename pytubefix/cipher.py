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
import time
from typing import Optional

from pytubefix.exceptions import RegexMatchError, InterpretationError
from pytubefix.jsinterp import JSInterpreter, extract_player_js_global_var
from pytubefix.sig_nsig.node_runner import (
    NodeRunner,
    NodeRunnerEmptyResponseError,
)

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
        """Check if the exception is caused by a retryable Node.js transport miss."""
        return isinstance(exc, NodeRunnerEmptyResponseError)

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
                    try:
                        runner.restart()
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
        nsig = None
        last_exc = None
        try:
            if self._nsig_param_val:
                for param in self._nsig_param_val:
                    try:
                        if isinstance(param, list):
                            nsig = self._call_with_retry(
                                self.runner_nsig, [*param, n], label="nsig"
                            )
                        else:
                            nsig = self._call_with_retry(
                                self.runner_nsig, [param, n], label="nsig"
                            )
                    except Exception as e:
                        last_exc = e
                        logger.debug("nsig candidate %s failed", param, exc_info=True)
                        continue
                    if isinstance(nsig, str) and 'error' not in nsig and '_w8_' not in nsig:
                        # Cache the first working control pair for this player so
                        # later nsig calls do not keep probing dead branches.
                        if isinstance(self._nsig_param_val, list) and self._nsig_param_val:
                            self._nsig_param_val = [param] if isinstance(param, list) else param
                        break
            else:
                nsig = self._call_with_retry(
                    self.runner_nsig, [n], label="nsig"
                )
        except Exception as e:
            raise InterpretationError(js_url=self.js_url, reason=e)

        if 'error' in nsig or '_w8_' in nsig or not isinstance(nsig, str):
            raise InterpretationError(
                js_url=self.js_url,
                reason=last_exc if last_exc is not None else nsig
            )
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
            # Temp-variable chain (player f4d92f0b / 2026-03-31)
            #   var e=jp(55,325,is(26,8416,F.s)); set(...,KH(30,486,e))
            # The middle function (jp) performs the signature transform; the
            # inner call only decodes F.s and the outer call re-encodes it.
            r'(?P<tmp>[a-zA-Z0-9$_]+)\s*=\s*(?P<sig>[a-zA-Z0-9$_]+)\((?P<param>\d+),(?P<param2>\d+),(?:[a-zA-Z0-9$_]+\(\d+,\d+,)*(?:decodeURIComponent\()?[a-zA-Z0-9$_.]+\.s\)+\s*;[^;]{0,160}\b[a-zA-Z0-9$_]+\(\d+,\d+,(?P=tmp)\)',
            # New obfuscated patterns (2026+)
            # YouTube uses nested XOR-controlled multi-branch signature functions:
            #   Player 4f48ea67: aM(12,2643,b4(8,4750,J.s))
            # We need to extract the INNER function (b4), not the outer wrapper (aM)
            # Pattern: outerFunc(p1,p2,INNER(p3,p4,J.s))
            r'[a-zA-Z0-9$_]+\(\d+,\d+,(?P<sig>[a-zA-Z0-9$_]+)\((?P<param>\d+),(?P<param2>\d+),[a-zA-Z0-9$_.]+\.s\)\)',
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

                w8_idx = None
                for k, val in enumerate(global_obj):
                    if val.endswith('_w8_'):
                        w8_idx = k
                        logger.debug(f"_w8_ found in index {k}")
                        break

                if w8_idx is not None:
                    # Strategy 1a: Find via catch block with XOR reference
                    # Pattern: catch(x) { VAR = GLOBAL[xor_var ^ CONST] + arg; break a }
                    xor_catch = re.compile(
                        r'catch\s*\([^)]+\)\s*\{\s*'
                        r'[A-Za-z0-9_$]+\s*=\s*'
                        + re.escape(varname) +
                        r'\[([A-Za-z0-9_$]+)\^(\d+)\]\s*\+\s*([A-Za-z0-9_$]+)\s*;\s*break\s+a\s*\}'
                    )
                    for cm in xor_catch.finditer(js):
                        xor_var = cm.group(1)
                        w8_const = int(cm.group(2))
                        arg_var = cm.group(3)

                        # Find enclosing function
                        search_start = max(0, cm.start() - 5000)
                        func_area = js[search_start:cm.start()]
                        fms = list(re.finditer(
                            r'(?:([a-zA-Z0-9_$]+)\s*=\s*function|function\s+([a-zA-Z0-9_$]+))\s*\(([^)]*)\)',
                            func_area
                        ))
                        if not fms:
                            continue

                        last = fms[-1]
                        n_func = last.group(1) or last.group(2)
                        actual_start = search_start + last.start()

                        # Verify: function must have var xor_var = param ^ param
                        # Use a small window after function header (the XOR init is near the top)
                        header_area = js[actual_start:actual_start + 200]
                        if not re.search(r'var\s+' + re.escape(xor_var) + r'\s*=\s*[A-Za-z0-9_$]+\s*\^\s*[A-Za-z0-9_$]+', header_area):
                            continue

                        # For mega-functions (>50KB), use a window around the catch block
                        # (the nsig branch) instead of the full function body.
                        # The nsig branch is near the catch, but some players also
                        # place follow-up helper branches several hundred chars after it.
                        branch_start = max(actual_start, cm.start() - 2000)
                        branch_end = min(len(js), cm.end() + 1200)
                        # Avoid duplicating the header when the function is small
                        # (branch_start <= actual_start + 200)
                        if branch_start <= actual_start + 200:
                            body = js[actual_start:branch_end]
                        else:
                            body = js[actual_start:actual_start + 200] + js[branch_start:branch_end]

                        logger.debug(f"Nfunc name (strategy 1a - _w8_ XOR catch): {n_func}")
                        w8_xor_b = w8_const ^ w8_idx
                        xor_params = self._extract_xor_branch_nsig_params(
                            js, n_func, varname, global_obj, body, xor_var, arg_var,
                            w8_xor_b=w8_xor_b
                        )
                        if xor_params is not None:
                            logger.debug(f"Using XOR-branch params for {n_func}: {xor_params}")
                            self._nsig_param_val = xor_params
                        else:
                            self._nsig_param_val = self._extract_nsig_param_val(js, n_func)
                        return n_func

                    # Strategy 1b: Find via catch block with direct index reference
                    # Pattern: catch(x) { VAR = GLOBAL[index] + argname; break a }
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
                        '''  % (re.escape(varname), w8_idx),
                        # Relaxed: function referencing varname[w8_idx]
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
                        ''' % (re.escape(varname), w8_idx),
                    ]
                    for np_ in nsig_patterns:
                        func_name = re.search(np_, js)
                        if func_name:
                            n_func = func_name.group("funcname")
                            logger.debug(f"Nfunc name (strategy 1b - _w8_ direct): {n_func}")
                            xor_params = self._extract_xor_branch_nsig_params(
                                js, n_func, varname, global_obj
                            )
                            if xor_params is not None:
                                logger.debug(f"Using XOR-branch params for {n_func}: {xor_params}")
                                self._nsig_param_val = xor_params
                            else:
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
            # function that uses XOR-controlled branching. There are two variants:
            #   Variant A (3-4 params): SX=function(r,p,I,S){var a=p^r; ... SX(a^C1,a^C2,I) ...}
            #   Variant B (many params): Kv=function(n,d,r,H,D,...){var h=d^n; ... Kv(D^C1,D^C2,r) ...}
            # The function may call itself recursively with XOR'd constants to reach
            # the nsig transformation branch.
            logger.debug('Trying multi-branch XOR nsig detection (strategy 2.5)')

            # Pattern A: function(r,p,I,S?) with var a=p^r
            xor_func_pattern_a = re.compile(
                r'([a-zA-Z0-9_$]+)\s*=\s*function\s*\(([a-zA-Z0-9_$]+)\s*,\s*([a-zA-Z0-9_$]+)\s*,\s*([a-zA-Z0-9_$]+)(?:\s*,\s*[a-zA-Z0-9_$]+)*\)\s*\{'
                r'var\s+([a-zA-Z0-9_$]+)\s*=\s*\3\s*\^\s*\2\b'
            )
            # Pattern B: function(n,d,r,...) with var h=d^n (many parameters)
            xor_func_pattern_b = re.compile(
                r'([a-zA-Z0-9_$]+)\s*=\s*function\s*\(([a-zA-Z0-9_$]+)\s*,\s*([a-zA-Z0-9_$]+)\s*,\s*([a-zA-Z0-9_$]+)(?:\s*,\s*[a-zA-Z0-9_$]+){2,}\)\s*\{'
                r'var\s+([a-zA-Z0-9_$]+)\s*=\s*\3\s*\^\s*\2\b'
            )

            for pattern in [xor_func_pattern_a, xor_func_pattern_b]:
                for xfm in pattern.finditer(js):
                    candidate = xfm.group(1)
                    param1 = xfm.group(2)  # r or n
                    param2 = xfm.group(3)  # p or d
                    param3 = xfm.group(4)  # I or r
                    xor_var = xfm.group(5)  # a or h
                    func_start = xfm.start()

                    # Check for self-recursive call or direct call with XOR'd constants
                    # Look for patterns like: candidate(a^C1,a^C2,I) or candidate(D^C1,D^C2,r)
                    chunk = js[func_start:func_start + 1000]
                    recursive = re.search(
                        rf'{re.escape(candidate)}\(([a-zA-Z0-9_$]+)\^(\d+)\s*,\s*\1\^(\d+)\s*,',
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
                    # (the big transformation array) AND substantial array references
                    has_try = 'try{' in func_body or 'try {' in func_body
                    has_null = func_body.count('null') >= 2
                    # Check for array references with XOR: v[a^, W[h^, T[m^, etc.
                    xor_refs = len(re.findall(rf'\w\[{re.escape(xor_var)}\^', func_body))

                    if has_try and has_null and xor_refs > 20:
                        c1 = int(recursive.group(2))
                        c2 = int(recursive.group(3))
                        a_val = c1 ^ c2

                        # Generate control parameter pairs (param1, param2) that route to the
                        # nsig transformation branch. Try several param1 values where
                        # common branch conditions are satisfied.
                        # For functions with (n|72)==n branch: use values that satisfy this
                        # but avoid (n&92)==n which may call r as a function.
                        # For functions with (n>>1&6)>=5: use values like 13-15, 28-31.
                        self._nsig_param_val = []
                        for r_val in [73, 74, 75, 77, 78, 79, 13, 14, 15, 12, 29, 30, 31, 28, 1, 0]:
                            self._nsig_param_val.append([r_val, a_val ^ r_val])

                        logger.debug(
                            f"Nfunc name (strategy 2.5 - XOR multi-branch): {candidate}, "
                            f"constants={c1},{c2}, a={a_val}, params=({param1},{param2},{param3})"
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
    def _extract_xor_branch_nsig_params(
        js: str, func_name: str, global_var_name: str, global_arr: list,
        body: Optional[str] = None, xor_var: Optional[str] = None,
        arg_var: Optional[str] = None, w8_xor_b: Optional[int] = None
    ) -> Optional[list]:
        """For XOR-branch nsig functions where I=param1^param2 controls branching,
        compute the correct control parameters by decoding XOR constants from the function body.

        The nsig branch's first operation is always n.split(''), which appears as:
        arg[GLOBAL[xor_var ^ k1]](GLOBAL[xor_var ^ k2]) where GLOBAL[I^k1]='split', GLOBAL[I^k2]=''

        Returns a list [[X, F]] on success, or None if this is not an XOR-branch function.
        """
        if body is None:
            func_def = re.search(
                r'(?:function\s+%s|(?:var\s+)?%s\s*=\s*function)\s*\(' % (
                    re.escape(func_name), re.escape(func_name)), js)
            if not func_def:
                return None

            func_start = func_def.start()
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
            body = js[func_start:func_end]

        # Check for XOR-branch pattern: var X = Y ^ Z
        xor_m = re.search(r'var\s+([A-Za-z0-9_$]+)\s*=\s*([A-Za-z0-9_$]+)\s*\^\s*([A-Za-z0-9_$]+)', body)
        if not xor_m:
            return None

        if xor_var is None:
            xor_var = xor_m.group(1)

        if 'split' not in global_arr or '' not in global_arr:
            return None
        split_idx = global_arr.index('split')
        empty_idx = global_arr.index('')

        # Find the split operation: arg[GLOBAL[xor_var ^ k1]](GLOBAL[xor_var ^ k2])
        # or arg[GLOBAL[xor_var ^ k1]](GLOBAL[k2]) — some players use direct index for k2.
        # GLOBAL[I^k1] must be 'split' and GLOBAL[...k2] must be ''.
        # Multiple matches may exist; iterate and validate each one.
        if arg_var:
            arg_pat = re.escape(arg_var)
        else:
            arg_pat = r'[A-Za-z0-9_$]+'
        gv = re.escape(global_var_name)
        xv = re.escape(xor_var)
        split_patterns = [
            # Both k1 and k2 are XOR'd: arg[G[xor^k1]](G[xor^k2])
            re.compile(
                arg_pat + r'\[' + gv + r'\[' + xv + r'\^(\d+)\]\]\(' +
                gv + r'\[' + xv + r'\^(\d+)\]\)'
            ),
            # Only k1 is XOR'd, k2 is direct: arg[G[xor^k1]](G[k2])
            re.compile(
                arg_pat + r'\[' + gv + r'\[' + xv + r'\^(\d+)\]\]\(' +
                gv + r'\[(\d+)\]\)'
            ),
            # k1 is direct, k2 is XOR'd: arg[G[k1]](G[xor^k2])
            re.compile(
                arg_pat + r'\[' + gv + r'\[(\d+)\]\]\(' +
                gv + r'\[' + xv + r'\^(\d+)\]\)'
            ),
            # Both k1 and k2 are direct: arg[G[k1]](G[k2])
            re.compile(
                arg_pat + r'\[' + gv + r'\[(\d+)\]\]\(' +
                gv + r'\[(\d+)\]\)'
            ),
        ]

        I = None
        for pat_idx, pattern in enumerate(split_patterns):
            for split_op in pattern.finditer(body):
                k1 = int(split_op.group(1))
                k2_raw = int(split_op.group(2))

                # Determine I_candidate and check_idx based on pattern type
                if pat_idx == 0:  # Both XOR'd: arg[G[xor^k1]](G[xor^k2])
                    I_candidate = split_idx ^ k1
                    check_idx = I_candidate ^ k2_raw
                elif pat_idx == 1:  # k1 XOR'd, k2 direct: arg[G[xor^k1]](G[k2])
                    I_candidate = split_idx ^ k1
                    check_idx = k2_raw
                elif pat_idx == 2:  # k1 direct, k2 XOR'd: arg[G[k1]](G[xor^k2])
                    if k1 != split_idx:
                        continue  # k1 doesn't match split_idx, skip
                    # I is determined by k2: xor^k2 = empty_idx => I = empty_idx ^ k2
                    I_candidate = empty_idx ^ k2_raw
                    check_idx = empty_idx
                else:  # pat_idx == 3: Both direct: arg[G[k1]](G[k2])
                    if k1 != split_idx or k2_raw != empty_idx:
                        continue
                    if w8_xor_b is not None:
                        I_candidate = w8_xor_b
                    else:
                        I_candidate = 0  # No XOR needed
                    check_idx = k2_raw
                if 0 <= check_idx < len(global_arr) and global_arr[check_idx] == '':
                    # Validate I_candidate: if w8_xor_b is known (from the catch block),
                    # the correct I must match it. This prevents picking a split operation
                    # from a non-nsig branch that happens to also use split('').
                    if w8_xor_b is not None and I_candidate != w8_xor_b:
                        continue
                    I = I_candidate
                    break
            if I is not None:
                break

        if I is None:
            return None

        # Find valid X value by evaluating the branch condition.
        # var xor = p1 ^ p2; the branch selector is one of p1, p2.
        param_names = [xor_m.group(2), xor_m.group(3)]
        split_pos = split_op.start()
        pre_split = body[:split_pos]

        # Find the labeled-block condition closest to the split operation.
        # The nsig branch is: if(COND)a:{ ... split ... catch ... break a }
        # We want the LAST if(...)label:{ before the split, which is the actual
        # nsig branch guard (not an earlier unrelated branch).
        X = None
        mask_branch_meta = None
        or_branch_meta = None

        def _eval_js_branch(cond_str: str, pname: str, x_candidate: int) -> bool:
            expr = re.sub(
                r'\b' + re.escape(pname) + r'\b',
                str(x_candidate), cond_str
            )
            expr = expr.replace('&&', ' and ').replace('||', ' or ')
            expr = expr.replace('!', ' not ')
            return bool(eval(expr))  # noqa: S307 - restricted branch syntax only

        def _normalize_js_cond(cond_str: str) -> str:
            return re.sub(r'\s+', '', cond_str)

        def _extract_if_conditions(src: str) -> list[str]:
            conds = []
            for if_match in re.finditer(r'if\s*\(', src):
                open_idx = if_match.end() - 1
                depth = 1
                cond_end = None
                for i in range(open_idx + 1, len(src)):
                    if src[i] == '(':
                        depth += 1
                    elif src[i] == ')':
                        depth -= 1
                        if depth == 0:
                            cond_end = i
                            break
                if cond_end is None:
                    continue
                conds.append(src[open_idx + 1:cond_end])
            return conds

        def _pick_branch_candidate(
            pname: str, predicate, extra_conds: list[str]
        ) -> Optional[tuple[int, list[str]]]:
            best_x = None
            best_hits = None
            for x_candidate in range(0, 256):
                if not predicate(x_candidate):
                    continue
                hits = []
                for cond in extra_conds:
                    if pname not in cond:
                        continue
                    try:
                        if _eval_js_branch(cond, pname, x_candidate):
                            hits.append(cond)
                    except Exception:
                        continue
                if best_hits is None or len(hits) < len(best_hits):
                    best_x = x_candidate
                    best_hits = hits
                    if not hits:
                        break
            if best_x is None:
                return None
            return best_x, best_hits or []

        # Pattern 1: !(P-C>>S) — older style, e.g. !(X-9>>3)
        for pname in param_names:
            branch_m = re.search(
                r'!\s*\(' + re.escape(pname) + r'\s*-\s*(\d+)\s*>>\s*(\d+)\)',
                pre_split
            )
            if branch_m:
                center = int(branch_m.group(1))
                shift = int(branch_m.group(2))
                # pname is the branch-selector; the other param = I ^ pname
                for x_candidate in range(0, 256):
                    if not ((x_candidate - center) >> shift):
                        X = x_candidate
                        break
                if X is not None:
                    F = I ^ X
                    break

        # Pattern 2: (P+C>>S)==V — newer style, e.g. (O+4>>3)==3 or O+4>>3==3
        # This pattern appears in labeled blocks: if(O+4>>3==3)a:{...split...}
        # So we need to search the entire function body, not just pre_split
        if X is None:
            for pname in param_names:
                branch_m = re.search(
                    r'if\s*\(\s*\(?' + re.escape(pname) + r'\s*\+\s*(\d+)\s*>>\s*(\d+)\)?\s*==\s*(\d+)\s*\)\s*[a-zA-Z_$]:\{',
                    body
                )
                if branch_m:
                    offset = int(branch_m.group(1))
                    shift = int(branch_m.group(2))
                    target = int(branch_m.group(3))
                    # (pname + offset) >> shift == target
                    # So: target * (2^shift) <= pname + offset < (target+1) * (2^shift)
                    # Therefore: target * (2^shift) - offset <= pname < (target+1) * (2^shift) - offset
                    min_val = target * (1 << shift) - offset
                    max_val = (target + 1) * (1 << shift) - offset
                    # Pick the minimum value to avoid conflicts with other branches
                    X = min_val
                    if 0 <= X < 256:
                        F = I ^ X
                        break

        # Pattern 3: Compound conditions with && — e.g. (p-7|46)<p&&(p+4&56)>=p
        # This pattern appears in players from 2025+ with multiple branch conditions
        if X is None:
            for pname in param_names:
                # Match compound conditions: (P-C1|C2)<P&&(P+C3&C4)>=P
                branch_m = re.search(
                    r'if\s*\(\s*\(' + re.escape(pname) + r'-(\d+)\|(\d+)\)<' + re.escape(pname) +
                    r'&&\(' + re.escape(pname) + r'\+(\d+)&(\d+)\)>=' + re.escape(pname) + r'\s*\)\s*[a-zA-Z_$]:\{',
                    body
                )
                if branch_m:
                    c1 = int(branch_m.group(1))
                    c2 = int(branch_m.group(2))
                    c3 = int(branch_m.group(3))
                    c4 = int(branch_m.group(4))
                    # Find a p value that satisfies both conditions:
                    # (p-c1|c2)<p && (p+c3&c4)>=p
                    # Also avoid p values that might trigger other branches:
                    # - Avoid (p|24)==p (branch 1)
                    # - Avoid p<<1&7==0 (branch 3)
                    for x_candidate in range(1, 256):
                        cond1 = ((x_candidate - c1) | c2) < x_candidate
                        cond2 = ((x_candidate + c3) & c4) >= x_candidate
                        # Check if this p would trigger other common branch patterns
                        avoid_branch1 = (x_candidate | 24) == x_candidate
                        avoid_branch3 = (x_candidate << 1) & 7 == 0
                        if cond1 and cond2 and not avoid_branch1 and not avoid_branch3:
                            X = x_candidate
                            F = I ^ X
                            logger.debug(
                                f"Compound condition matched: ({pname}-{c1}|{c2})<{pname}&&"
                                f"({pname}+{c3}&{c4})>={pname}, X={X}"
                            )
                            break
                    if X is not None:
                        break

        # Pattern 4: Simple arithmetic range-check — e.g. P+3<38&&P+4>=26
        # This pattern uses plain < and >= comparisons with constants
        if X is None:
            for pname in param_names:
                branch_m = re.search(
                    r'if\s*\(\s*' + re.escape(pname) + r'\+(\d+)<(\d+)&&'
                    + re.escape(pname) + r'\+(\d+)>=(\d+)\s*\)\s*[a-zA-Z_$]:\{',
                    body
                )
                if branch_m:
                    off1 = int(branch_m.group(1))
                    limit1 = int(branch_m.group(2))
                    off2 = int(branch_m.group(3))
                    limit2 = int(branch_m.group(4))
                    # p+off1 < limit1 && p+off2 >= limit2
                    # => p < limit1 - off1  AND  p >= limit2 - off2
                    lo = limit2 - off2
                    hi = limit1 - off1
                    # Collect all OTHER branch conditions in the body to avoid conflicts
                    all_branch_conds = list(re.finditer(
                        r'if\s*\((.+?)\)\s*[a-zA-Z_$]:\{', body
                    ))
                    # Pick the highest valid p to minimize overlap with lower branches
                    for x_candidate in range(hi - 1, lo - 1, -1):
                        if x_candidate < 0:
                            continue
                        # Check that this p does NOT trigger other branches
                        triggers_other = False
                        for other_cond in all_branch_conds:
                            cond_str = other_cond.group(1)
                            if cond_str == branch_m.group(0).split('(', 1)[1].rsplit(')', 1)[0]:
                                continue  # skip our own condition
                            if pname not in cond_str:
                                continue
                            try:
                                if _eval_js_branch(cond_str, pname, x_candidate):
                                    triggers_other = True
                                    break
                            except Exception:
                                continue
                        if not triggers_other:
                            X = x_candidate
                            F = I ^ X
                            logger.debug(
                                f"Range-check condition matched: {pname}+{off1}<{limit1}&&"
                                f"{pname}+{off2}>={limit2}, range=[{lo},{hi}), X={X}"
                            )
                            break
                    if X is not None:
                        break

        # Pattern 5: Bitmask-equality branch â€” e.g. (U&115)==U
        # Some 2026 players route nsig through this branch, but low control
        # values also trigger later helper branches that expect extra args.
        # Prefer the first candidate that satisfies the mask while avoiding
        # those helper branches.
        if X is None:
            for pname in param_names:
                branch_m = re.search(
                    r'if\s*\(\s*\(' + re.escape(pname) + r'\s*&\s*(\d+)\)\s*==\s*'
                    + re.escape(pname) + r'\s*\)\s*[a-zA-Z_$]:\{',
                    body
                )
                if not branch_m:
                    continue

                mask = int(branch_m.group(1))
                target_norm = _normalize_js_cond(f'({pname}&{mask})=={pname}')
                extra_conds = []
                extra_patterns = [
                    r'\(\(\s*' + re.escape(pname) + r'\s*\|\s*\d+\)\s*&\s*\d+\)\s*<\s*\d+\s*&&\s*'
                    r'\(\s*' + re.escape(pname) + r'\s*\^\s*\d+\)\s*>>\s*\d+\s*>=\s*0',
                    r'\b' + re.escape(pname) + r'\s*-\s*\d+\s*>>\s*\d+\s*>=\s*0\s*&&\s*'
                    r'\(\s*' + re.escape(pname) + r'\s*-\s*\d+\s*&\s*\d+\)\s*<\s*\d+',
                    r'\(\s*' + re.escape(pname) + r'\s*\|\s*\d+\)\s*==\s*' + re.escape(pname),
                    r'\(\s*' + re.escape(pname) + r'\s*&\s*\d+\)\s*==\s*' + re.escape(pname),
                ]
                for extra_pat in extra_patterns:
                    for match in re.finditer(extra_pat, body):
                        cond = match.group(0)
                        if _normalize_js_cond(cond) != target_norm and cond not in extra_conds:
                            extra_conds.append(cond)

                for x_candidate in range(0, 256):
                    if (x_candidate & mask) != x_candidate:
                        continue
                    try:
                        if any(_eval_js_branch(cond, pname, x_candidate) for cond in extra_conds):
                            continue
                    except Exception:
                        continue
                    X = x_candidate
                    F = I ^ X
                    mask_branch_meta = (pname, mask, extra_conds)
                    logger.debug(
                        f"Bitmask-equality branch matched: ({pname}&{mask})=={pname}, X={X}"
                    )
                    break
                if X is not None:
                    break

        # Pattern 6: Or-equality branch - e.g. (n|8)==n or (I|40)==I
        # Some 2026 players route nsig through this branch but neighboring
        # helper branches also fire on low or even control values.
        if X is None:
            all_if_conds = _extract_if_conditions(body)
            for pname in param_names:
                branch_matches = list(re.finditer(
                    r'if\s*\(\s*(?P<cond>\(\s*' + re.escape(pname) + r'\s*\|\s*'
                    r'(?P<mask>\d+)\)\s*==\s*' + re.escape(pname) + r')\s*\)\s*'
                    r'[a-zA-Z_$]:\{',
                    pre_split
                ))
                if not branch_matches:
                    continue
                branch_m = branch_matches[-1]

                mask = int(branch_m.group('mask'))
                target_norm = _normalize_js_cond(branch_m.group('cond'))
                extra_conds = []
                for cond in all_if_conds:
                    if pname not in cond:
                        continue
                    if _normalize_js_cond(cond) == target_norm:
                        continue
                    extra_conds.append(cond)

                extra_patterns = [
                    r'\(\s*' + re.escape(pname) + r'\s*[+-]\s*\d+\s*\^\s*\d+\)\s*[<>]=?\s*'
                    + re.escape(pname) + r'\s*&&\s*\(\s*' + re.escape(pname)
                    + r'\s*[+-]\s*\d+\s*\^\s*\d+\)\s*[<>]=?\s*' + re.escape(pname),
                    r'\b' + re.escape(pname) + r'\s*-\s*\d+\s*<<\s*\d+\s*<\s*'
                    + re.escape(pname) + r'\s*&&\s*\(\s*' + re.escape(pname)
                    + r'\s*\+\s*\d+\s*&\s*\d+\)\s*>=\s*' + re.escape(pname),
                    r'\(\s*' + re.escape(pname) + r'\s*\+\s*\d+\s*\^\s*\d+\)\s*>=\s*'
                    + re.escape(pname) + r'\s*&&\s*' + re.escape(pname)
                    + r'\s*\+\s*\d+\s*>>\s*\d+\s*<\s*' + re.escape(pname),
                    r'\(\(\s*' + re.escape(pname) + r'\s*\|\s*\d+\)\s*&\s*\d+\)\s*<\s*\d+\s*&&\s*'
                    r'\(\s*' + re.escape(pname) + r'\s*\^\s*\d+\)\s*>>\s*\d+\s*>=\s*0',
                    r'\(\s*' + re.escape(pname) + r'\s*\|\s*\d+\)\s*==\s*' + re.escape(pname),
                ]
                for extra_pat in extra_patterns:
                    for match in re.finditer(extra_pat, body):
                        cond = match.group(0)
                        if _normalize_js_cond(cond) != target_norm and cond not in extra_conds:
                            extra_conds.append(cond)

                picked = _pick_branch_candidate(
                    pname,
                    lambda x_candidate, mask=mask: (x_candidate | mask) == x_candidate,
                    extra_conds
                )
                if picked is None:
                    continue

                X, triggered = picked
                F = I ^ X
                or_branch_meta = (pname, mask, extra_conds)
                logger.debug(
                    f"Or-equality branch matched: ({pname}|{mask})=={pname}, "
                    f"X={X}, extra_hits={len(triggered)}"
                )
                break

        if X is None:
            # Collect ALL if(COND)label:{ conditions before the split,
            # then try them in reverse order (closest to split first).
            # Use a more precise pattern that handles nested parentheses better:
            # Look for if(...) followed immediately by label:{
            # We search for all occurrences and manually extract the condition
            all_conds = []
            all_if_conds = _extract_if_conditions(pre_split)
            # Find all "if(" positions
            for if_match in re.finditer(r'if\s*\(', pre_split):
                if_start = if_match.end() - 1  # Position of opening (
                # Find the matching closing ) by counting parentheses
                depth = 0
                cond_end = None
                for i in range(if_start, len(pre_split)):
                    if pre_split[i] == '(':
                        depth += 1
                    elif pre_split[i] == ')':
                        depth -= 1
                        if depth == 0:
                            cond_end = i
                            break
                if cond_end is None:
                    continue
                # Check if followed by label:{
                label_match = re.match(r'\s*([a-zA-Z_$]+)\s*:\s*\{', pre_split[cond_end + 1:])
                if label_match:
                    condition = pre_split[if_start + 1:cond_end]
                    all_conds.append((if_match.start(), condition))

            for _, nsig_cond in reversed(all_conds):
                for pname in param_names:
                    if pname not in nsig_cond:
                        continue
                    target_norm = _normalize_js_cond(nsig_cond)
                    extra_conds = []
                    for other_cond in all_if_conds:
                        if pname not in other_cond:
                            continue
                        if _normalize_js_cond(other_cond) == target_norm:
                            continue
                        extra_conds.append(other_cond)

                    picked = _pick_branch_candidate(
                        pname,
                        lambda x_candidate, cond=nsig_cond, pname=pname: _eval_js_branch(
                            cond, pname, x_candidate
                        ),
                        extra_conds
                    )
                    if picked is None:
                        continue
                    X, _ = picked
                    F = I ^ X
                    break
                    if X is not None:
                        break
                if X is not None:
                    break

        if X is None:
            return None

        # Generate multiple candidate parameter pairs to handle different branch conditions.
        # Some branches may call r/W as a function or have other side effects, so we need
        # to try alternative X values that still satisfy the nsig branch condition.
        candidates = [[X, I ^ X]]

        # For (p&mask)==p branches, keep a few more safe values that avoid the
        # unrelated helper branches which expect extra parameters.
        if mask_branch_meta is not None:
            pname, mask, extra_conds = mask_branch_meta
            for alt_x in range(X + 1, 256):
                if (alt_x & mask) != alt_x:
                    continue
                try:
                    if any(_eval_js_branch(cond, pname, alt_x) for cond in extra_conds):
                        continue
                except Exception:
                    continue
                candidates.append([alt_x, I ^ alt_x])
                if len(candidates) >= 8:
                    break

        # For (p|mask)==p branches, keep a few more values that still avoid
        # the neighboring helper branches.
        if or_branch_meta is not None:
            pname, mask, extra_conds = or_branch_meta
            for alt_x in range(X + 1, 256):
                if (alt_x | mask) != alt_x:
                    continue
                try:
                    if any(_eval_js_branch(cond, pname, alt_x) for cond in extra_conds):
                        continue
                except Exception:
                    continue
                candidates.append([alt_x, I ^ alt_x])
                if len(candidates) >= 8:
                    break

        # For (n|72)==n branches, try values that satisfy this but avoid problematic branches
        if (X | 72) == X:
            # Try alternative values that satisfy (n|72)==n but not (n&92)==n
            for alt_x in [73, 74, 75, 77, 78, 79, 104, 105, 106, 107, 108, 109, 110, 111]:
                if (alt_x | 72) == alt_x and (alt_x & 92) != alt_x:
                    candidates.append([alt_x, I ^ alt_x])

        # For !((Q|4)>>4) branches (Q<16), try values that avoid (Q<<1&6)<1 branches
        # This handles players where nsig branch is !((Q|4)>>4) which means (Q|4)<16
        if X < 16:
            # Try alternative values Q where !((Q|4)>>4) but not ((Q<<1&6)<1)
            for alt_x in [1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15]:
                if alt_x < 16 and (alt_x << 1 & 6) >= 1:
                    candidates.append([alt_x, I ^ alt_x])

        logger.debug(
            f"XOR-branch nsig detected: I={I}, X={X}, F={I^X} "
            f"(k1={k1}, split_idx={split_idx}), candidates={len(candidates)}"
        )
        return candidates

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
