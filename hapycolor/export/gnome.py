from hapycolor import config
from hapycolor import helpers

import subprocess

class Gnome:

    @staticmethod
    def profile(palette, name):
        """
            Creates a Gnome Terminal profile
            Requires a 18 colors palette in hexadecimal format
        """

        colors = map(lambda x: rgb_to_hex[1:], palette['colors'])
        fg = rgb_to_hex(palette['foreground'])[1:]
        bg = rgb_to_hex(palette['background'])[1:]

        print(colors, fg, bg)

        open('./tmp', 'a').close()
        with open('./tmp', 'w') as f:
            for c in colors:
                f.write('%s\n' % c)
            f.write('%s' % bg)
            f.write('%s' % fg)
            f.close()

        process = subprocess.Popen('bash ./export_gnome.sh "' + name + ' ./tmp ' + saved_profiles_path, shell=True, stdout=subprocess.PIPE)
        out = process.terminate()
        err_code = process.returncode

        return err_code
