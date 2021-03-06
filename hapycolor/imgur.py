import imgur_downloader.imgurdownloader as imguralbum
from hapycolor import exceptions
import pathlib
import tempfile


def download(url):
    """
    Downloads an image from Imgur_ and returns its local path.

    :arg url: The image's url
    :return: The local path of the downloaded image
    :raises: :class:`UnsupportedFeatureError` if the url points to an album
    :raises: :class:`ImageNotFoundException` if the image does not exist

    .. _Imgur: http://imgur.com/
    """
    if url.find("/a/") != -1:
        raise exceptions.UnsupportedFeatureError("Hapycolor does not yet"
                                                 + " support imgur's albums")
    name = url.split("/")[-1]
    dest = pathlib.Path('.')
    if (dest / name).exists():
        (dest / name).unlink()
    try:
        imguralbum.ImgurDownloader(url, dest.as_posix()).save_images()
        image_path = dest / name
        return image_path.as_posix()
    except imguralbum.ImgurException as exc:
        msg = "ERROR: The provided url does not lead to an image"
        raise exceptions.ImageNotFoundException(msg)
