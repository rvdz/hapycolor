from hapycolor import imgur
from hapycolor import exceptions
import pathlib
import shutil
import os
import unittest
import urllib.error

class TestImgur(unittest.TestCase):
    warning = "This test is supposed to fail if there is no internet " \
            + "connection"

    def test_download_image(self):
        url = "http://i.imgur.com/tfraio8.png"
        try:
            with imgur.download(url) as image_path:
                self.assertTrue(pathlib.Path(image_path).exists(),
                        TestImgur.warning)
        except urllib.error.URLError:
            self.fail(TestImgur.warning)

    def test_download_unexistent_image(self):
        url = "https://imgur.com/trijjjjo8"
        with self.assertRaises(exceptions.ImageNotFoundException):
            try:
                with imgur.download(url) as image_path:
                    pass
            except urllib.error.URLError:
                self.fail(TestImgur.warning)

    def test_download_album_fail(self):
            with self.assertRaises(exceptions.UnsupportedFeatureError):
                try:
                    album = "https://imgur.com/a/v9hZq"
                    with imgur.download(album):
                        pass
                except urllib.error.URLError:
                    self.fail(TestImgur.warning)
