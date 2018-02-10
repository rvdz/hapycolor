import abc


class Filter(metaclass=abc.ABCMeta):
    """
    This is the base class for all filters. Currently, it only asks to
    implement the function that, given a palette, filter its colors.
    """
    @abc.abstractstaticmethod
    def apply(palette):
        """
        :arg palette: the input palette
        :return: returns an output palette
        """
        pass
