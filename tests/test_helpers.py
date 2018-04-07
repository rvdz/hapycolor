from hapycolor import helpers
import os
import unittest


class TestHelpers(unittest.TestCase):
    def test_is_hex_valid(self):
        colors = ["0x123456", "0X234567", "0x12afDC"]
        for c in colors:
            self.assertTrue(helpers.is_hex(c))

    def test_is_hex_invalid(self):
        colors = ["asdf", "", "123456", "abcdef", "0x12345", "0x12345G"]
        for c in colors:
            self.assertFalse(helpers.is_hex(c))

    def test_hsl_to_rgb_1(self):
        colors = []
        colors.append((0, 0, 0))
        colors.append((360, 1, 1))
        colors.append((22, 0.111111111111, 0.99999))
        for c in colors:
            self.__test_rgb_color(helpers.hsl_to_rgb(c))

    def __test_rgb_color(self, color):
        self.assertEqual(len(color), 3)
        for c in color:
            self.assertTrue(0 <= c and c <= 255)

    def __test_hsl_color(self, color):
        self.assertEqual(len(color), 3)
        self.assertTrue(0 <= color[0] and color[0] <= 360)
        self.assertTrue(0 <= color[1] and color[1] <= 1)
        self.assertTrue(0 <= color[2] and color[2] <= 1)

    hsl_rgb_dict = {
            (34, 0.33, 0.8): (221, 206, 187),
            (0, 0, 0): (0, 0, 0),
            (58, 0.12, 0.55): (154, 153, 126),
            (120, 0.68, 0.17): (14, 73, 14),
            (0, 0, 1): (255, 255, 255),
            (84, 0.1, 0.1): (26, 28, 23),
       }

    def test_hsl_to_rgb_2(self):
        for hsl1, rgb2 in TestHelpers.hsl_rgb_dict.items():
            with self.subTest(line=hsl1):
                rgb1 = helpers.hsl_to_rgb(hsl1)
                self.assertAlmostEqual(rgb1[0], rgb2[0], 4)
                self.assertAlmostEqual(rgb1[1], rgb2[1], 5)
                self.assertAlmostEqual(rgb1[2], rgb2[2], 5)

    def test_rgb_to_hsl(self):
        for hsl1, rgb2 in TestHelpers.hsl_rgb_dict.items():
            with self.subTest(line=hsl1):
                hsl2 = helpers.rgb_to_hsl(rgb2)
                self.assertAlmostEqual(hsl1[0], hsl2[0], 1)
                self.assertAlmostEqual(hsl1[1], hsl2[1], 2)
                self.assertAlmostEqual(hsl1[2], hsl2[2], 2)

    def test_hex_to_rgb(self):
        colors = {
               "#000000": (0, 0, 0),
               "#FFFFFF": (255, 255, 255),
               "#89ABCD": (137, 171, 205),
            }
        for c in colors:
            self.assertEqual(helpers.hex_to_rgb(c), colors[c])

    tmp_file = "/tmp/test_save_json.json"
    hello_world = {
            "asdf": """asaasaasssasaasssasaaaasssasaasssasaaaaaaaasssasaaaasss
asaaaasssasaasssasaasssasaasssasaasssasaaaasssasaasssasaaaasssasaaaaaasssasaaaa
sssasaasssasaaaasssasaaaaaasssasaaaasssasaasssasaaaaaaaasssasaaaasssasaasssasaa
sssasaaaasssasaaaaaaaasssasaasssasaaaaaaaaaaaasssasaaaaaasssasaasssasaaaaaasssa
saasssasaaaasssasaasssasaaaaaaaasssasaasssasaaaaaasssasaaaasssasaasssasaaaasssa
saaaasssasaasssasaaaasssasaaaaaasssasaaaasssasaaaasssasaasssasaaaaaaaasssasaass
sasaaaaaaaasssasaa""",
            "Aubergine": """=aA-a1=oA=bi+b1-Ab-bb:bA+B1=iBGolf by Quintopia
!dlroW ,olleH""",
           "Beatnik": """Soars, larkspurs, rains.
Indistinctness.
Mario snarl (nurses, natures, rules...) sensuously retries goal.
Agribusinesses' costs par lain ropes (mopes) autos' cores.
Tuner ambitiousness.
Flit.
Dour entombment.
Legals' saner kinking lapse.
Nests glint.
Dread, tied futures, dourer usual tumor grunts alter atonal
  garb tries shouldered coins.
Taste a vast lustiness.
Stile stuns gad subgroup gram lanes.
Draftee insurer road: cuckold blunt, strut sunnier.
Rely enure pantheism: arty gain groups (genies, pan) titters, tattles, nears.
Bluffer tapes?  Idle diatom stooge!
Feted antes anklets ague?  Remit goiter gout!
Doubtless teared toed alohas will dull gangs' aerials' tails' sluices;
Gusset ends!  Gawkier halo!

Enter abstruse rested loser beer guy louts.
Curtain roams lasso weir lupus stunt.
Truant bears animate talon.  Entire torte originally timer.
Redo stilt gobs.

Utter centaurs;
Urgent stars;
Usurers (dilute);
Noses;
Bones;
Brig sonar graders;
Utensil silts;
Lazies.
Fret arson veterinary rows.

Atlas grunted: "Pates, slues, sulfuric manor liaising tines,
  trailers, rep... unfair!  Instant snots!"

Sled rested until eatery fail.
Ergs fortitude
  Indent spotter
Euros enter egg.
Curious tenures.
Torus cutlasses.
Sarong torso earns cruel lags it reeled.

Engineer: "Erase handbag -- unite ratification!"

oaring oaten donkeys unsold, surer rapid saltest tags
BUTTERED TIBIA LUGS REWIRING TOILETS
anion festers raring edit epilogues.
DIRGE ROTOR.
linnet oaring.
GORE BOOTIES.
Ironed goon lists tallest sublets --
Riots,
Raucous onset.

Ignobly, runners' diet anguishes sunrise loner.
Erode mob, slier switcher!
Loaners stilt drudge pearl atoll, risking hats' ends.

Rebind sitters.

Toga epistles -- crud lard.  (Pager purse dons souls.)

glob title a curio hired rites shed suds lade grease strut arctic revs toad
unless idlers rind stilt region land GERMICIDES SULTANA GUTS gill siting leans
nice spurs
tests gloves
roused asp

Holes!  Moles!  (Sores!)
Hygienists!  Scars!  (Asses!)
Smells spell rares.

Cubs instant sing in parse goodies.
Rosin.  Unhelpful sisal acres.  Slope told.
MALENESS PASTA LAB.  "Infirmary vine," rang illiterates (beans).
Rosin sours, insults truss abalones, nailed rules, helical atlases.
Dear remodeling stings mar rents.
Sunless shiner orb (silly idol.)
Clarity disses senna.
Vagabonds sauted; sloes performed gelds.
Alter post radial lip sectioning gums.
Saint Towellings.
Larger aeons telephone stolid char, pal!
Boats Dean forsook, rosters, tunas, terrariums -- united, traced.
Nude pagoda careens.""",
            "Brainfuck": """++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+
++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>."""
    }

    def test_save_json(self):

        try:
            helpers.save_json(TestHelpers.tmp_file, TestHelpers.hello_world)
            os.remove(TestHelpers.tmp_file)
        except Exception as err:
            self.fail(str(err))

    def test_load_json(self):
        try:
            helpers.save_json(TestHelpers.tmp_file, TestHelpers.hello_world)
            self.assertEqual(helpers.load_json(TestHelpers.tmp_file),
                             TestHelpers.hello_world)
            os.remove(TestHelpers.tmp_file)
        except Exception as err:
            self.fail(str(err))
