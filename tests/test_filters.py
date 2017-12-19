from hapycolor import config
from hapycolor import filters
from hapycolor.filters import *
from hapycolor.filters import base

import unittest

class TestFilters(unittest.TestCase):
    def test_filters_are_modules(self):
        """
        Asserts that all the filters in the configuration file represent a
        module of the filters module.
        """
        fltr_config = config.load("Filters")
        for f in fltr_config:
            try:
                eval(f)
            except Exception as e:
                self.fail(str(f) + " is not a module - " + str(e))

    def test_filter_modules_contain_filter_class(self):
        """
        Asserts that the filters modules defined in the configuration file
        contain a class that implements a Filter class.
        """
        fltr_config = config.load("Filters")
        classes = []
        for f in fltr_config:
            clazz = "".join(x.title() for x in f.split('_'))
            try:
                classes.append(eval(f + "." + clazz))
            except Exception as e:
                self.fail(str(clazz) + " is not a class - " + str(e))

        [self.assertIsInstance(c(), base.Filter) for c in classes]


    def test_correct_order(self):
        """
        Asserts that the luminosity filter will be applied before the reduction.
        """
        fltrs_classes = filters.get_filters()
        self.assertLess(fltrs_classes.index(luminosity_filter.LuminosityFilter),
                        fltrs_classes.index(reducer.Reducer))

    def test_filters_class_names(self):
        """
        Assert that each filter class is named after its module name. It should be
        a PascalCase version of it. In addition, it checks also if the respective
        class inherits from :class:base.Filter.
        """
        import inspect

        filters.__all__ = ['luminosity_filter', 'reducer']
        filter_modules = inspect.getmembers(filters)[0][1]
        for m in filter_modules:
            try:
                self.assertTrue(inspect.ismodule(eval("filters." + m)))
                clazz_str = "".join([t.title() for t in m.split("_")])
                clazz = eval(m + "." + clazz_str)
                self.assertTrue(inspect.isclass(clazz))
                self.assertIsInstance(clazz(), base.Filter)
            except NameError as e:
                self.fails(str(e))
