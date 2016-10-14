"""
/***************************************************************************
Name                 : ProfileTenureViewTest
Description          : Test for ProfileTenureView widget.
Date                 : 10/October/2016
copyright            : John Kahiu
email                : gkahiu at gmail dot com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import sys
import unittest
from unittest import TestCase

from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest

from profile_tenure_view import ProfileTenureView

app = QApplication(sys.argv)


class TestProfileTenureView(TestCase):
    def setUp(self):
        self.tenure_view = ProfileTenureView()

    def test_profile(self):
        self.fail()

    def test_save_tenure_view(self):
        self.fail()

if __name__ == "__main__":
    unittest.main()