#!/usr/bin/env python3
"""
Escape Markdown chars
"""


def escape_markdown(text: str) -> str:
    """
    Escape Markdown chars
    """
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + char if char in escape_chars else char for char in text])
