Installation
============

Hapycolor can be installed with `pip`, or by cloning this repository.

Pip install
-----------

.. code-block:: shell

    pip3 install hapycolor

Git install
-----------

.. code-block:: shell

    git clone https://github.com/rvdz/hapycolor
    cd hapycolor
    python3 setup.py install

If you don't have sudoers permissions, then run:

.. code-block:: shell

    python3 setup.py install --user

Then, you should add the generated binary in your $PATH. To do so, execute
the following command or add it in your bashrc or zshrc.

.. code-block:: shell

    export PATH=<path/to/bin>:$PATH

For more information, please check: `Installing Python Modules`_.

.. _`Installing Python Modules`: https://docs.python.org/3.6/install/index.html#alternate-installation.


Requirements
------------

- python >= 3.5
- imagemagick
- feh (only for Linux)

Debian or Ubuntu
^^^^^^^^^^^^^^^^

.. code-block:: shell

    sudo apt-get update && sudo apt-get install feh python3 python3-pip imagemagick -y

macOS
^^^^^

With homebrew_:

.. code-block:: shell

    brew install python3 python3-pip imagemagick

.. _homebrew: https://brew.sh

Test
----

To run the tests locally, excute:

.. code-block:: shell

    python3 tests/run_suite.py --verbose <0-3>

To run the tests on a clean Debian Stretch image, you can build and run
the provided dockerfile:

.. code-block:: shell

    make build
    make run

The created container can be stopped by running:

.. code-block:: shell

    make stop
