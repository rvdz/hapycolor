import json
import xml.etree.ElementTree as ET
import re

class ProfileGenerator:

    def __init__(self):
        pass



    def __create_color_bloc(self, color):
        assert(len(color) == 3)

        new_line = "\n\t\t"
        red_key = ET.Element("key")
        red_key.text = "Red Component"
        red_key.tail = new_line
        green_key = ET.Element("key")
        green_key.text = "Green Component"
        green_key.tail = new_line
        blue_key = ET.Element("key")
        blue_key.text = "Blue Component"
        blue_key.tail = new_line

        color_keys = [blue_key, green_key, red_key]

        bloc = ET.Element("dict")
        bloc.text = new_line
        bloc.tail = "\n\t"
        for i, c in enumerate(color):
            bloc.append(color_keys[i])
            r = ET.Element("real")
            r.text = str(c)
            if i != 2:
                r.tail = new_line
            else:
                r.tail = "\n\t"
            bloc.append(r)
        return bloc

    def __insert_palette(self, colors, root):
        assert(len(colors) == 16)
        p = re.compile(r"Ansi [0-9]* Color")
        for i, n in enumerate(root):
            if n.tag == "key" and p.match(n.text):
                root.insert(i+1, self.__create_color_bloc(colors.pop(0)))

    def __set_name(self, name, root):
        name_element = ET.Element("string")
        name_element.text = name
        name_element.tail = "\n\t"

        for i, n in enumerate(root):
            if n.tag == "key" and n.text == "Name":
                root.insert(i + 1, name_element)

    def __set_background(self, color, root):
        bloc = self.__create_color_bloc(color)
        for i, n in enumerate(root):
            if n.tag == "key" and n.text == "Background Color":
                root.insert(i+1, bloc)

    def __set_guid(self, template, root):
        # Retrieves all the profiles' guids

        profiles = root
        for i, n in enumerate(root):
            if n.tag == "key" and n.text == "New Bookmarks":
                profiles = root[i+1]

        guids = []
        for p in profiles:
            for i, n in enumerate(p):
                if n.tag == "key" and n.text == "Guid":
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
        guid_element = ET.Element("string")

        guid_string = ["%X" % i for i in guid]
        guid_element.text = "-".join(guid_string)
        guid_element.tail = "\n\t"
        for i, n in enumerate(template):
            if n.tag == "key" and n.text == "Guid":
                template.insert(i+1, guid_element)

    def iterm(self, palette, name):
        template = "/Users/yanncolina/Documents/template.plist"
        config_file = "/Users/yanncolina/Documents/com.googlecode.iterm2.plist"

        template_tree = ET.parse(template)
        template_root = template_tree.getroot()

        self.__insert_palette(palette, template_root)
        self.__set_name(name, template_root)

        bg = (0, 0, 0)
        self.__set_background(bg, template_root)

        config_tree = ET.parse(config_file)
        root = config_tree.getroot().find("dict")

        self.__set_guid(template_root, root)

        for i, n in enumerate(root):
            if n.tag == "key" and n.text == "New Bookmarks":
                root[i+1].text = "\n\t\t"
                root[i+1].append(template_root)

        with open(config_file, "wb") as f:
            f.write(ET.tostring(config_tree.getroot()))


    def gnome_terminal(output_file):
        # f = open(output_file, 'w')
        print("\nGnome terminal theme")
        colors = []
        for i in range(15):
            colors.append('#ABCD' + '{0:02d}'.format(i))
        bg = "#010101"
        fg = "#ABABAB"

        for i, c in enumerate(colors):
            print('COLOR_' + '{0:02d}'.format(i+1) + '="' + c + '"')

        print('BACKGROUND_COLOR="' + bg + '"')
        print('FOREGROUND_COLOR="' + fg + '"')
        print('CURSOR_COLOR="$FOREGROUND_COLOR"')
        print('PROFILE_NAME="HapyColor"')

        # f.close()


    def vim(output_file, palette):
        header = '''
set background=dark
if exists("syntax_on")
    syntax reset
endif
let g:colors_name = "hapycolor"'''

        groups = [["Normal"],
                  ["Comment"],
                  ["Boolean"],
                  ["Character", "Keyword"],
                  ["Number"],
                  ["String"],
                  ["Conditional", "Macro"],
                  ["Constant", "Define"],
                  ["Cursor"],
                  ["Delimiter", "Directory"],
                  ["Error", "ErrorMsg", "Exception"],
                  ["Float"],
                  ["Function", "MatchParen"],
                  ["Identifier"],
                  ["Label","Operator"]]

        print(header)
        assert(len(palette) == len(groups))

        print("\n")
        for i, G in enumerate(groups):
            for g in G:
                print("hi " + g + "\tguifg=" + palette[i])
            print()



palette = ["#010101", "#101010", "#101010", "#101010", "#101010", "#101010", "#101010",
           "#101010", "#101010", "#101010", "#101010", "#101010", "#101010", "#101010",
           "#101010"]
# ProfileGenerator.vim("test.vim", palette)

pe = ProfileGenerator()
colors = [(c, c, c) for c in range(16)]
pe.iterm(colors, "IncreaseColor")
