from hapycolor import config
from hapycolor import helpers

from hapycolor import exceptions
from hapycolor import palette as pltte
from . import base

import random
import enum
import uuid
import re
import xml.etree.ElementTree as ET

class Iterm(base.Target):

    class Enumeration(object):
        def __init__(Iterm, key_values):
            for k in key_values:
                setattr(Iterm, k, key_values[k])

    Tag = Enumeration({
                       "DICT"   : "dict",
                       "REAL"   : "real",
                       "KEY"    : "key",
                       "STRING" : "string"
                      })

    Key = Enumeration({
                       "NEW_BOOKMARKS"     : "New Bookmarks",
                       "GUID"              : "Guid",
                       "NAME"              : "Name",
                       "TRANSPARENCY"      : "Transparency",
                       "BACKGROUND_COLOR"  : "Background Color",
                       "FOREGROUND_COLOR"  : "Foreground Color",
                       "CURSOR_TEXT_COLOR" : "Cursor Text Color",
                       "CURSOR_COLOR"      : "Cursor Color"
                      })

    preferences_key = "iterm_preferences"
    template_key = "iterm_template"
    def is_config_initialized():
        return Iterm.preferences_key in Iterm.load_config()

    def initialize_config():
        """
        Checks if iTerm's preferences file is correct and save it's path in the
        project configuration file.
        """
        p = config.input_path("Path to iTerm configuration file: ")
        if not p.is_absolute() and p.is_file():
            p = p.resolve()
        if not p.is_file():
            raise exceptions.WrongInputError("Path does not lead to a file")
        if p.name != "com.googlecode.iterm2.plist":
            raise exceptions.WrongInputError("The file does not match an iTerm"
                                             + " configuration file")
        Iterm.save_config({Iterm.preferences_key: p.as_posix()})

    def compatible_os():
        return [config.OS.DARWIN]

    def export(palette, image_path):
        """
        Creates an iterm's profile which is added to the terminal preferences'
        file. It requires a palette of 16 colors defined in the rgb format and
        a name for the new profile.

        :arg palette: an instance of the class :class:`hapycolor.palette.Palette`
        :arg image_path: a string which will be used to name the newly created profile
        """
        if palette.__class__ != pltte.Palette or not palette.is_initialized:
            msg = "The palette has not been correctly initialized"
            raise exceptions.PaletteFormatError(msg)

        template_tree = ET.parse(Iterm.load_config()[Iterm.template_key])

        template_root = template_tree.getroot()

        Iterm.__set_ansi_colors(palette.colors, template_root)

        name = image_path.split("/")[-1].split(".")[0]
        Iterm.__set_name(name, template_root)

        Iterm.__set_background_color(palette.background, template_root)
        Iterm.__set_foreground_color(palette.foreground, template_root)
        Iterm.__set_cursor_text_color(palette.foreground, template_root)
        Iterm.__set_cursor_color(palette.foreground, template_root)
        Iterm.__set_transparency(0.2, template_root)

        config_tree = ET.parse(Iterm.load_config()[Iterm.preferences_key])
        root = config_tree.getroot().find(Iterm.Tag.DICT)

        Iterm.__set_guid(template_root, root)

        # Append profile to profile list
        for i, n in enumerate(root):
            if n.tag == Iterm.Tag.KEY and n.text == Iterm.Key.NEW_BOOKMARKS:
                root[i+1].text = "\n\t\t"
                root[i+1].append(template_root)

        # Save changes
        with open(Iterm.load_config()[Iterm.preferences_key], "wb") as f:
            f.write(ET.tostring(config_tree.getroot()))

    def __create_color_bloc(color):
        """ Creates a Color bloc. Requires a color in the rgb format """
        if color.__class__ != tuple \
                or len(color) != 3 \
                or not helpers.can_be_rgb(color):
            msg = "Requires a color un the rgb format"
            raise exceptions.ColorFormatError(msg)

        new_line       = "\n\t\t"
        red_key        = ET.Element(Iterm.Tag.KEY)
        red_key.text   = "Red Component"
        red_key.tail   = new_line
        green_key      = ET.Element(Iterm.Tag.KEY)
        green_key.text = "Green Component"
        green_key.tail = new_line
        blue_key       = ET.Element(Iterm.Tag.KEY)
        blue_key.text  = "Blue Component"
        blue_key.tail  = new_line

        color_keys = [blue_key, green_key, red_key]

        bloc      = ET.Element(Iterm.Tag.DICT)
        bloc.text = new_line
        bloc.tail = "\n\t"
        for i, c in enumerate(color):
            bloc.append(color_keys[i])
            r = ET.Element(Iterm.Tag.REAL)
            r.text = str(c/255)
            if i != 2:
                r.tail = new_line
            else:
                r.tail = "\n\t"
            bloc.append(r)
        return bloc

    def __set_ansi_colors(colors, root):
        tc = TermColorManager(colors)
        p = re.compile(r"Ansi [0-9]* Color")
        for i, n in enumerate(root):
            if n.tag == Iterm.Tag.KEY and p.match(n.text):
                ansi_number = int(n.text.split()[1])
                color = tc.get_color(ansi_number)
                root.insert(i+1, Iterm.__create_color_bloc(color))

    def __set_guid(template, root):
        """ Insert new guid into the template """
        guid_element = ET.Element(Iterm.Tag.STRING)

        guid_element.text = str(uuid.uuid1()).upper()
        guid_element.tail = "\n\t"
        for i, n in enumerate(template):
            if n.tag == Iterm.Tag.KEY and n.text == Iterm.Key.GUID:
                template.insert(i+1, guid_element)

    def __set_background_color(color, root):
        color_element = Iterm.__create_color_bloc(color)
        Iterm.__set_element(Iterm.Key.BACKGROUND_COLOR, color_element, root)

    def __set_cursor_color(color, root):
        color_element = Iterm.__create_color_bloc(color)
        Iterm.__set_element(Iterm.Key.CURSOR_TEXT_COLOR, color_element, root)

    def __set_cursor_text_color(color, root):
        color_element = Iterm.__create_color_bloc(color)
        Iterm.__set_element(Iterm.Key.CURSOR_COLOR, color_element, root)

    def __set_foreground_color(color, root):
        color_element = Iterm.__create_color_bloc(color)
        Iterm.__set_element(Iterm.Key.FOREGROUND_COLOR, color_element, root)

    def __set_transparency(value, root):
        element = ET.Element(Iterm.Tag.REAL)
        element.text = str(value)
        Iterm.__set_element(Iterm.Key.TRANSPARENCY, element, root)

    def __set_name(name, root):
        name_element      = ET.Element(Iterm.Tag.STRING)
        name_element.text = name
        name_element.tail = "\n\t"
        Iterm.__set_element(Iterm.Key.NAME, name_element, root)

    def __set_element(element_name, element, root):
        """
        Finds the key named 'element_name' in 'root' and appends 'element'
        after it.
        """
        for i, n in enumerate(root):
            if n.tag == Iterm.Tag.KEY and n.text == element_name:
                root.insert(i + 1, element)


