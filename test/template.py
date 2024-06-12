"""
Tests for HTML formatting utilities.

Copyright 2017-2020 ICTU
Copyright 2017-2022 Leiden University
Copyright 2017-2024 Leon Helwerda

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

import unittest
from server.template import Template

class TemplateTest(unittest.TestCase):
    """
    Test for formatter which supports HTML encoding and URL encoding.
    """

    def test_format(self) -> None:
        """
        Test formatting a template using conversion fields.
        """

        template = Template()
        self.assertEqual(template.format("<span>{username!h}</span>",
                                         username="<script>evil();</script>"),
                         "<span>&lt;script&gt;evil();&lt;/script&gt;</span>")
        self.assertEqual(template.format('<a href="{page!u}">Go</a>',
                                         page='ha" onclick="evil();'),
                         '<a href="ha%22%20onclick%3D%22evil%28%29%3B">Go</a>')
        self.assertEqual(template.format('This is {number!s}',
                                         number=123.456),
                         'This is 123.456')
