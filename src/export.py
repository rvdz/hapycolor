import json
import xml.etree.ElementTree as ET
import enum
import re
import utils
import config

class iTerm:

    def __init__(self, palette, name):
        class Enumeration(object):
            def __init__(self, key_values):
                for k in key_values:
                    setattr(self, k, key_values[k])
        self.Tag = Enumeration({"DICT": "dict",
                                "REAL": "real",
                                "KEY": "key",
                                "STRING": "string"})

        self.Key = Enumeration({"NEW_BOOKMARKS": "New Bookmarks",
                                "GUID": "Guid",
                                "NAME": "Name",
                                "TRANSPARENCY": "Transparency",
                                "BACKGROUND_COLOR": "Background Color",
                                "FOREGROUND_COLOR": "Foreground Color",
                                "CURSOR_TEXT_COLOR": "Cursor Text Color",
                                "CURSOR_COLOR": "Cursor Color"})
        self.__create_profile(palette, name)


    def __create_color_bloc(self, color):
        assert(len(color) == 3)

        new_line = "\n\t\t"
        red_key = ET.Element(self.Tag.KEY)
        red_key.text = "Red Component"
        red_key.tail = new_line
        green_key = ET.Element(self.Tag.KEY)
        green_key.text = "Green Component"
        green_key.tail = new_line
        blue_key = ET.Element(self.Tag.KEY)
        blue_key.text = "Blue Component"
        blue_key.tail = new_line

        color_keys = [blue_key, green_key, red_key]

        bloc = ET.Element(self.Tag.DICT)
        bloc.text = new_line
        bloc.tail = "\n\t"
        for i, c in enumerate(color):
            bloc.append(color_keys[i])
            r = ET.Element(self.Tag.REAL)
            r.text = str(c/255)
            if i != 2:
                r.tail = new_line
            else:
                r.tail = "\n\t"
            bloc.append(r)
        return bloc

    def __set_ansi_colors(self, colors, root):
        assert(len(colors) == 16)
        p = re.compile(r"Ansi [0-9]* Color")
        for i, n in enumerate(root):
            if n.tag == self.Tag.KEY and p.match(n.text):
                root.insert(i+1, self.__create_color_bloc(colors.pop(0)))



    def __set_guid(self, template, root):
        # Retrieves all the profiles' guids

        profiles = root
        for i, n in enumerate(root):
            if n.tag == self.Tag.KEY and n.text == self.Key.NEW_BOOKMARKS:
                profiles = root[i+1]

        guids = []
        for p in profiles:
            for i, n in enumerate(p):
                if n.tag == self.Tag.KEY and n.text == self.Key.GUID:
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
        guid_element = ET.Element(self.Tag.STRING)

        guid_string = ["%X" % i for i in guid]
        guid_element.text = "-".join(guid_string)
        guid_element.tail = "\n\t"
        for i, n in enumerate(template):
            if n.tag == self.Tag.KEY and n.text == self.Key.GUID:
                template.insert(i+1, guid_element)


    def __set_background_color(self, color, root):
        color_element = self.__create_color_bloc(color)
        self.__set_element(self.Key.BACKGROUND_COLOR, color_element, root)

    def __set_cursor_color(self, color, root):
        color_element = self.__create_color_bloc(color)
        self.__set_element(self.Key.CURSOR_TEXT_COLOR, color_element, root)

    def __set_cursor_text_color(self, color, root):
        color_element = self.__create_color_bloc(color)
        self.__set_element(self.Key.CURSOR_COLOR, color_element, root)

    def __set_foreground_color(self, color, root):
        color_element = self.__create_color_bloc(color)
        self.__set_element(self.Key.FOREGROUND_COLOR, color_element, root)

    def __set_transparency(self, value, root):
        element = ET.Element(self.Tag.REAL)
        element.text = str(value)
        self.__set_element(self.Key.TRANSPARENCY, element, root)

    def __set_name(self, name, root):
        name_element = ET.Element(self.Tag.STRING)
        name_element.text = name
        name_element.tail = "\n\t"
        self.__set_element(self.Key.NAME, name_element, root)

    def __set_element(self, element_name, element, root):
        """ Finds the key named 'element_name' in 'root' and appends 'element' after it """
        for i, n in enumerate(root):
            if n.tag == self.Tag.KEY and n.text == element_name:
                root.insert(i + 1, element)


    def __create_profile(self, palette, name):
        """ Creates an iterm's profile which is added to the terminal preferences' file.
            It requires a palette of 16 colors in rgb format and a for the new profile. """

        template_tree = ET.parse(config.Config.ITERM_TEMPLATE)
        template_root = template_tree.getroot()

        self.__set_ansi_colors(palette["colors"][:], template_root)
        self.__set_name(name, template_root)

        self.__set_background_color(palette["background"], template_root)
        self.__set_foreground_color(palette["foreground"], template_root)
        self.__set_cursor_text_color(palette["foreground"], template_root)
        self.__set_cursor_color(palette["foreground"], template_root)
        self.__set_transparency(0.2, template_root)

        config_tree = ET.parse(config.Config.ITERM_CONFIG)
        root = config_tree.getroot().find(self.Tag.DICT)

        self.__set_guid(template_root, root)

        # Append profile to profile list
        for i, n in enumerate(root):
            if n.tag == self.Tag.KEY and n.text == self.Key.NEW_BOOKMARKS:
                root[i+1].text = "\n\t\t"
                root[i+1].append(template_root)

        # Save changes
        with open(config.Config.ITERM_CONFIG, "wb") as f:
            f.write(ET.tostring(config_tree.getroot()))


class Vim:
    def __init__(self, palette):
        self.header = '''
set background=dark
if exists("syntax_on")
syntax reset
endif
let g:colors_name = "'''
        self.header += config.Config.APP_NAME + '"'

        self.foreground = "Normal"
        self.groups = [["Comment"],
                       ["Boolean"],
                       ["Character"],
                       ["Keyword"],
                       ["Number"],
                       ["String"],
                       ["Conditional"],
                       ["Macro"],
                       ["Constant", "Define"],
                       ["Cursor"],
                       ["Delimiter", "Directory"],
                       ["Error", "ErrorMsg", "Exception"],
                       ["Float"],
                       ["Function", "MatchParen"],
                       ["Identifier"],
                       ["Label","Operator"]]
        self.__create_profile(palette)

    def __create_profile(self, palette):
        assert(len(palette["colors"]) == len(self.groups))
        with open(config.Config.COLORSCHEME_VIM, "w") as f:
            f.write(self.header + "\n\n")
            l = ["hi " + self.foreground, "guifg=" + utils.rgb_to_hex(palette["foreground"]) + "\n"]
            f.write("{: <20}  {: <20}".format(*l))
            for i, G in enumerate(self.groups):
                for g in G:
                    l = ["hi " + g, "guifg=" + utils.rgb_to_hex(palette["colors"][i]) + "\n"]
                    f.write("{: <20}  {: <20}".format(*l))
