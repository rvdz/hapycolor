from hapycolor import config
from hapycolor import exceptions
from hapycolor import targets
from hapycolor.targets.iterm import Iterm
from hapycolor.targets.vim import Vim
from hapycolor.targets.wallpaper import Wallpaper

from tests.helpers import configurationtesting, retrytesting, disableprints
from tests.test_iterm import itermtesting
from tests.test_vim import vimtesting

from unittest.mock import patch
import unittest

class TestIntegrationConfiguration(unittest.TestCase):
    @vimtesting(fails=1)
    @retrytesting(retries=0)
    @configurationtesting()
    @disableprints()
    def test_vim_intialization_failed_attempt_and_abort(self):
        try:
            targets.initialize_target(Vim)
        except Exception as e:
            self.fail(str(e))
        self.assertFalse(Vim.is_enabled())

    @configurationtesting()
    @retrytesting(retries=1)
    @vimtesting(fails=2)
    @disableprints()
    def test_vim_intialization_two_failed_attempts_and_abort(self):
        try:
            targets.initialize_target(Vim)
        except Exception as e:
            self.fail(str(e))
        self.assertFalse(Vim.is_enabled())

    @vimtesting(fails=1)
    @configurationtesting()
    @retrytesting(retries=1)
    @disableprints()
    def test_vim_intialization_one_failed_attempt_and_success(self):
        try:
            targets.initialize_target(Vim)
        except Exception as e:
            self.fail(str(e))
        self.assertTrue(Vim.is_enabled())
