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
            raw = "b'0,0: (1194.25)  #050505  gray(5)\n'"
            raw_colors.extract_rgb(raw)

    def test_no_failures_alpha(self):
        try:
            image = "./images/alpha.png"
            raw_colors.get(image, 15)
        except Exception as e:
            self.fail(str(e))

    def test_trolling(self):
        """
        TODO: Working on chrome, but should be tested on firefox or chromium
        """
        proc = raw_colors.trolling("--version")
        regex = "(Google Chrome)|(Firefox)|(Chromium)"
        self.assertRegex(proc.stdout.decode(), regex)
