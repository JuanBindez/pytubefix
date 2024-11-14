"""
This module contains all the logic needed to interpret the JavaScript obfuscation functions that YouTube uses.

All this code was based on the yt-dlp project, see: https://github.com/yt-dlp/yt-dlp.

"""

import collections
import contextlib
import itertools
import json
import math
import operator
import re
import datetime
import email.utils
import calendar


def js_to_json(code, vars={}, *, strict=False):
    """Converts JavaScript code to JSON"""
    # vars is a dict of var, val pairs to substitute
    STRING_QUOTES = '\'"`'
    STRING_RE = '|'.join(rf'{q}(?:\\.|[^\\{q}])*{q}' for q in STRING_QUOTES)
    COMMENT_RE = r'/\*(?:(?!\*/).)*?\*/|//[^\n]*\n'
    SKIP_RE = fr'\s*(?:{COMMENT_RE})?\s*'
    INTEGER_TABLE = (
        (fr'(?s)^(0[xX][0-9a-fA-F]+){SKIP_RE}:?$', 16),
        (fr'(?s)^(0+[0-7]+){SKIP_RE}:?$', 8),
    )

    def process_escape(match):
        JSON_PASSTHROUGH_ESCAPES = R'"\bfnrtu'
        escape = match.group(1) or match.group(2)

        return (Rf'\{escape}' if escape in JSON_PASSTHROUGH_ESCAPES
                else R'\u00' if escape == 'x'
                else '' if escape == '\n'
                else escape)

    def template_substitute(match):
        evaluated = js_to_json(match.group(1), vars, strict=strict)
        if evaluated[0] == '"':
            return json.loads(evaluated)
        return evaluated

    def fix_kv(m):
        """Fixes a key-value pair"""
        v = m.group(0)
        if v in ('true', 'false', 'null'):
            return v
        if v in ('undefined', 'void 0'):
            return 'null'
        if v.startswith('/*') or v.startswith('//') or v.startswith('!') or v == ',':
            return ''

        if v[0] in STRING_QUOTES:
            v = re.sub(r'(?s)\${([^}]+)}', template_substitute,
                       v[1:-1]) if v[0] == '`' else v[1:-1]
            escaped = re.sub(r'(?s)(")|\\(.)', process_escape, v)
            r = f'"{escaped}"'
            return r

        for regex, base in INTEGER_TABLE:
            im = re.match(regex, v)
            if im:
                i = int(im.group(1), base)
                return f'"{i}":' if v.endswith(':') else str(i)

        if v in vars:
            try:
                if not strict:
                    json.loads(vars[v])
            except json.JSONDecodeError:
                return json.dumps(vars[v])

            return vars[v]

        if not strict:
            return f'"{v}"'

        raise ValueError(f'Unknown value: {v}')

    def create_map(mobj):
        r = json.dumps(
            dict(json.loads(js_to_json(mobj.group(1) or '[]', vars=vars))))
        return r

    code = re.sub(r'new Map\((\[.*?\])?\)', create_map, code)
    if not strict:
        code = re.sub(r'new Date\((".+")\)', r'\g<1>', code)
        code = re.sub(r'new \w+\((.*?)\)',
                      lambda m: json.dumps(m.group(0)), code)
        code = re.sub(r'parseInt\([^\d]+(\d+)[^\d]+\)', r'\1', code)
        code = re.sub(
            r'\(function\([^)]*\)\s*\{[^}]*\}\s*\)\s*\(\s*(["\'][^)]*["\'])\s*\)', r'\1', code)

    return re.sub(rf'''(?sx)
        {STRING_RE}|
        {COMMENT_RE}|,(?={SKIP_RE}[\]}}])|
        void\s0|(?:(?<![0-9])[eE]|[a-df-zA-DF-Z_$])[.a-zA-Z_$0-9]*|
        \b(?:0[xX][0-9a-fA-F]+|0+[0-7]+)(?:{SKIP_RE}:)?|
        [0-9]+(?={SKIP_RE}:)|
        !+
        ''', fix_kv, code)


DATE_FORMATS = (
    '%d %B %Y',
    '%d %b %Y',
    '%B %d %Y',
    '%B %dst %Y',
    '%B %dnd %Y',
    '%B %drd %Y',
    '%B %dth %Y',
    '%b %d %Y',
    '%b %dst %Y',
    '%b %dnd %Y',
    '%b %drd %Y',
    '%b %dth %Y',
    '%b %dst %Y %I:%M',
    '%b %dnd %Y %I:%M',
    '%b %drd %Y %I:%M',
    '%b %dth %Y %I:%M',
    '%Y %m %d',
    '%Y-%m-%d',
    '%Y.%m.%d.',
    '%Y/%m/%d',
    '%Y/%m/%d %H:%M',
    '%Y/%m/%d %H:%M:%S',
    '%Y%m%d%H%M',
    '%Y%m%d%H%M%S',
    '%Y%m%d',
    '%Y-%m-%d %H:%M',
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%d %H:%M:%S.%f',
    '%Y-%m-%d %H:%M:%S:%f',
    '%d.%m.%Y %H:%M',
    '%d.%m.%Y %H.%M',
    '%Y-%m-%dT%H:%M:%SZ',
    '%Y-%m-%dT%H:%M:%S.%fZ',
    '%Y-%m-%dT%H:%M:%S.%f0Z',
    '%Y-%m-%dT%H:%M:%S',
    '%Y-%m-%dT%H:%M:%S.%f',
    '%Y-%m-%dT%H:%M',
    '%b %d %Y at %H:%M',
    '%b %d %Y at %H:%M:%S',
    '%B %d %Y at %H:%M',
    '%B %d %Y at %H:%M:%S',
    '%H:%M %d-%b-%Y',
)

