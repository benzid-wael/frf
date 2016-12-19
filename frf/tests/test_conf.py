# Copyright 2016 by Teem, and other contributors,
# as noted in the individual source code files.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By contributing to this project, you agree to also license your source
# code under the terms of the Apache License, Version 2.0, as described
# above.

import unittest
import os

from frf._conf import Conf


class TestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.conf = Conf(
            'frf.tests.fakeproject.settings', os.path.dirname(__file__))

    def test_access_setting_via_dict(self):
        self.assertEqual(
            self.conf['TIMEZONE'], 'US/Mountain')

    def test_access_via_property(self):
        self.assertEqual(
            self.conf.TIMEZONE, 'US/Mountain')

    def test_set_via_property(self):
        self.conf.WOOT = True

        self.assertTrue(self.conf['WOOT'])

    def test_fail_file_not_found(self):
        with self.assertRaises(ImportError):
            Conf('thissettingsfile.should.not.exist')

    def test_get_path_of_file(self):
        self.assertIn(
            'frf/tests/test_conf.py', self.conf.pathof('test_conf.py'))
