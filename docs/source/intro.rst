What is Hapycolor?
==================

.. _intro_label:

Introduction
------------
At the beginning, there was patience, frustration and despair. But one day, `dylanarps <https://github.com/dylanaraps>`_
said: "Let there be Instant `Rice <https://www.reddit.com/r/unixporn/wiki/index>`_!", and `wal <https://github.com/dylanaraps/pywal>`_ was born.
Ricers from all over the world were excited by such promise, but, unfortunately, their hopes did not match the
cruel reality of ricing's nature. The idea was there, but its implementation did not stood up to its aspirations.
Maybe Instant Ricing will remain a forever untouchable software `Shangri-La <https://en.wikipedia.org/wiki/Shangri-La>`_?

Hapycolor is bringing Instant Ricing to reality
-----------------------------------------------
In our quest to Ricing's mystic graal, we devised numerous ingenious techniques that solved wal's lack of color processing,
and more. Hence, we believe that Hapycolor is on the way to accomplish the ancients' prophecy.

It is now possible to finely configure its own environment with one single command, just choose an image,
feed it to Hapycolor, *et voilà*!

Currently, there are two main color filters: a first which filters out the colors that are too bright, too dark
or not enough saturated (see :ref:`filter_label`), and a second one, that cleverly removes the colors that are
too close to one another (see :ref:`reduction_label`).

Then, the generated palette is sent to compatible targets, which carefully distribute the colors according
to their own logic.

In addition, Hapycolor has a new approach on how to export the generated palette to a target.
Instead of exporting the generated palette throughout the system, Hapycolor aims at creating new
profiles in the target's configuration without altering the previous version or creating/overriding
global environment variables. E.g, this project deals with `iTerm <https://iterm2.com/>`_'s preferences and creates a new profile
with associated to the image's name. Moreover, a wise algorithm has been implemented in order to match the colors
to the sixteen colors of the profile (see
`Standard colors and High-intensity colors <https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit>`_) which
makes the most out of generated range of colors.

Is it an illusion?
------------------
In the light of these arguments, an experienced ricer, should remain skeptical, and must wonder if the concept of
"Instant Ricing" is an abomination, an illusion or even a shame to this Art. As I mentioned previously,
what is considered as an "accomplished" rice, is the result of hard work, "patience, frustration and despair"
(see :ref:`intro_label`). But also satisfaction.

Furthermore, by bringing to life this bestiality, professional ricers might worry that the new generations will easily give in to
tentation, by choosing the deceptive simplistic path, over the slow, winding, but genuine one. I can already hear
the doomsayers foreshadowing the fall of the authentic Art of Racing, which will be forever forgotten.

Besides, the feeling of satisfaction can never be felt by just launching a single command, or else, it
would be an erroneous perception. So, Hapycolor would also deprive its user from this pleasure.

Did we kill the Art of Ricing?

Synthesis
---------

.. todo:: Find a better title

These relevant arguments forget one essential trait of the accomplished Ricer. Indeed, a True Ricer would
spot a subtle mistake in the last sentence, since this artistry has no end, and thus, one can not claim to have reached
the ultimate state of enlightenment.

Therefore, after launching the first command, the user will not be completely satisfied by the result and will
go on tweaking his environment, starting the never ending creative process. Hence, the term "Instant Rice" is
only a hallucination or a short-circuited consideration.

Besides, we did rice by working on Hapycolor, we experimented and explored new territories, from color theory to
the arcane mechanics of `dconf <https://en.wikipedia.org/wiki/Dconf>`_. This path was full of contention,
surprise, patience and achievements.

Moreover, Hapycolor has been designed to be a collaborative project where it is easy to add new color filters
or new targets. This means that it provides new tools upon which ricers can walk the Trail, and share easily
their knowledge and work.

tl;dr?
------
Hapycolor is an tool that helps ricers to efficiently configure their system from a selected image, according
to their will, in addition of benefiting from other people's work. In particular through the choice of
color filters and targets.
