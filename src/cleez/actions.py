from argparse import (
    _AppendAction,
    _AppendConstAction,
    _CountAction,
    _ExtendAction,
    _HelpAction,
    _StoreAction,
    _StoreConstAction,
    _StoreFalseAction,
    _StoreTrueAction,
    _SubParsersAction,
    _VersionAction,
)

STORE = _StoreAction
STORE_CONST = _StoreConstAction
STORE_TRUE = store_true = _StoreTrueAction
STORE_FALSE = _StoreFalseAction
APPEND = _AppendAction
APPEND_CONST = _AppendConstAction
COUNT = _CountAction
HELP = _HelpAction
VERSION = _VersionAction
PARSERS = _SubParsersAction
EXTEND = _ExtendAction
