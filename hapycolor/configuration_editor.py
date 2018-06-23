import re
from hapycolor import helpers
from hapycolor import exceptions

class ConfigFileEditor:
    """
    Many targets are usually defined by a configuration file which
    maps colors to the elements of the target.
    In order to create a generic tool able to deal with these kind
    of targets, hapycolor defines a "macro" indicating hapycolor
    that the next color will have to be replaced, i.e., if the
    user wants a color to be replaced by hapycolor, he or she will
    have to precede the target line by a comment line similar to:
    '# @hapycolor(args)'.

    The provided arguments specify which color has to be replaced
    by which color. For instance, if there is only one color which
    has to be replaced by the foreground (resp. background),
    then the argument will only be: "foreground" (resp. "background").
    If the user wants to use another color from the palette, then use:
    "random".

    In some cases, there might be multiple colors on the same line,
    but only a few of them have to be replaced, for instance:

        set colors #010203 #020304 #040506

    Here, the first color should be replaced by the foreground, and
    the last, should be replaced by a color of the palette. In this
    case, the macro should look like:

        # @hapycolor("foreground", None, "random")
        set colors #010203 #020304 #040506

    To use this class, first initialize it with a list storing the
    lines of the configuration file, then, call the function
    :func:`replace(palette)` providing the generated palette which
    will return the new configuration file.
    """
    def __init__(self, configuration):
        self.configuration = configuration
        self.attributes = self.parser()
        if list(filter(lambda a: a, self.attributes)):
            first_line = [line for line, attr in zip(configuration, self.attributes)
                          if attr is not None][0]
            self.pattern, self.converter = self.get_format(first_line)

    def parser(self):
        attributes = [None]
        for line in self.configuration:
            if ConfigFileEditor.is_macro(line):
                attributes.append(ConfigFileEditor.from_macro(line))
            else:
                attributes.append(None)
        return attributes

    @staticmethod
    def is_macro(line):
        pattern = r".*@hapycolor\(.*"
        return re.match(pattern, line) is not None

    @staticmethod
    def from_macro(line):
        pattern = r".*@hapycolor"
        match = re.match(pattern + r"\((.*)\)", line)
        options = [option.strip() for option in match.group(1).split(',')]
        options = [opt[1:-1] if opt != "None" else None for opt in options]
        return options

    @staticmethod
    def get_format(color_line):
                    # (r, g, b)
        patterns = [r"\( *[0-9]+ *, *[0-9]+ *, *[0-9]+ *\)",
                    # (r, g, b, alpha)
                    r"\( *[0-9]+ *, *[0-9]+ *, *[0-9]+ *,",
                    # #rrggbb
                    r"#[0-9a-f-A-F]{6}"]

        converters = [lambda c: "({}, {}, {})".format(c[0], c[1], c[2]),
                      lambda c: "({}, {}, {},".format(c[0], c[1], c[2]),
                      helpers.rgb_to_hex]

        for pattern, converter in zip(patterns, converters):
            if re.match(".*" + pattern + ".*", color_line):
                return pattern, converter

        msg = "Color format at line '{}' not found, feel ".format(color_line)
        msg += " free to raise an issue: https://github.com/rvdz/hapycolor/issues"
        raise exceptions.ColorFormatNotFound(msg)

    def replace(self, palette):
        new_configuration = []
        iter_palette = iter(palette)
        for line, options in zip(self.configuration, self.attributes):
            if options is not None:
                new_line = self.replace_line(line, iter(options), iter_palette)
            else:
                new_line = line
            new_configuration.append(new_line)
        return new_configuration

    def replace_line(self, line, iter_options, iter_palette):
        def repl(match, opt):
            if opt is None:
                return match.group(0)
            elif opt == "random":
                color = next(iter_palette)
            elif opt == "foreground":
                color = iter_palette.foreground
            elif opt == "background":
                color = iter_palette.background
            else:
                msg = "Macro not recognized in line: {}".format(line)
                raise exceptions.InvalidMacroException(msg)
            return self.converter(color)

        sections = re.split("(" + self.pattern + ")", line)
        new_line = []
        for section in sections:
            match = re.match(self.pattern, section)
            if match:
                new_line.append(repl(match, next(iter_options)))
            else:
                new_line.append(section)
        return ''.join(new_line)
