import pytest

from pytubefix import cipher
from pytubefix.exceptions import RegexMatchError


def test_get_initial_function_name_with_no_match_should_error():
    with pytest.raises(RegexMatchError):
        cipher.get_initial_function_name("asdf")


def test_js_splice():
    mapping = {

    }
    for args, result in mapping.items():
        a = [1, 2, 3, 4]
        assert cipher.js_splice(a, *args) == result


def test_get_throttling_function_name(base_js):
    base_js_code_fragments = [
        # Values expected as of 2022/02/04:
        {
            'raw_var': r'var Apa=[hha]',
            'raw_code': r'a.url="";a.C&&(b=a.get("n"))&&(b=Apa[0](b),a.set("n",b),' \
                        r'Apa.length||hha(""))}};',
            'nfunc_name': 'hha'
        },
        # Values expected as of 2022/04/15:
        {
            'raw_var': r'var $x=[uq]',
            'raw_code': r'a.url="";a.D&&(b=a.get("n"))&&(b=$x[0](b),a.set("n",b),' \
                        r'$x.length||uq(""))',
            'nfunc_name': 'uq'
        }
    ]
    for code_fragment, base_js_file in zip(base_js_code_fragments, base_js):
        assert code_fragment['raw_var'] in base_js_file
        assert code_fragment['raw_code'] in base_js_file
        func_name = cipher.get_throttling_function_name(base_js_file)
        assert func_name == code_fragment['nfunc_name']
