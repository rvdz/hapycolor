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
    pip3 install . --user


Requirements
------------

- python >= 3.5
- imagemagick
- feh (Linux only)

Debian or Ubuntu
^^^^^^^^^^^^^^^^

.. code-block:: shell

    sudo apt-get update && sudo apt-get install python3 python3-pip imagemagick feh -y

macOS
^^^^^

With homebrew_:

.. code-block:: shell

    brew install python3 python3-pip imagemagick

.. _homebrew: https://brew.sh

Usage
-----
For basic usage, execute:

.. code-block:: shell

    hapycolor -f <path/to/file>

The full documentation of Hapycolor's cli can be found by running:

.. code-block:: shell

    hapycolor --help

Test
----

To run the tests locally, excute:

.. code-block:: shell

    python3 setup.py test

