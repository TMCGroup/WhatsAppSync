from django.test import TestCase

__author__ = 'kenneth'


class DumbTest(TestCase):
    def test_one_plus_one(self):
        self.assertEquals(1+1, 2)