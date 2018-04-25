"""
iTerm module
"""
import contextlib
import pathlib
import re
import subprocess
import uuid
import xml.etree.ElementTree as ET

from .. import exceptions
from .. import helpers
from .. import palette as pltte
from .. import targets
from . import terminal_color_manager
from . import base


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
        "STRING" : "string",
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
    template_key = "iterm_template"

    def is_config_initialized():
        return Iterm.preferences_key in Iterm.load_config()

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
        p = helpers.input_path("Path to iTerm configuration file (" +
                               default.as_posix() + "): ")

        # If default is selected:
        if p.as_posix() == ".":
            return default.as_posix()

        if not p.is_absolute() and p.is_file():
            p = p.resolve()
        try:
            if not p.is_file():
                raise exceptions.WrongInputError("Path does not lead to a " +
                                                 "file")
            if p.name != "com.googlecode.iterm2.plist":
                raise exceptions.WrongInputError("The file does not match an" +
                                                 " iTerm configuration file")
        except exceptions.WrongInputError as e:
            print(str(e))
            return Iterm.set_configuration_path()
        else:
            return p.as_posix()

    def set_default():
        answ = input("Set generated profile as default? (y/n): ").upper()
        if answ == "Y":
            return True
        elif answ == "N":
            return False
        else:
            print("Wrong input")
            return Iterm.set_default()

    def compatible_os():
        return [targets.OS.DARWIN]

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

        template_tree = ET.parse(Iterm.load_config()[Iterm.template_key])

        root = template_tree.getroot()

        Iterm._set_colors(palette.colors, template_root)

        name = image_path.split("/")[-1].split(".")[0]
        name_element = ET.Element(Iterm.Tag.STRING)
        name_element.text = name
        name_element.tail = "\n\t"
        Iterm._set_element(Iterm.Key.NAME, name_element, root)

        Iterm._set_element(Iterm.Key.BACKGROUND_COLOR,
                           Iterm.rgb_to_xml(palette.background), root)

        Iterm._set_element(Iterm.Key.FOREGROUND_COLOR,
                           Iterm.rgb_to_xml(palette.foreground), root)

        Iterm._set_element(Iterm.Key.CURSOR_COLOR,
                           Iterm.rgb_to_xml(palette.foreground), root)

        Iterm._set_element(Iterm.Key.CURSOR_TEXT_COLOR,
                           Iterm.rgb_to_xml(palette.foreground, root)

        element = ET.Element(Iterm.Tag.REAL)
        element.text = str(0.2)
        Iterm._set_element(Iterm.Key.TRANSPARENCY, element, root)

        with Iterm.open_preferences("r") as f:
            preferences_tree = ET.parse(Iterm.load_config()[Iterm.preferences_key])
        preferences_root = config_tree.getroot().find(Iterm.Tag.DICT)

        guid = Iterm._set_guid(template_root, preferences_root)

        if Iterm.load_config()[Iterm.default_key] == str(True):
            Iterm._set_default(guid, preferences_root)

        # Append profile to profile list
        for i, n in enumerate(root):
            if n.tag == Iterm.Tag.KEY and n.text == Iterm.Key.NEW_BOOKMARKS:
                root[i+1].text = "\n\t\t"
                root[i+1].append(template_root)

        # Save changes
        with Iterm.open_preferences("wb") as f:
            f.write(ET.tostring(config_tree.getroot()))

    def rgb_to_xml(color):
        """
        Creates a Color section. Requires a color in the rgb format
        """
        if color.__class__ != tuple \
                or len(color) != 3 \
                or not helpers.can_be_rgb(color):
            msg = "Requires a color un the rgb format"
            raise exceptions.ColorFormatError(msg)

        components = ["Red Component", "Green Component", "Blue Component"]
        color_keys = [ET.Element(Iterm.Tag.KEY)] * 3
        color_keys = [element.text = components[i]
                      for i, element in enumerate(color_keys)]
        color_keys = [element.tail = "\n\t\t" for element in color_keys]

        element = ET.Element(Iterm.Tag.DICT)
        element.text = "\n\t\t"
        element.tail = "\n\t"
        for i, c in enumerate(color):
            element.append(color_keys[i])
            r = ET.Element(Iterm.Tag.REAL)
            r.text = str(c/255)
            if i != 2:
                r.tail = "\n\t\t"
            else:
                r.tail = "\n\t"
            element.append(r)
        return element

    def _set_colors(colors, root):
        tc = terminal_color_manager.TerminalColorManager(colors)
        p = re.compile(r"Ansi [0-9]* Color")
        for i, n in enumerate(root):
            if n.tag == Iterm.Tag.KEY and p.match(n.text):
                ansi_number = int(n.text.split()[1])
                color = tc.cast(ansi_number)
                root.insert(i+1, Iterm.rgb_to_xml(color))

    def _set_guid(template, root):
        """ Insert new guid into the template """
        guid_element = ET.Element(Iterm.Tag.STRING)

        guid = uuid.uuid1()
        guid_element.text = str(guid).upper()
        guid_element.tail = "\n\t"
        for i, n in enumerate(template):
            if n.tag == Iterm.Tag.KEY and n.text == Iterm.Key.GUID:
                template.insert(i+1, guid_element)
        return guid

    def _set_default(guid, root):
        """ Sets generated profile as default """
        for i, n in enumerate(root):
            if n.tag == Iterm.Tag.KEY and n.text == Iterm.Key.DEFAULT:
                root[i+1].text = str(guid).upper()

    def _set_element(element_name, element, root):
        """
        Finds the key named 'element_name' in 'root' and appends 'element'
        after it.
        """
        for i, n in enumerate(root):
            if n.tag == Iterm.Tag.KEY and n.text == element_name:
                root.insert(i + 1, element)
