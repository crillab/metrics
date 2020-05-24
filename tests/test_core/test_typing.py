import unittest

from metrics.core.builder.attribute_manager import AttributeManagerSet
from metrics.core.builder.typing_strategy import TypingStrategyEnum


class MyTestCase(unittest.TestCase):

    def test_integer(self):
        ati = TypingStrategyEnum.INTEGER

        self.assertTrue(ati.verify('12'))
        self.assertTrue(ati.verify('-22'))

        self.assertEqual(0, ati.parse('0'))

    def test_float(self):
        atf = TypingStrategyEnum.FLOAT

        self.assertTrue(atf.verify('12'))
        self.assertTrue(atf.verify('-22'))

        self.assertEqual(0, atf.parse('0'))

        self.assertTrue(atf.verify('12.1'))
        self.assertTrue(atf.verify('-22E+1'))

        self.assertEqual(0.5, atf.parse('0.5'))

    def test_attr_set_float(self):
        float_list = ['1', '2.0', '3']
        a_set = AttributeManagerSet()
        float_list_checker = a_set.add_attribute_manager_for_typing_finder('float_list', is_list=True)

        for e in float_list:
            float_list_checker.verify(e)

        parsed = [float_list_checker.parse(e) for e in float_list]

        self.assertEqual([1.0, 2.0, 3.0], parsed)

    def test_attr_set_integer(self):
        int_list = ['1', '2', '3']
        a_set = AttributeManagerSet()
        int_list_checker = a_set.add_attribute_manager_for_typing_finder('int_list', is_list=True)

        for e in int_list:
            int_list_checker.verify(e)

        parsed = [int_list_checker.parse(e) for e in int_list]

        self.assertEqual([1, 2, 3], parsed)

    def test_attr_set_integer(self):
        str_list = ['1', '2', 'lol']
        a_set = AttributeManagerSet()
        str_list_checker = a_set.add_attribute_manager_for_typing_finder('str_list', is_list=True)

        for e in str_list:
            str_list_checker.verify(e)

        parsed = [str_list_checker.parse(e) for e in str_list]

        self.assertEqual(str_list, parsed)


if __name__ == '__main__':
    unittest.main()
