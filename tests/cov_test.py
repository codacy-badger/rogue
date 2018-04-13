#!/usr/bin/env python3

import pyrogue
import rogue
import unittest

class myDevice(pyrogue.Device):
    def __init__(self, name="myDevice", description='My device', **kargs):
        super().__init__(name=name, description=description, **kargs)

        self.add(pyrogue.LocalVariable(
            name='var',
            value=3.14,
            mode='RW'))

        self.add(pyrogue.LinkVariable(
            name='var_link',
            mode='RW',
            linkedSet=self.set_val,
            linkedGet=self.get_val,
            dependencies=[self.var]))

    @staticmethod
    def set_val(dev, var, value):
        var.dependencies[0].set(value)

    @staticmethod
    def get_val(var):
        return var.dependencies[0].value()

class LocalRoot(pyrogue.Root):
    def __init__(self):
        pyrogue.Root.__init__(self, name='LocalRoot', description='Local root')
        my_device = myDevice()
        self.add(my_device)

class Root(unittest.TestCase):
    """
    Test Pyrogue
    """

    def test_pyrogue_loc_var(self):
        # Test read
        root = LocalRoot()
        root.start()
        result = root.myDevice.var.get()
        self.assertEqual(result, 3.14)

        # Test write
        root.myDevice.var.set(123)
        result = root.myDevice.var.get()
        self.assertEqual(result, 123)

        root.stop()

    def test_pyrogue_link_var(self):
        # Test read
        root = LocalRoot()
        root.start()
        result = root.myDevice.var_link.get()
        self.assertEqual(result, 3.14)

        # Test write
        root.myDevice.var.set(123)
        result = root.myDevice.var_link.get()
        self.assertEqual(result, 123)

        root.stop()

if __name__ == "__main__":
    unittest.main()