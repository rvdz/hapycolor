from hapycolor import imgur
from hapycolor import exceptions
import pathlib
import shutil
import os
import unittest

class TestImgur(unittest.TestCase):
    def test_download_image(self):
        url = "http://i.imgur.com/tfraio8.png"
        with imgur.download(url) as image_path:
            self.assertTrue(pathlib.Path(image_path).exists())

    def test_download_unexistent_image(self):
        url = "https://imgur.com/trijjjjo8"
        with self.assertRaises(exceptions.ImageNotFoundException):
            with imgur.download(url) as image_path:
                pass

    def test_download_album_fail(self):
        with self.assertRaises(exceptions.UnsupportedFeatureError):
            album = "https://imgur.com/a/v9hZq"
            with imgur.download(album):
                pass
