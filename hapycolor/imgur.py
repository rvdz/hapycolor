import imgur_downloader.imgurdownloader as imguralbum
from hapycolor import exceptions
import contextlib
import os

@contextlib.contextmanager
def download(url):
    """
    Downloads an image from Imgur_ and returns its local path.

    :arg url: The image's url
    :return: The local path of the downloaded image.
    :raises :class:`UnsupportedFeatureError`: if the url points to an album
    :raises :class:`ImageNotFoundException`: if the image does not exist

    .. _Imgur: http://imgur.com/
    """
    if url.find("/a/") != -1:
        raise exceptions.UnsupportedFeatureError("Hapycolor does not yet support imgur's albums")
    dest = os.path.join(os.getcwd(), "/tmp/test_imgur_downloads")
    name = url.split("/")[-1]
    try:
        imguralbum.ImgurDownloader(url, dest).save_images()
        image_path = dest + "/" + name
        yield image_path
        os.remove(image_path)
    except imguralbum.ImgurException:
        raise exceptions.ImageNotFoundException("The provided url does not lead to an image")
