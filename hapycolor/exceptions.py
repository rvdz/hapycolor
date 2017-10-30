import hapycolor.config

class HapycolorError(Exception):
    """ Basic exception for errors raised by hapycolor """
    def __init__(self, msg=None):
        if msg is None:
            msg = "An error occured somewhere. I could tell you more about the error, but" \
                    " someone was too lazy when writing the exception."
        super(HapycolorError, self).__init__(msg)

class WrongInputError(HapycolorError, ValueError):
    def __init__(self, msg):
        super(WrongInputError, self).__init__(msg)
        self.msg = msg

class ExportTargetFailure(HapycolorError):
    def __init__(self, msg, target):
        super(ExportTargetFailure, self).__init__(msg)
        self.target = target
        self.msg = msg
    def disable_target(self):
        save_config("export", self.target.value["enabled"], str(False))

class PlatformNotSupportedError(HapycolorError):
    def __str__(self):
        supported_os = ",".join([o.name for o in config.OS])
        super(PlatformNotSupportedError, self).__init__("Platform not supported\nCurrently supporting: %s" % supported_os)


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
        if not wrapped_exc is None:
            msg = msg + " - " + str(wrapped_exc)
        super(InvalidImageError, self).__init__(msg)
        self.msg = msg

class FilterError(HapycolorError):
    def __init__(self, msg, wrapped_exc):
        super(FilterError, self).__init__(msg + " - " + str(wrapped_exc))
        self.msg = msg + " - " + str(wrapped_exc)

class UnknownFilterTypeError(HapycolorError):
    def __init__(self, msg):
        super(UnknownFilterTypeError, self).__init__(msg)
        self.msg = msg

class ExtractorArgumentsError(HapycolorError):
    def __init__(self, msg, wrapped_exc=None):
        if not wrapped_exc is None:
            msg = msg + " - " + str(wrapped_exc)
        super(ExtractorArgumentsError, self).__init__(msg)
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
