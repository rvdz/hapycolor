from hapycolor import config
from hapycolor import helpers

import enum
import json
import re
import xml.etree.ElementTree as ET


class Iterm:

    class Enumeration(object):
        def __init__(Iterm, key_values):
            for k in key_values:
                setattr(Iterm, k, key_values[k])

    Tag = Enumeration({"DICT": "dict",
                       "REAL": "real",
                       "KEY": "key",
                       "STRING": "string"})

    Key = Enumeration({"NEW_BOOKMARKS": "New Bookmarks",
                       "GUID": "Guid",
                       "NAME": "Name",
                       "TRANSPARENCY": "Transparency",
                       "BACKGROUND_COLOR": "Background Color",
                       "FOREGROUND_COLOR": "Foreground Color",
                       "CURSOR_TEXT_COLOR": "Cursor Text Color",
                       "CURSOR_COLOR": "Cursor Color"})

    @staticmethod
    def __create_color_bloc(color):
        assert(len(color) == 3)

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

        color_keys = [blue_key, green_key, red_key]

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

    @staticmethod
    def __set_ansi_colors(colors, root):
        assert(len(colors) >= 16)
        p = re.compile(r"Ansi [0-9]* Color")
        for i, n in enumerate(root):
            if n.tag == Iterm.Tag.KEY and p.match(n.text):
                root.insert(i+1, Iterm.__create_color_bloc(colors.pop(0)))


    @staticmethod
    def __set_guid(template, root):
        # Retrieves all the profiles' guids

        profiles = root
        for i, n in enumerate(root):
            if n.tag == Iterm.Tag.KEY and n.text == Iterm.Key.NEW_BOOKMARKS:
                profiles = root[i+1]
        guids = []
        for p in profiles:
            for i, n in enumerate(p):
                if n.tag == Iterm.Tag.KEY and n.text == Iterm.Key.GUID:
                    guid = p[i+1].text.split("-")
                    guids.append([int(i, 16) for i in guid])

        assert(len(guids) > 0)
        guid = guids[0][:]

        # Generates a new guid
        # The maximal value of the last integer of a guid
        max_id = 281474976710656
        while guid[-1] in [g[-1] for g in guids]:
            guid[-1] = (guid[-1] + 1) % max_id

        # Insert new guid into the template
        guid_element = ET.Element(Iterm.Tag.STRING)

        guid_string = ["%X" % i for i in guid]
        guid_element.text = "-".join(guid_string)
        guid_element.tail = "\n\t"
        for i, n in enumerate(template):
            if n.tag == Iterm.Tag.KEY and n.text == Iterm.Key.GUID:
                template.insert(i+1, guid_element)

    @staticmethod
    def __set_background_color(color, root):
        color_element = Iterm.__create_color_bloc(color)
        Iterm.__set_element(Iterm.Key.BACKGROUND_COLOR, color_element, root)

    @staticmethod
    def __set_cursor_color(color, root):
        color_element = Iterm.__create_color_bloc(color)
        Iterm.__set_element(Iterm.Key.CURSOR_TEXT_COLOR, color_element, root)

    @staticmethod
    def __set_cursor_text_color(color, root):
        color_element = Iterm.__create_color_bloc(color)
        Iterm.__set_element(Iterm.Key.CURSOR_COLOR, color_element, root)

    @staticmethod
    def __set_foreground_color(color, root):
        color_element = Iterm.__create_color_bloc(color)
        Iterm.__set_element(Iterm.Key.FOREGROUND_COLOR, color_element, root)

    @staticmethod
    def __set_transparency(value, root):
        element = ET.Element(Iterm.Tag.REAL)
        element.text = str(value)
        Iterm.__set_element(Iterm.Key.TRANSPARENCY, element, root)

    @staticmethod
    def __set_name(name, root):
        name_element = ET.Element(Iterm.Tag.STRING)
        name_element.text = name
        name_element.tail = "\n\t"
        Iterm.__set_element(Iterm.Key.NAME, name_element, root)

    @staticmethod
    def __set_element(element_name, element, root):
        """ Finds the key named 'element_name' in 'root' and appends 'element' after it """
        for i, n in enumerate(root):
            if n.tag == Iterm.Tag.KEY and n.text == element_name:
                root.insert(i + 1, element)


    @staticmethod
    def profile(palette, name, img):
        """ Creates an iterm's profile which is added to the terminal preferences' file.
            It requires a palette of 16 colors in rgb format and a for the new profile. """

        template_tree = ET.parse(config.iterm_template())
        template_root = template_tree.getroot()

        Iterm.__set_ansi_colors(palette["colors"][:], template_root)
        Iterm.__set_name(name, template_root)

        Iterm.__set_background_color(palette["background"], template_root)
        Iterm.__set_foreground_color(palette["foreground"], template_root)
        Iterm.__set_cursor_text_color(palette["foreground"], template_root)
        Iterm.__set_cursor_color(palette["foreground"], template_root)
        Iterm.__set_transparency(0.2, template_root)

        config_tree = ET.parse(config.iterm_config())
        root = config_tree.getroot().find(Iterm.Tag.DICT)

        Iterm.__set_guid(template_root, root)

        # Append profile to profile list
        for i, n in enumerate(root):
            if n.tag == Iterm.Tag.KEY and n.text == Iterm.Key.NEW_BOOKMARKS:
                root[i+1].text = "\n\t\t"
                root[i+1].append(template_root)

        # Save changes
        with open(config.iterm_config(), "wb") as f:
            f.write(ET.tostring(config_tree.getroot()))
