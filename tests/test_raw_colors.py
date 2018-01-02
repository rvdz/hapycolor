import unittest
from hapycolor import exceptions
from hapycolor import raw_colors


class TestRawColors(unittest.TestCase):
    def test_no_failures_rgb(self):
        try:
            image = "./images/firewatch.jpg"
            raw_colors.get(image, 15)
        except Exception as e:
            print(str(e))
            self.fail(str(e))

    def test_no_failures_greyscale(self):
        with self.assertRaises(exceptions.BlackAndWhitePictureException):
            image = "./images/greyscale.png"
            raw_colors.get(image, 15)

    def test_no_failures_alpha(self):
        try:
            image = "./images/alpha.png"
            raw_colors.get(image, 15)
        except Exception as e:
            self.fail(str(e))
