from __future__ import absolute_import
from udsoncan import DataIdentifier, Routine, Units
from test.UdsTest import UdsTest

class TestDefinitions(UdsTest):
    def test_data_identifier_name_from_id(self):
        for i in xrange(0x10000):
            name = DataIdentifier.name_from_id(i)
            self.assertTrue(isinstance(name, unicode))

    def test_routine_name_from_id(self):
        for i in xrange(0x10000):
            name = Routine.name_from_id(i)
            self.assertTrue(isinstance(name, unicode))

