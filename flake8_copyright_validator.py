import difflib
import re
from typing import List, Optional, Tuple

import importlib_metadata

from error_messages import COPYRIGHT_LENGTH_MISMATCH, COPYRIGHT_PLAIN_NOT_FOUND, COPYRIGHT_REGEX_MISMATCH


class CopyrightValidator:
    name = __name__
    version = importlib_metadata.version(__name__)
    copyright_text_list: List[str] = []
    copyright_regex_list: List[str] = []
    detailed_output: bool = False
    update: bool = False
    copyright_text: Optional[str] = None
    bytes_to_read: int = 2048
    lines_to_exclude: List[str] = []
    symbols_to_replace = ["'"]

    def __init__(self, tree, filename) -> None:
        self._tree = tree
        self._filename = filename

    @classmethod
    def add_options(cls, parser):
        parser.add_option(
            '--copyright-text',
            help='a text to look for in files',
            parse_from_config=True,
        )
        parser.add_option(
            '--copyright-regex',
            help='a text to look for in files',
            parse_from_config=True,
        )
        parser.add_option(
            '--update',
            help='defines if files should be updated with provided copyright text',
            action='store_true'
        )
        parser.add_option(
            '--detailed-output',
            help='provides detailed output',
            action='store_true',
            parse_from_config=True,
        )
        parser.add_option(
            '--bytes-to-read',
            type=int,
            help='number of bytes to read',
            parse_from_config=True,
        )
        parser.add_option(
            '--lines-to-exclude',
            help='exclude file if line from list found as first line',
            parse_from_config=True,
        )
        parser.add_option(
            '--symbols-to-replace',
            comma_separated_list=True,
            help='symbols you wrap your copyright text with that will be replaced',
            parse_from_config=True,
        )

    @classmethod
    def parse_options(cls, manager, options, files):
        cls.detailed_output = options.detailed_output
        cls.update = options.update
        if options.symbols_to_replace:
            cls.symbols_to_replace = options.symbols_to_replace
        if options.lines_to_exclude:
            cls.lines_to_exclude = cls._parse_lines(options.lines_to_exclude, cls.symbols_to_replace)
        if options.copyright_text:
            cls.copyright_text_list = cls._parse_lines(options.copyright_text, cls.symbols_to_replace)
            cls.copyright_text = '\n'.join(cls.copyright_text_list)
        if options.copyright_regex:
            cls.copyright_regex_list = cls._parse_lines(options.copyright_regex, cls.symbols_to_replace)
        if options.bytes_to_read:
            cls.bytes_to_read = options.bytes_to_read

    def run(self):
        with open(self._filename, 'r+') as w:
            content = w.read() if self.update else w.read(self.bytes_to_read)
            lines = content.split('\n')
            if not lines:
                return
            for excluded_line in self.lines_to_exclude:
                if lines[0].startswith(excluded_line):
                    return
            if self.copyright_regex_list:
                err_msg, err_idx = self._validate_via_regex(lines)
            else:
                err_msg, err_idx = self._validate_text_plain(lines)
            if err_msg:
                self._add_copyright(w, content)
                yield err_idx, 0, err_msg, type(self)
            return

    @staticmethod
    def _parse_lines(lines_from_options, symbols_to_replace=None) -> List[str]:
        if not symbols_to_replace:
            symbols_to_replace = []
        for symbol_to_replace in symbols_to_replace:
            lines_from_options = lines_from_options.replace(symbol_to_replace, '')
        lines = lines_from_options.split('\n')
        lines.remove('')
        return lines

    def _validate_via_regex(self, lines_to_validate: List[str]) -> Tuple[Optional[str], int]:
        if len(self.copyright_regex_list) > len(lines_to_validate):
            return COPYRIGHT_LENGTH_MISMATCH, 0
        for line_idx, validation_pair in enumerate(zip(lines_to_validate, self.copyright_regex_list), start=1):
            line_to_validate, regex = validation_pair
            if not re.search(regex, line_to_validate):
                return COPYRIGHT_REGEX_MISMATCH, line_idx
        return None, 0

    def _validate_text_plain(self, lines_to_validate: List[str]) -> Tuple[Optional[str], int]:
        copyright_len = len(self.copyright_text_list)
        if lines_to_validate[0:copyright_len] != self.copyright_text_list:
            diff = '\n'.join(
                [line for line in difflib.unified_diff(self.copyright_text_list, lines_to_validate[0:copyright_len])]
            )
            return COPYRIGHT_PLAIN_NOT_FOUND.format(details=diff if self.detailed_output else ''), 0
        return None, 0

    def _add_copyright(self, file, content: str) -> None:
        if not self.update:
            return
        if not self.copyright_text:
            raise TypeError('Provide --copyright-text parameter to add at the beginning of validated files')
        content = self.copyright_text + '\n' + content
        file.seek(0)
        file.write(content)