DATE_FORMATS_MONTH_FIRST = list(DATE_FORMATS)
DATE_FORMATS_MONTH_FIRST.extend([
    '%m-%d-%Y',
    '%m.%d.%Y',
    '%m/%d/%Y',
    '%m/%d/%y',
    '%m/%d/%Y %H:%M:%S',
])

TIMEZONE_NAMES = {
    'UT': 0, 'UTC': 0, 'GMT': 0, 'Z': 0,
    'AST': -4, 'ADT': -3,  # Atlantic (used in Canada)
    'EST': -5, 'EDT': -4,  # Eastern
    'CST': -6, 'CDT': -5,  # Central
    'MST': -7, 'MDT': -6,  # Mountain
    'PST': -8, 'PDT': -7  # Pacific
}
DATE_FORMATS_DAY_FIRST = list(DATE_FORMATS)
DATE_FORMATS_DAY_FIRST.extend([
    '%d-%m-%Y',
    '%d.%m.%Y',
    '%d.%m.%y',
    '%d/%m/%Y',
    '%d/%m/%y',
    '%d/%m/%Y %H:%M:%S',
    '%d-%m-%Y %H:%M',
    '%H:%M %d/%m/%Y',
])


def extract_timezone(date_str):
    r = r'''(?x)
            ^.{8,}?                                              # >=8 char non-TZ prefix, if present
            (?P<tz>Z|                                            # just the UTC Z, or
                (?:(?<=.\b\d{4}|\b\d{2}:\d\d)|                   # preceded by 4 digits or hh:mm or
                   (?<!.\b[a-zA-Z]{3}|[a-zA-Z]{4}|..\b\d\d))     # not preceded by 3 alpha word or >= 4 alpha or 2 digits
                   [ ]?                                          # optional space
                (?P<sign>\+|-)                                   # +/-
                (?P<hours>[0-9]{2}):?(?P<minutes>[0-9]{2})       # hh[:]mm
            $)
        '''
    m = re.search(r, date_str)
    if not m:
        m = re.search(r'\d{1,2}:\d{1,2}(?:\.\d+)?(?P<tz>\s*[A-Z]+)$', date_str)
        timezone = TIMEZONE_NAMES.get(m and m.group('tz').strip())
        if timezone is not None:
            date_str = date_str[:-len(m.group('tz'))]
        timezone = datetime.timedelta(hours=timezone or 0)
    else:
        date_str = date_str[:-len(m.group('tz'))]
        if not m.group('sign'):
            timezone = datetime.timedelta()
        else:
            sign = 1 if m.group('sign') == '+' else -1
            timezone = datetime.timedelta(
                hours=sign * int(m.group('hours')),
                minutes=sign * int(m.group('minutes')))
    return timezone, date_str


def date_formats(day_first=True):
    """Return a list of date formats"""
    return DATE_FORMATS_DAY_FIRST if day_first else DATE_FORMATS_MONTH_FIRST


def unified_timestamp(date_str, day_first=True):
    """Converts a date string to a timestamp"""
    if not isinstance(date_str, str):
        return None

    date_str = re.sub(r'\s+', ' ', re.sub(
        r'(?i)[,|]|(mon|tues?|wed(nes)?|thu(rs)?|fri|sat(ur)?)(day)?', '', date_str))

    pm_delta = 12 if re.search(r'(?i)PM', date_str) else 0
    timezone, date_str = extract_timezone(date_str)

    # Remove AM/PM + timezone
    date_str = re.sub(r'(?i)\s*(?:AM|PM)(?:\s+[A-Z]+)?', '', date_str)

    # Remove unrecognized timezones from ISO 8601 alike timestamps
    m = re.search(r'\d{1,2}:\d{1,2}(?:\.\d+)?(?P<tz>\s*[A-Z]+)$', date_str)
    if m:
        date_str = date_str[:-len(m.group('tz'))]

    # Python only supports microseconds, so remove nanoseconds
    m = re.search(
        r'^([0-9]{4,}-[0-9]{1,2}-[0-9]{1,2}T[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}\.[0-9]{6})[0-9]+$', date_str)
    if m:
        date_str = m.group(1)

    for expression in date_formats(day_first):
        with contextlib.suppress(ValueError):
            dt = datetime.datetime.strptime(
                date_str, expression) - timezone + datetime.timedelta(hours=pm_delta)
            return calendar.timegm(dt.timetuple())

    timetuple = email.utils.parsedate_tz(date_str)
    if timetuple:
        return calendar.timegm(timetuple) + pm_delta * 3600 - timezone.total_seconds()


class NO_DEFAULT:
    pass


