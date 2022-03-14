Prometeo Python API client
==========================

The official python package for the `Prometeo API <https://prometeoapi.com/>`_


Installation
------------

Install from PyPI using `pip <http://www.pip-installer.org/en/latest/>`_:

.. code-block:: bash

    $ pip install prometeo


Quick Start
-----------

Go to `your dashboard <https://test.prometeo.qualia.uy/dashboard/>`_, there you'll find your API key. Use it to instantiate the client:

.. code-block:: python

    from prometeo import Client

    client = Client('<YOUR_API_KEY>', environment='testing')


The ``environment`` argument is either ``sandbox`` for the sandbox or ``production`` for the production environment.

.. note::

   `Contact us <mailto:info@prometeoapi.com>`_ to get an api key!


Usage Guide
-----------

Guides for all the available services:

.. toctree::
   :glob:
   :maxdepth: 1

   guides/*


Reference
---------

.. toctree::
   :maxdepth: 2

   api


.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
