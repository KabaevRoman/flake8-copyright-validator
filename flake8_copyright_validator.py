import difflib
from typing import List, Tuple

import importlib_metadata


class CopyrightValidator:
    name = __name__
    version = importlib_metadata.version(__name__)
    copyright_text_list: List[str] = None
    custom_escape_sequences: List[Tuple[str, str]] = None
    detailed_output: bool = False
    update: bool = False
    copyright_text: str = None
    bytes_to_read: int = 2048
    lines_to_exclude = []
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
            '--update',
            help='defines if files should be updated with provided copyright text',
            action='store_true'
        )
        parser.add_option(
            '--detailed-output',
            help='provides detailed output',
            action='store_true'
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
    def parse_options(cls, options):
        cls.detailed_output = options.detailed_output
        cls.update = options.update
        if options.symbols_to_replace:
            cls.symbols_to_replace = options.symbols_to_replace
        if options.lines_to_exclude:
            cls.lines_to_exclude = cls._parse_lines(options.lines_to_exclude, cls.symbols_to_replace)
        cls.copyright_text_list = cls._parse_lines(options.copyright_text, cls.symbols_to_replace)
        cls.copyright_text = '\n'.join(cls.copyright_text_list)

        if options.bytes_to_read:
            cls.bytes_to_read = options.bytes_to_read

    def run(self):
        license_lines = self.copyright_text_list
        diff = None
        with open(self._filename, 'r+') as w:
            if self.update:
                content = w.read()
            else:
                content = w.read(self.bytes_to_read)
            lines = content.split('\n')
            if not lines:
                return
            for excluded_line in self.lines_to_exclude:
                if lines[0].startswith(excluded_line):
                    return
            if lines[0:len(license_lines)] != license_lines:
                diff = '\n'.join([line for line in difflib.unified_diff(license_lines, lines[0:len(license_lines)])])
                err_msg = f'NCF100 No copyright found\n{diff if self.detailed_output else ""}'
                yield 1, 0, err_msg, type(self)
            if self.update and diff:
                content = self.copyright_text + '\n' + content
                w.seek(0)
                w.write(content)

    @staticmethod
    def _parse_lines(lines_from_options, symbols_to_replace=None) -> List[str]:
        if not symbols_to_replace:
            symbols_to_replace = []
        for symbol_to_replace in symbols_to_replace:
            lines_from_options = lines_from_options.replace(symbol_to_replace, '')
        lines = lines_from_options.split('\n')
        lines.remove('')
        return lines