class function_with_repr:
    def __init__(self, func, repr_=None):
        self.func, self.__repr = func, repr_

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __repr__(self):
        if self.__repr:
            return self.__repr
        return f'{self.func.__module__}.{self.func.__qualname__}'


def remove_quotes(s):
    """Remove quotes from a string"""
    if s is None or len(s) < 2:
        return s
    for quote in ('"', "'",):
        if s[0] == quote and s[-1] == quote:
            return s[1:-1]
    return s


def truncate_string(s, left, right=0):
    """Truncate a string to a given length"""
    assert left > 3 and right >= 0
    if s is None or len(s) <= left + right:
        return s
    return f'{s[:left - 3]}...{s[-right:] if right else ""}'


def _js_bit_op(op):
    def zeroise(x):
        if x in (None, JS_Undefined):
            return 0
        with contextlib.suppress(TypeError):
            if math.isnan(x):  # NB: NaN cannot be checked by membership
                return 0
        return x

    def wrapped(a, b):
        return op(zeroise(a), zeroise(b)) & 0xffffffff

    return wrapped


def _js_arith_op(op):
    def wrapped(a, b):
        if JS_Undefined in (a, b):
            return float('nan')
        return op(a or 0, b or 0)

    return wrapped


def _js_div(a, b):
    if JS_Undefined in (a, b) or not (a or b):
        return float('nan')
    return (a or 0) / b if b else float('inf')


def _js_mod(a, b):
    if JS_Undefined in (a, b) or not b:
        return float('nan')
    return (a or 0) % b


def _js_exp(a, b):
    if not b:
        return 1  # even 0 ** 0 !!
    if JS_Undefined in (a, b):
        return float('nan')
    return (a or 0) ** b


def _js_eq_op(op):
    def wrapped(a, b):
        if {a, b} <= {None, JS_Undefined}:
            return op(a, a)
        return op(a, b)

    return wrapped


def _js_comp_op(op):
    def wrapped(a, b):
        if JS_Undefined in (a, b):
            return False
        if isinstance(a, str) or isinstance(b, str):
            return op(str(a or 0), str(b or 0))
        return op(a or 0, b or 0)

    return wrapped


def _js_ternary(cndn, if_true=True, if_false=False):
    """Simulate JS's ternary operator (cndn?if_true:if_false)"""
    if cndn == "null":
        print()
    if cndn in (False, None, 0, '', JS_Undefined):
        return if_false
    with contextlib.suppress(TypeError):
        if math.isnan(cndn):  # NB: NaN cannot be checked by membership
            return if_false
    return if_true


# Ref: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Operator_Precedence
_OPERATORS = {  # None => Defined in JSInterpreter._operator
    '?': None,
    '??': None,
    '||': None,
    '&&': None,

    '|': _js_bit_op(operator.or_),
    '^': _js_bit_op(operator.xor),
    '&': _js_bit_op(operator.and_),

    '===': operator.is_,
    '!==': operator.is_not,
    '==': _js_eq_op(operator.eq),
    '!=': _js_eq_op(operator.ne),

    '<=': _js_comp_op(operator.le),
    '>=': _js_comp_op(operator.ge),
    '<': _js_comp_op(operator.lt),
    '>': _js_comp_op(operator.gt),

    '>>': _js_bit_op(operator.rshift),
    '<<': _js_bit_op(operator.lshift),

    '+': _js_arith_op(operator.add),
    '-': _js_arith_op(operator.sub),

    '*': _js_arith_op(operator.mul),
    '%': _js_mod,
    '/': _js_div,
    '**': _js_exp,
}

_COMP_OPERATORS = {'===', '!==', '==', '!=', '<=', '>=', '<', '>'}

_NAME_RE = r'[a-zA-Z_$][\w$]*'
_MATCHING_PARENS = dict(zip(*zip('()', '{}', '[]')))
_QUOTES = '\'"/'


class JS_Undefined:
    pass


class JS_Break(Exception):
    def __init__(self):
        Exception.__init__(self, 'Invalid break')


class JS_Continue(Exception):
    def __init__(self):
        Exception.__init__(self, 'Invalid continue')


class JS_Throw(Exception):
    def __init__(self, e):
        self.error = e
        Exception.__init__(self, f'Uncaught exception {e}')


class LocalNameSpace(collections.ChainMap):
    def __setitem__(self, key, value):
        for scope in self.maps:
            if key in scope:
                scope[key] = value
                return
        self.maps[0][key] = value

    def __delitem__(self, key):
        raise NotImplementedError('Deleting is not supported')


