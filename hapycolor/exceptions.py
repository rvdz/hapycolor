"""
Hapycolor's exceptions
"""

from hapycolor import config


class HapycolorError(Exception):
    """ Basic exception for errors raised by hapycolor """
    def __init__(self, msg=None):
        if msg is None:
            msg = "An error occured somewhere. I could tell you more about " \
                  + " the error, but someone was too lazy when writing the " \
                  + " exception."
        super(HapycolorError, self).__init__(msg)


class WrongInputError(HapycolorError, ValueError):
    def __init__(self, msg):
        super(WrongInputError, self).__init__(msg)
        self.msg = msg


class CallingAbstractMethodError(HapycolorError):
    def __init__(self, msg):
        super(CallingAbstractMethodError, self).__init__(msg)
        self.msg = msg


class ExportTargetFailure(HapycolorError):
    def __init__(self, msg, target):
        super(ExportTargetFailure, self).__init__(msg)
        self.target = target
        self.msg = msg

    def disable_target(self):
        self.target.disable()


class PlatformNotSupportedError(HapycolorError):
    def __str__(self):
        supported_os = ",".join([o.name for o in config.OS])
        err_msg = "Platform not supported\n" \
                  + "Currently supporting: %s" % supported_os
        super(PlatformNotSupportedError, self).__init__(err_msg)


class InvalidValueError(HapycolorError):
    def __init__(self, msg):
        super(HapycolorError, self).__init__(msg)
        self.msg = msg


class EmptyPaletteException(HapycolorError):
    def __init__(self, msg):
        super(EmptyPaletteException, self).__init__(msg)
        self.msg = msg


class InvalidImageError(HapycolorError):
    def __init__(self, msg, wrapped_exc=None):
        if wrapped_exc is not None:
            msg = msg + " - " + str(wrapped_exc)
        super(InvalidImageError, self).__init__(msg)
        self.msg = msg


class HslFilterError(HapycolorError):
    def __init__(self, msg, wrapped_exc):
        super(HslFilterError, self).__init__(msg + " - " + str(wrapped_exc))
        self.msg = msg + " - " + str(wrapped_exc)


class UnknownLuminosityFilterTypeError(HapycolorError):
    def __init__(self, msg):
        super(UnknownLuminosityFilterTypeError, self).__init__(msg)
        self.msg = msg


class ExtractorArgumentsError(HapycolorError):
    def __init__(self, msg, wrapped_exc=None):
        if wrapped_exc is not None:
            msg = msg + " - " + str(wrapped_exc)
        super(ExtractorArgumentsError, self).__init__(msg)
        self.msg = msg


class InvalidConfigKeyError(HapycolorError):
    def __init__(self, msg, wrapped_exc=None):
        if wrapped_exc is not None:
            msg = msg + " - " + str(wrapped_exc)
        super(InvalidConfigKeyError, self).__init__(msg)
        self.msg = msg


class ReducerArgumentsError(HapycolorError):
    def __init__(self, msg):
        super(ReducerArgumentsError, self).__init__(msg)
        self.msg = msg


class ColorFormatError(HapycolorError):
    def __init__(self, msg):
        super(ColorFormatError, self).__init__(msg)
        self.msg = msg


class EmptyListError(HapycolorError):
    def __init__(self, msg):
        super(EmptyListError, self).__init__(msg)
        self.msg = msg


class UninitializedError(HapycolorError):
    def __init__(self, msg):
        super(UninitializedError, self).__init__(msg)
        self.msg = msg


class PaletteFormatError(HapycolorError):
    def __init__(self, msg):
        super(PaletteFormatError, self).__init__(msg)
        self.msg = msg


class InvalidTarget(HapycolorError):
    def __init__(self, msg):
        super(InvalidTarget, self).__init__(msg)
        self.msg = msg


class NoCommonPathFound(HapycolorError):
    def __init__(self, msg):
        super(NoCommonPathFound, self).__init__(msg)
        self.msg = msg


class UnsupportedFeatureError(HapycolorError):
    def __init__(self, msg):
        super(UnsupportedFeatureError, self).__init__(msg)
        self.msg = msg


class ImageNotFoundException(HapycolorError):
    def __init__(self, msg):
        super(ImageNotFoundException, self).__init__(msg)
        self.msg = msg


class BlackAndWhitePictureException(HapycolorError):
    def __init__(self, msg):
        super(BlackAndWhitePictureException, self).__init__(msg)
        self.msg = msg


class NotPolarException(HapycolorError):
    def __init__(self, msg):
        super(NotPolarException, self).__init__(msg)
        self.msg = msg


class UnknownAnalysisTypeException(HapycolorError):
    def __init__(self, msg):
        super(UnknownAnalysisTypeException, self).__init__(msg)
        self.msg = msg


class VariableNotFoundError(HapycolorError):
    def __init__(self, msg):
        super(VariableNotFoundError, self).__init__(msg)
        self.msg = msg


class InvalidFileError(HapycolorError):
    def __init__(self, msg):
        super(InvalidFileError, self).__init__(msg)
        self.msg = msg
