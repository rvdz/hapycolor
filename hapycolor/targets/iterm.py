from hapycolor import config
from hapycolor import helpers

from hapycolor import exceptions
from hapycolor import palette as pltte
from . import base
import subprocess
import contextlib

import random
import enum
import pathlib
import uuid
import re
import xml.etree.ElementTree as ET

class Iterm(base.Target):

    @contextlib.contextmanager
    def open_preferences(mode="r"):
        preferences = Iterm.load_config()[Iterm.preferences_key]
        subprocess.run(["plutil", "-convert", "xml1", preferences])
        with open(preferences, mode) as f:
            yield f
        # subprocess.run(["plutil", "-convert", "binary1", preferences])

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
                       "DEFAULT"           : "Default Bookmark Guid",
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
    default_key = "default"
    template = "./hapycolor/targets/iterm_template.xml"

    def is_config_initialized():
        try:
            return Iterm.preferences_key in Iterm.load_config()
        except exceptions.InvalidConfigKeyError:
            return False

    def initialize_config():
        """
        Checks if iTerm's preferences file is correct and save it's path in the
        project configuration file. Then asks for the user if the generated
        profiles should be set as default.
        """
        config_path = Iterm.set_configuration_path()
        Iterm.save_config({Iterm.preferences_key: config_path})
        is_default = Iterm.set_default()
        Iterm.save_config({Iterm.default_key: str(is_default)})

    def reconfigure():
        try:
            is_default = eval(Iterm.load_config()[Iterm.default_key])
            is_set = "set" if not is_default else "unset"
            print("\nChange configuration path: 1")
            print(is_set.title() + " generated profile as default: 2")
            option = int(input("Option: "))
            if option != 1 and option != 2:
                raise ValueError
            elif option == 1:
                path = Iterm.set_configuration_path()
                Iterm.save_config({Iterm.preferences_key: path})
            elif option == 2:
                Iterm.save_config({Iterm.default_key: str(not is_default)})
        except ValueError:
            print("Wrong input")
            Iterm.reconfigure()

    def set_configuration_path():
        default_str = "~/Library/Preferences/com.googlecode.iterm2.plist"
        default = pathlib.Path(default_str).expanduser()
        msg = """Path to iTerm configuration file
(Keep empty to use default path '""" + default.as_posix() + """'): """
        p = config.input_path(msg)

        # If default is selected:
        if p.as_posix() == ".":
            return default.as_posix()

        if not p.is_absolute() and p.is_file():
            p = p.resolve()
        try:
            if not p.is_file():
                msg = "Path does not lead to a file"
                raise exceptions.WrongInputError(msg)
            if p.name != "com.googlecode.iterm2.plist":
                msg = "The file does not match an iTerm configuration file"
                raise exceptions.WrongInputError(msg)
        except exceptions.WrongInputError as e:
            print(str(e))
            return Iterm.set_configuration_path()
        else:
            return p.as_posix()

    def set_default():
        answer = input("Set generated profile as default? (y/n): ").upper()
        return answer == "N"

    def compatible_os():
        return [config.OS.DARWIN]

    def export(palette, image_path):
        """
        Creates an iterm's profile which is added to the terminal preferences'
        file. It requires a palette of 16 colors defined in the rgb format and
        a name for the new profile.

        :arg palette: an instance of the class
            :class:`hapycolor.palette.Palette`
        :arg image_path: a string which will be used to name the newly created
             profile
        """
        if palette.__class__ != pltte.Palette or not palette.is_initialized:
            msg = "The palette has not been correctly initialized"
            raise exceptions.PaletteFormatError(msg)

        template_tree = ET.parse(Iterm.template)

        template_root = template_tree.getroot()

        Iterm.__set_ansi_colors(palette.colors, template_root)

        name = image_path.split("/")[-1].split(".")[0]
        Iterm.__set_name(name, template_root)

        Iterm.__set_background_color(palette.background, template_root)
        Iterm.__set_foreground_color(palette.foreground, template_root)
        Iterm.__set_cursor_text_color(palette.foreground, template_root)
        Iterm.__set_cursor_color(palette.foreground, template_root)
        Iterm.__set_transparency(0.2, template_root)

        with Iterm.open_preferences("r") as f:
            config_tree = ET.parse(Iterm.load_config()[Iterm.preferences_key])
        root = config_tree.getroot().find(Iterm.Tag.DICT)

        guid = Iterm.__set_guid(template_root, root)

        if Iterm.load_config()[Iterm.default_key] == str(True):
            Iterm.__set_default(guid, root)

        # Append profile to profile list
        for i, n in enumerate(root):
            if n.tag == Iterm.Tag.KEY and n.text == Iterm.Key.NEW_BOOKMARKS:
                root[i+1].text = "\n\t\t"
                root[i+1].append(template_root)

        # Save changes
        with Iterm.open_preferences("wb") as f:
            f.write(ET.tostring(config_tree.getroot()))

    def __create_color_bloc(color):
        """ Creates a Color bloc. Requires a color in the rgb format """
        if color.__class__ != tuple \
                or len(color) != 3 \
                or not helpers.can_be_rgb(color):
            msg = "Requires a color un the rgb format"
            raise exceptions.ColorFormatError(msg)

        new_line = "\n\t\t"
        red_key = ET.Element(Iterm.Tag.KEY)
        red_key.text = "Red Component"
        red_key.tail = new_line
        green_key = ET.Element(Iterm.Tag.KEY)
        green_key.text = "Green Component"
        green_key.tail = new_line
        blue_key = ET.Element(Iterm.Tag.KEY)
        blue_key.text = "Blue Component"
        blue_key.tail = new_line

        color_keys = [red_key, green_key, blue_key]

        bloc = ET.Element(Iterm.Tag.DICT)
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

        guid = uuid.uuid1()
        guid_element.text = str(guid).upper()
        guid_element.tail = "\n\t"
        for i, n in enumerate(template):
            if n.tag == Iterm.Tag.KEY and n.text == Iterm.Key.GUID:
                template.insert(i+1, guid_element)
        return guid

    def __set_default(guid, root):
        """ Sets generated profile as default """
        for i, n in enumerate(root):
            if n.tag == Iterm.Tag.KEY and n.text == Iterm.Key.DEFAULT:
                root[i+1].text = str(guid).upper()

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
        name_element = ET.Element(Iterm.Tag.STRING)
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
    `Standard and Hight-intensity colors
    <https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit>`_

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
        Takes standard or high-intensity terminal color's number and retrives
        the appropriate rgb color.

        :arg index: an integer between 0 and 15
        """
        if index.__class__ != int or index < 0 or index > 15:
            msg = "Ansi color values are described by integers starting from" \
                  + " 0 up to 15"
            raise exceptions.InvalidValueError(msg)

        if self.colors.__class__ != dict or len(self.colors) == 0:
            msg = "TermColorManager has not been initialized properly"
            raise exceptions.UninitializedError(msg)

        for tc in TermColorEnum:
            # If the provided index corresponds to this TermColor enum
            if index in tc.value[1]:
                # If there are no colors for this label, returns a random one
                if tc not in self.colors:
                    tmp_colors = {**self.colors}
                    del tmp_colors[TermColorEnum.BLACK]
                    del tmp_colors[TermColorEnum.WHITE]
                    label = random.choice(list(tmp_colors))

                    # If the label is empty, pick another one
                    while not self.colors[label]:
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
    - Second list defines to which terminal's standard and high-intensity
        color's number the label is related.

    For more details about standard and high-intensity terminal colors see:
    `Standard and High-intensity colors
    <https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit>`_
    """
    BLACK   = [[ ],         [ 0, 8]]
    WHITE   = [[ ],         [ 7, 15]]
    RED     = [[ 345, 25],  [ 1, 9]]
    YELLOW  = [[ 25, 60],   [ 3, 11]]
    GREEN   = [[ 60, 160],  [ 2, 10]]
    CYAN    = [[ 160, 200], [ 6, 14]]
    BLUE    = [[ 200, 260], [ 4, 12]]
    MAGENTA = [[ 260, 345], [ 5, 13]]