class JSInterpreter:
    __named_object_counter = 0

    _RE_FLAGS = {
        # special knowledge: Python's re flags are bitmask values, current max 128
        # invent new bitmask values well above that for literal parsing
        # TODO: new pattern class to execute matches with these flags
        'd': 1024,  # Generate indices for substring matches
        'g': 2048,  # Global search
        'i': re.I,  # Case-insensitive search
        'm': re.M,  # Multi-line search
        's': re.S,  # Allows . to match newline characters
        'u': re.U,  # Treat a pattern as a sequence of unicode code points
        'y': 4096,  # Perform a "sticky" search that matches starting at the current position in the target string
    }

    def __init__(self, code, objects=None):
        self.code, self._functions = code, {}
        self._objects = {} if objects is None else objects

    class Exception(Exception):
        def __init__(self, msg, expr=None, *args, **kwargs):
            if expr is not None:
                msg = f'{msg.rstrip()} in: {truncate_string(expr, 50, 50)}'
            super().__init__(msg, *args, **kwargs)

    def _named_object(self, namespace, obj):
        self.__named_object_counter += 1
        name = f'__pytubefix_jsinterp_obj{self.__named_object_counter}'
        if callable(obj) and not isinstance(obj, function_with_repr):
            obj = function_with_repr(obj, f'F<{self.__named_object_counter}>')
        namespace[name] = obj
        return name

    @classmethod
    def _regex_flags(cls, expr):
        flags = 0
        if not expr:
            return flags, expr
        for idx, ch in enumerate(expr):
            if ch not in cls._RE_FLAGS:
                break
            flags |= cls._RE_FLAGS[ch]
        return flags, expr[idx + 1:]

    @staticmethod
    def _separate(expr, delim=',', max_split=None):
        OP_CHARS = '+-*/%&|^=<>!,;{}:['
        if not expr:
            return
        counters = {k: 0 for k in _MATCHING_PARENS.values()}
        start, splits, pos, delim_len = 0, 0, 0, len(delim) - 1
        in_quote, escaping, after_op, in_regex_char_group = None, False, True, False
        for idx, char in enumerate(expr):

            if not in_quote and char in _MATCHING_PARENS:
                counters[_MATCHING_PARENS[char]] += 1
            elif not in_quote and char in counters:
                # Something's wrong if we get negative, but ignore it anyway
                if counters[char]:
                    counters[char] -= 1
            elif not escaping:
                if char in _QUOTES and in_quote in (char, None):
                    if in_quote or after_op or char != '/':
                        in_quote = None if in_quote and not in_regex_char_group else char
                elif in_quote == '/' and char in '[]':
                    in_regex_char_group = char == '['
            escaping = not escaping and in_quote and char == '\\'
            in_unary_op = (not in_quote and not in_regex_char_group
                           and after_op not in (True, False) and char in '-+')
            after_op = char if (not in_quote and char in OP_CHARS) else (
                char.isspace() and after_op)

            if char != delim[pos] or any(counters.values()) or in_quote or in_unary_op:
                pos = 0
                continue
            if pos != delim_len:
                pos += 1
                continue
            yield expr[start: idx - delim_len]
            start, pos = idx + 1, 0
            splits += 1
            if max_split and splits >= max_split:
                break
        yield expr[start:]

    @classmethod
    def _separate_at_paren(cls, expr, delim=None):
        if delim is None:
            delim = expr and _MATCHING_PARENS[expr[0]]
        separated = list(cls._separate(expr, delim, 1))
        if len(separated) < 2:
            raise cls.Exception(f'No terminating paren {delim}', expr)
        return separated[0][1:].strip(), separated[1].strip()

    def _operator(self, op, left_val, right_expr, expr, local_vars, allow_recursion):
        if op in ('||', '&&'):
            if (op == '&&') ^ _js_ternary(left_val):
                return left_val  # short circuiting
        elif op == '??':
            if left_val not in (None, JS_Undefined):
                return left_val
        elif op == '?':
            right_expr = _js_ternary(
                left_val, *self._separate(right_expr, ':', 1))

        right_val = self.interpret_expression(
            right_expr, local_vars, allow_recursion)
        if not _OPERATORS.get(op):
            return right_val

        try:
            return _OPERATORS[op](left_val, right_val)
        except Exception as e:
            raise self.Exception(f'Failed to evaluate {left_val!r} '
                                 f'{op} {right_val!r}', expr, cause=e)

    def _index(self, obj, idx, allow_undefined=False):
        if idx == 'length':
            return len(obj)
        try:
            return obj[int(idx)] if isinstance(obj, list) else obj[idx]
        except Exception as e:
            if allow_undefined:
                return JS_Undefined
            raise self.Exception(f'Cannot get index {idx}', repr(obj), cause=e)

    def _dump(self, obj, namespace):
        try:
            return json.dumps(obj)
        except TypeError:
            return self._named_object(namespace, obj)

    # @Debugger.wrap_interpreter
    def interpret_statement(self, stmt, local_vars, allow_recursion=100):
        if allow_recursion < 0:
            raise self.Exception('Recursion limit reached')
        allow_recursion -= 1

        should_return = False
        sub_statements = list(self._separate(stmt, ';')) or ['']
        expr = stmt = sub_statements.pop().strip()

        for sub_stmt in sub_statements:
            ret, should_return = self.interpret_statement(
                sub_stmt, local_vars, allow_recursion)
            if should_return:
                return ret, should_return

        m = re.match(
            r'(?P<var>(?:var|const|let)\s)|return(?:\s+|(?=["\'])|$)|(?P<throw>throw\s+)', stmt)
        if m:
            expr = stmt[len(m.group(0)):].strip()
            if m.group('throw'):
                raise JS_Throw(self.interpret_expression(
                    expr, local_vars, allow_recursion))
            should_return = not m.group('var')
        if not expr:
            return None, should_return

        if expr[0] in _QUOTES:
            inner, outer = self._separate(expr, expr[0], 1)
            if expr[0] == '/':
                flags, outer = self._regex_flags(outer)
                # We don't support regex methods yet, so no point compiling it
                inner = f'{inner}/{flags}'
                # Avoid https://github.com/python/cpython/issues/74534
                # inner = re.compile(inner[1:].replace('[[', r'[\['), flags=flags)
            else:
                inner = json.loads(js_to_json(
                    f'{inner}{expr[0]}', strict=True))
            if not outer:
                return inner, should_return
            expr = self._named_object(local_vars, inner) + outer

        if expr.startswith('new '):
            obj = expr[4:]
            if obj.startswith('Date('):
                left, right = self._separate_at_paren(obj[4:])
                date = unified_timestamp(
                    self.interpret_expression(left, local_vars, allow_recursion), False)
                if date is None:
                    raise self.Exception(
                        f'Failed to parse date {left!r}', expr)
                expr = self._dump(int(date * 1000), local_vars) + right
            else:
                raise self.Exception(f'Unsupported object {obj}', expr)

        if expr.startswith('void '):
            left = self.interpret_expression(
                expr[5:], local_vars, allow_recursion)
            return None, should_return

        if expr.startswith('{'):
            inner, outer = self._separate_at_paren(expr)
            # try for object expression (Map)
            sub_expressions = [list(self._separate(sub_expr.strip(), ':', 1))
                               for sub_expr in self._separate(inner)]
            if all(len(sub_expr) == 2 for sub_expr in sub_expressions):
                def dict_item(key, val):
                    val = self.interpret_expression(
                        val, local_vars, allow_recursion)
                    if re.match(_NAME_RE, key):
                        return key, val
                    return self.interpret_expression(key, local_vars, allow_recursion), val

                return dict(dict_item(k, v) for k, v in sub_expressions), should_return

            inner, should_abort = self.interpret_statement(
                inner, local_vars, allow_recursion)
            if not outer or should_abort:
                return inner, should_abort or should_return

            expr = self._dump(inner, local_vars) + outer

        if expr.startswith('('):
            inner, outer = self._separate_at_paren(expr)
            inner, should_abort = self.interpret_statement(
                inner, local_vars, allow_recursion)
            if not outer or should_abort:
                return inner, should_abort or should_return

            expr = self._dump(inner, local_vars) + outer

        if expr.startswith('['):
            inner, outer = self._separate_at_paren(expr)
            name = self._named_object(local_vars, [
                self.interpret_expression(item, local_vars, allow_recursion)
                for item in self._separate(inner)])
            expr = name + outer

        m = re.match(r'''(?x)
                (?P<try>try)\s*\{|
                (?P<if>if)\s*\(|
                (?P<switch>switch)\s*\(|
                (?P<for>for)\s*\(
                ''', expr)
        md = m.groupdict() if m else {}
        if md.get('if'):
            cndn, expr = self._separate_at_paren(expr[m.end() - 1:])
            if_expr, expr = self._separate_at_paren(expr.lstrip())
            # TODO: "else if" is not handled
            else_expr = None
            m = re.match(r'else\s*{', expr)
            if m:
                else_expr, expr = self._separate_at_paren(expr[m.end() - 1:])
            cndn = _js_ternary(self.interpret_expression(
                cndn, local_vars, allow_recursion))
            ret, should_abort = self.interpret_statement(
                if_expr if cndn else else_expr, local_vars, allow_recursion)
            if should_abort:
                return ret, True

        if md.get('try'):
            try_expr, expr = self._separate_at_paren(expr[m.end() - 1:])
            err = None
            try:
                ret, should_abort = self.interpret_statement(
                    try_expr, local_vars, allow_recursion)
                if should_abort:
                    return ret, True
            except Exception as e:
                # XXX: This works for now, but makes debugging future issues very hard
                err = e

            pending = (None, False)
            m = re.match(fr'catch\s*(?P<err>\(\s*{_NAME_RE}\s*\))?\{{', expr)
            if m:
                sub_expr, expr = self._separate_at_paren(expr[m.end() - 1:])
                if err:
                    catch_vars = {}
                    if m.group('err'):
                        catch_vars[m.group('err')] = err.error if isinstance(
                            err, JS_Throw) else err
                    catch_vars = local_vars.new_child(catch_vars)
                    err, pending = None, self.interpret_statement(
                        sub_expr, catch_vars, allow_recursion)

            m = re.match(r'finally\s*\{', expr)
            if m:
                sub_expr, expr = self._separate_at_paren(expr[m.end() - 1:])
                ret, should_abort = self.interpret_statement(
                    sub_expr, local_vars, allow_recursion)
                if should_abort:
                    return ret, True

            ret, should_abort = pending
            if should_abort:
                return ret, True

            if err:
                raise err

        elif md.get('for'):
            constructor, remaining = self._separate_at_paren(
                expr[m.end() - 1:])
            if remaining.startswith('{'):
                body, expr = self._separate_at_paren(remaining)
            else:
                switch_m = re.match(r'switch\s*\(', remaining)  # FIXME
                if switch_m:
                    switch_val, remaining = self._separate_at_paren(
                        remaining[switch_m.end() - 1:])
                    body, expr = self._separate_at_paren(remaining, '}')
                    body = 'switch(%s){%s}' % (switch_val, body)
                else:
                    body, expr = remaining, ''
            start, cndn, increment = self._separate(constructor, ';')
            self.interpret_expression(start, local_vars, allow_recursion)
            while True:
                if not _js_ternary(self.interpret_expression(cndn, local_vars, allow_recursion)):
                    break
                try:
                    ret, should_abort = self.interpret_statement(
                        body, local_vars, allow_recursion)
                    if should_abort:
                        return ret, True
                except JS_Break:
                    break
                except JS_Continue:
                    pass
                self.interpret_expression(
                    increment, local_vars, allow_recursion)

        elif md.get('switch'):
            switch_val, remaining = self._separate_at_paren(expr[m.end() - 1:])
            switch_val = self.interpret_expression(
                switch_val, local_vars, allow_recursion)
            body, expr = self._separate_at_paren(remaining, '}')
            items = body.replace(
                'default:', 'case default:').split('case ')[1:]
            for default in (False, True):
                matched = False
                for item in items:
                    case, stmt = (i.strip()
                                  for i in self._separate(item, ':', 1))
                    if default:
                        matched = matched or case == 'default'
                    elif not matched:
                        matched = (case != 'default'
                                   and switch_val == self.interpret_expression(case, local_vars, allow_recursion))
                    if not matched:
                        continue
                    try:
                        ret, should_abort = self.interpret_statement(
                            stmt, local_vars, allow_recursion)
                        if should_abort:
                            return ret
                    except JS_Break:
                        break
                if matched:
                    break

        if md:
            ret, should_abort = self.interpret_statement(
                expr, local_vars, allow_recursion)
            return ret, should_abort or should_return

        # Comma separated statements
        sub_expressions = list(self._separate(expr))
        if len(sub_expressions) > 1:
            for sub_expr in sub_expressions:
                ret, should_abort = self.interpret_statement(
                    sub_expr, local_vars, allow_recursion)
                if should_abort:
                    return ret, True
            return ret, False

        r = rf'''(?x)
                (?P<pre_sign>\+\+|--)(?P<var1>{_NAME_RE})|
                (?P<var2>{_NAME_RE})(?P<post_sign>\+\+|--)'''
        for m in re.finditer(r, expr):
            var = m.group('var1') or m.group('var2')
            start, end = m.span()
            sign = m.group('pre_sign') or m.group('post_sign')
            ret = local_vars[var]
            local_vars[var] += 1 if sign[0] == '+' else -1
            if m.group('pre_sign'):
                ret = local_vars[var]
            expr = expr[:start] + self._dump(ret, local_vars) + expr[end:]

        if not expr:
            return None, should_return

        reg = fr'''(?x)
            (?P<assign>
                (?P<out>{_NAME_RE})(?:\[(?P<index>[^\]]+?)\])?\s*
                (?P<op>{"|".join(map(re.escape, set(_OPERATORS) - _COMP_OPERATORS))})?
                =(?!=)(?P<expr>.*)$
            )|(?P<return>
                (?!if|return|true|false|null|undefined|NaN)(?P<name>{_NAME_RE})$
            )|(?P<indexing>
                (?P<in>{_NAME_RE})\[(?P<idx>.+)\]$
            )|(?P<attribute>
                (?P<var>{_NAME_RE})(?:(?P<nullish>\?)?\.(?P<member>[^(]+)|\[(?P<member2>[^\]]+)\])\s*
            )|(?P<function>
                (?P<fname>{_NAME_RE})\((?P<args>.*)\)$
            )'''
        m = re.match(reg, expr)
        if m and m.group('assign'):
            out = m.group('out')
            left_val = local_vars.get(out)

            if not m.group('index'):
                local_vars[m.group('out')] = self._operator(
                    m.group('op'), left_val, m.group('expr'), expr, local_vars, allow_recursion)
                return local_vars[m.group('out')], should_return
            if left_val in (None, JS_Undefined):
                raise self.Exception(f'Cannot index undefined variable {
                                     m.group("out")}', expr)

            idx = self.interpret_expression(
                m.group('index'), local_vars, allow_recursion)
            if not isinstance(idx, (int, float)):
                raise self.Exception(f'List index {idx} must be integer', expr)
            idx = int(idx)
            left_val[idx] = self._operator(
                m.group('op'), self._index(left_val, idx), m.group('expr'),
                expr, local_vars, allow_recursion)
            return left_val[idx], should_return

        if expr.isdigit():
            return int(expr), should_return

        if expr == 'break':
            raise JS_Break()
        if expr == 'continue':
            raise JS_Continue()
        if expr == 'undefined':
            return JS_Undefined, should_return
        if expr == 'NaN':
            return float('NaN'), should_return

        if m and m.group('return'):
            return local_vars.get(m.group('name'), JS_Undefined), should_return

        with contextlib.suppress(ValueError):
            return json.loads(js_to_json(expr, strict=True)), should_return

        if m and m.group('indexing'):
            val = local_vars[m.group('in')]
            idx = self.interpret_expression(
                m.group('idx'), local_vars, allow_recursion)
            return self._index(val, idx), should_return

        for op in _OPERATORS:
            separated = list(self._separate(expr, op))
            right_expr = separated.pop()
            while True:
                if op in '?<>*-' and len(separated) > 1 and not separated[-1].strip():
                    separated.pop()
                elif not (separated and op == '?' and right_expr.startswith('.')):
                    break
                right_expr = f'{op}{right_expr}'
                if op != '-':
                    right_expr = f'{separated.pop()}{op}{right_expr}'
            if not separated:
                continue
            left_val = self.interpret_expression(
                op.join(separated), local_vars, allow_recursion)
            return self._operator(op, left_val, right_expr, expr, local_vars,
                                  allow_recursion), should_return

        if m and m.group('attribute'):
            variable, member, nullish = m.group('var', 'member', 'nullish')
            if not member:
                member = self.interpret_expression(
                    m.group('member2'), local_vars, allow_recursion)
            arg_str = expr[m.end():]
            if arg_str.startswith('('):
                arg_str, remaining = self._separate_at_paren(arg_str)
            else:
                arg_str, remaining = None, arg_str

            def assertion(cndn, msg):
                """ assert, but without risk of getting optimized out """
                if not cndn:
                    raise self.Exception(f'{member} {msg}', expr)

            def eval_method():
                nonlocal member
                types = {
                    'String': str,
                    'Math': float,
                    'Array': list,
                }
                obj = local_vars.get(variable, types.get(variable, NO_DEFAULT))
                if obj is NO_DEFAULT:
                    if variable not in self._objects:
                        try:
                            self._objects[variable] = self.extract_object(
                                variable)
                        except self.Exception:
                            if not nullish:
                                raise
                    obj = self._objects.get(variable, JS_Undefined)

                if nullish and obj is JS_Undefined:
                    return JS_Undefined

                # Member access
                if arg_str is None:
                    return self._index(obj, member, nullish)

                # Function call
                argvals = [
                    self.interpret_expression(v, local_vars, allow_recursion)
                    for v in self._separate(arg_str)]

                # Fixup prototype call
                # https://github.com/yt-dlp/yt-dlp/commit/6c056ea7aeb03660281653a9668547f2548f194f
                if isinstance(obj, type) and member.startswith('prototype.'):
                    new_member, _, func_prototype = member.partition('.')[
                        2].partition('.')
                    assertion(argvals, 'takes one or more arguments')
                    assertion(isinstance(
                        argvals[0], obj), f'needs binding to type {obj}')
                    if func_prototype == 'call':
                        obj, *argvals = argvals
                    elif func_prototype == 'apply':
                        assertion(len(argvals) == 2, 'takes two arguments')
                        obj, argvals = argvals
                        assertion(isinstance(argvals, list),
                                  'second argument needs to be a list')
                    else:
                        raise self.Exception(f'Unsupported Function method {
                                             func_prototype}', expr)
                    member = new_member

                if obj == str:
                    if member == 'fromCharCode':
                        assertion(argvals, 'takes one or more arguments')
                        return ''.join(map(chr, argvals))
                    raise self.Exception(
                        f'Unsupported String method {member}', expr)
                if obj == float:
                    if member == 'pow':
                        assertion(len(argvals) == 2, 'takes two arguments')
                        return argvals[0] ** argvals[1]
                    raise self.Exception(
                        f'Unsupported Math method {member}', expr)

                if member == 'split':
                    assertion(argvals, 'takes one or more arguments')
                    assertion(len(argvals) == 1,
                              'with limit argument is not implemented')
                    return obj.split(argvals[0]) if argvals[0] else list(obj)
                if member == 'join':
                    assertion(isinstance(obj, list),
                              'must be applied on a list')
                    assertion(len(argvals) == 1, 'takes exactly one argument')
                    return argvals[0].join(obj)
                if member == 'reverse':
                    assertion(not argvals, 'does not take any arguments')
                    obj.reverse()
                    return obj
                if member == 'slice':
                    assertion(isinstance(obj, (list, str)),
                              'must be applied on a list or string')
                    assertion(len(argvals) <= 2,
                              'takes between 0 and 2 arguments')
                    return obj[slice(*argvals, None)]
                if member == 'splice':
                    assertion(isinstance(obj, list),
                              'must be applied on a list')
                    assertion(argvals, 'takes one or more arguments')
                    index, howMany = map(int, (argvals + [len(obj)])[:2])
                    if index < 0:
                        index += len(obj)
                    add_items = argvals[2:]
                    res = []
                    for i in range(index, min(index + howMany, len(obj))):
                        res.append(obj.pop(index))
                    for i, item in enumerate(add_items):
                        obj.insert(index + i, item)
                    return res
                if member == 'unshift':
                    assertion(isinstance(obj, list),
                              'must be applied on a list')
                    assertion(argvals, 'takes one or more arguments')
                    for item in reversed(argvals):
                        obj.insert(0, item)
                    return obj
                if member == 'pop':
                    assertion(isinstance(obj, list),
                              'must be applied on a list')
                    assertion(not argvals, 'does not take any arguments')
                    if not obj:
                        return
                    return obj.pop()
                if member == 'push':
                    assertion(argvals, 'takes one or more arguments')
                    obj.extend(argvals)
                    return obj
                if member == 'forEach':
                    assertion(argvals, 'takes one or more arguments')
                    assertion(len(argvals) <= 2, 'takes at-most 2 arguments')
                    f, this = (argvals + [''])[:2]
                    return [f((item, idx, obj), {'this': this}, allow_recursion) for idx, item in enumerate(obj)]
                if member == 'indexOf':
                    assertion(argvals, 'takes one or more arguments')
                    assertion(len(argvals) <= 2, 'takes at-most 2 arguments')
                    idx, start = (argvals + [0])[:2]
                    try:
                        return obj.index(idx, start)
                    except ValueError:
                        return -1
                if member == 'charCodeAt':
                    assertion(isinstance(obj, str),
                              'must be applied on a string')
                    assertion(len(argvals) == 1, 'takes exactly one argument')
                    idx = argvals[0] if isinstance(argvals[0], int) else 0
                    if idx >= len(obj):
                        return None
                    return ord(obj[idx])

                idx = int(member) if isinstance(obj, list) else member
                return obj[idx](argvals, allow_recursion=allow_recursion)

            if remaining:
                ret, should_abort = self.interpret_statement(
                    self._named_object(local_vars, eval_method()) + remaining,
                    local_vars, allow_recursion)
                return ret, should_return or should_abort

            return eval_method(), should_return

        if m and m.group('function'):
            fname = m.group('fname')
            argvals = [self.interpret_expression(v, local_vars, allow_recursion)
                       for v in self._separate(m.group('args'))]
            if fname in local_vars:
                return local_vars[fname](argvals, allow_recursion=allow_recursion), should_return
            if fname not in self._functions:
                self._functions[fname] = self.extract_function(fname)
            return self._functions[fname](argvals, allow_recursion=allow_recursion), should_return

        raise self.Exception(
            f'Unsupported JS expression {truncate_string(expr, 20, 20) if expr != stmt else ""}', stmt)

    def interpret_expression(self, expr, local_vars, allow_recursion):
        ret, should_return = self.interpret_statement(
            expr, local_vars, allow_recursion)
        if should_return:
            raise self.Exception('Cannot return from an expression', expr)
        return ret

    def extract_object(self, objname):
        _FUNC_NAME_RE = r'''(?:[a-zA-Z$0-9]+|"[a-zA-Z$0-9]+"|'[a-zA-Z$0-9]+')'''
        obj = {}
        obj_m = re.search(
            r'''(?x)
                (?<!\.)%s\s*=\s*{\s*
                    (?P<fields>(%s\s*:\s*function\s*\(.*?\)\s*{.*?}(?:,\s*)?)*)
                }\s*;
            ''' % (re.escape(objname), _FUNC_NAME_RE),
            self.code)
        if not obj_m:
            raise self.Exception(f'Could not find object {objname}')
        fields = obj_m.group('fields')
        # Currently, it only supports function definitions
        r = r'''(?x)
                (?P<key>%s)\s*:\s*function\s*\((?P<args>(?:%s|,)*)\){(?P<code>[^}]+)}
            ''' % (_FUNC_NAME_RE, _NAME_RE)
        fields_m = re.finditer(r, fields)
        for f in fields_m:
            argnames = f.group('args').split(',')
            name = remove_quotes(f.group('key'))
            obj[name] = function_with_repr(self.build_function(
                argnames, f.group('code')), f'F<{name}>')

        return obj

    def extract_function_code(self, funcname):
        """ @returns argnames, code """
        func_m = re.search(
            r'''(?xs)
                (?:
                    function\s+%(name)s|
                    [{;,]\s*%(name)s\s*=\s*function|
                    (?:var|const|let)\s+%(name)s\s*=\s*function
                )\s*
                \((?P<args>[^)]*)\)\s*
                (?P<code>{.+})''' % {'name': re.escape(funcname)},
            self.code)
        if func_m is None:
            raise self.Exception(f'Could not find JS function "{funcname}"')
        code, _ = self._separate_at_paren(func_m.group('code'))
        return [x.strip() for x in func_m.group('args').split(',')], code

    def extract_function(self, funcname):
        return function_with_repr(
            self.extract_function_from_code(
                *self.extract_function_code(funcname)),
            f'F<{funcname}>')

    def extract_function_from_code(self, argnames, code, *global_stack):
        local_vars = {}
        while True:
            mobj = re.search(r'function\((?P<args>[^)]*)\)\s*{', code)
            if mobj is None:
                break
            start, body_start = mobj.span()
            body, remaining = self._separate_at_paren(code[body_start - 1:])
            name = self._named_object(local_vars, self.extract_function_from_code(
                [x.strip() for x in mobj.group('args').split(',')],
                body, local_vars, *global_stack))
            code = code[:start] + name + remaining
        return self.build_function(argnames, code, local_vars, *global_stack)

    def call_function(self, funcname, *args):
        return self.extract_function(funcname)(args)

    def build_function(self, argnames, code, *global_stack):
        global_stack = list(global_stack) or [{}]
        argnames = tuple(argnames)

        def resf(args, kwargs={}, allow_recursion=100):
            global_stack[0].update(itertools.zip_longest(
                argnames, args, fillvalue=None))
            global_stack[0].update(kwargs)
            var_stack = LocalNameSpace(*global_stack)
            ret, should_abort = self.interpret_statement(
                code.replace('\n', ' '), var_stack, allow_recursion - 1)
            if should_abort:
                return ret

        return resf
