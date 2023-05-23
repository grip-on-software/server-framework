"""
HTML formatting utilities.

Copyright 2017-2020 ICTU
Copyright 2017-2022 Leiden University
Copyright 2017-2023 Leon Helwerda

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from html import escape
import string
from typing import Any
from urllib.parse import quote

class Template(string.Formatter):
    """
    Formatter object which supports HTML encoding using the 'h' conversion
    type and URL encoding using the 'u' conversion type.
    """

    def convert_field(self, value: Any, conversion: str) -> Any:
        if conversion == 'h':
            return escape(value)
        if conversion == 'u':
            return quote(value)

        return super().convert_field(value, conversion)