class TermColorManager():
    """
    This class manages the terminal colors and defines a method that, for a
    standard of high-intensity terminal color's number, returns the
    appropriate rgb color of the provided palette.
    For more details about standard and high-intensity terminal colors, see:
    `Standard and Hight-intensity colors <https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit>`_

    Initializes a :class:`TermColorManager`'s instance with a list of colors.

    :arg colors: a `list` of rgb colors
    """
    def __init__(self, colors):
        if colors.__class__ != list or len(colors) == 0:
            msg = "'colors' list must contain at least one element"
            raise exceptions.EmptyListError(msg)
        if not all([helpers.can_be_rgb(c) for c in colors]):
            msg = "'colors' must be defined in the rgb base"
            raise exceptions.ColorFormatError(msg)
        # Convert to hsl
        hsl_colors = [helpers.rgb_to_hsl(c) for c in colors]
        self.colors = TermColorManager.analyze_colors(hsl_colors)

    @staticmethod
    def get_label(hsl_color):
        """ Returns a :class:`TermColorEnum` enum according to the color's hue

        :arg hsl_color: a tuple representing a color defined in the hsl base
        """
        for l in TermColorEnum:
            if l.value[0] \
                    and l.value[0][0] <= hsl_color[0] \
                    and hsl_color[0] <= l.value[0][1]:
                return l
        return TermColorEnum.RED

    @staticmethod
    def analyze_colors(colors):
        """
        Creates a dictionary which labelize each color with a respective enum
        from :class:`TermColorEnum`.
        """
        # Sort by hue
        colors.sort(key=lambda c: c[0])

        # Create a dictionary where each term is associated to the right
        # color extracted
        term_colors = {}
        for c in colors:
            label = TermColorManager.get_label(c)
            if label not in term_colors:
                term_colors[label] = []
            term_colors[label].append(c)
        term_colors[TermColorEnum.BLACK] = [(0, 0, 0)]
        term_colors[TermColorEnum.WHITE] = [(0, 0, 1)]

        return term_colors

    def get_color(self, index):
        """
        Takes standard or high-intensity terminal color's number and retrives the
        appropriate rgb color.

        :arg index: an integer between 0 and 15
        """
        if index.__class__ != int or index < 0 or index > 15:
            msg = "Ansi color values are described by integers starting from" \
                  + " 0 up to 15"
            raise exceptions.InvalidValueError(msg)

        if self.colors.__class__ != dict or len(self.colors) == 0:
            msg = "TermColorManager's instance has not been initialized properly"
            raise exceptions.UninitializedError(msg)

        for tc in TermColorEnum:
            if index in tc.value[1]:
                # If the provided index corresponds to this TermColor enum
                if tc not in self.colors:
                    # If there are no colors for this label, returns a random one
                    tmp_colors = {**self.colors}
                    del tmp_colors[TermColorEnum.BLACK]
                    del tmp_colors[TermColorEnum.WHITE]
                    label = random.choice(list(tmp_colors))

                    while not self.colors[label]:
                        # If the label is empty, pick another one
                        label = random.choice(list(self.colors))
                    return helpers.hsl_to_rgb(random.choice(self.colors[label]))

                if max(tc.value[1]) == index:
                    # Return the brightest color of the label
                    brightest_color = max(self.colors[tc], key=lambda c: c[2])
                    return helpers.hsl_to_rgb(brightest_color)

                # Return the darkest color of the label
                darkest_color = min(self.colors[tc], key=lambda c: c[2])
                return helpers.hsl_to_rgb(darkest_color)


class TermColorEnum(enum.Enum):
    """
    Defines six enumerates which represent a label of the 'hue' dimension

    - First list defines the hue's range in degrees
    - Second list defines to which terminal's standard and high-intensity color's number the label is related.

    For more details about standard and high-intensity terminal colors see:
    `Standard and High-intensity colors <https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit>`_
    """
    BLACK   = [[ ],         [ 0, 8]]
    WHITE   = [[ ],         [ 7, 15]]
    RED     = [[ 345, 25],  [ 4, 12]]
    YELLOW  = [[ 25, 60],   [ 6, 14]]
    GREEN   = [[ 60, 160],  [ 2, 10]]
    CYAN    = [[ 160, 200], [ 3, 11]]
    BLUE    = [[ 200, 260], [ 1, 9]]
    MAGENTA = [[ 260, 345], [ 5, 13]]
