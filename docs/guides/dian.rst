DIAN API
========


Log in
------

Initialize the client:

.. code-block:: python

    from prometeo import Client
    from prometeo.dian import DocumentType

    client = Client('<YOUR_API_KEY>', environment='testing')

Supply the NIT to log in as a company

.. code-block:: python

    session = client.dian.login(
        nit='098765',
        document_type=DocumentType.CEDULA_CIUDADANIA,
        document='12345',
        password='test_password',
    )

Or omit it to log in as a person:

.. code-block::

    session = client.dian.login(
        document_type=DocumentType.CEDULA_CIUDADANIA,
        document='12345',
        password='test_password',
    )

Check the :doc:`reference </api/dian>` for a list of possible values for ``DocumentType``


Getting the data
----------------

Company info (form 001):

.. code-block:: python

   session.get_company_info()

Balances:

.. code-block:: python

   session.get_balances()

Rent declaration:

.. code-block:: python

   session.get_rent_declaration(2019)

VAT declaration:

.. code-block:: python

   from prometeo.dian import Periodicity, QuartlerlyPeriod

   session.get_vat_declaration(2019, Periodicity.QUARTERLY, QuartlerlyPeriod.JANUARY_APRIL)

Numeration:

.. code-block:: python

   from datetime import datetime
   from prometeo.dian import NumerationType

   session.get_numeration(
       NumerationType.Authorization,
       datetime(2019, 1, 1),
       datetime(2019, 5, 1)
   )

Retentions:

.. code-block:: python

   from prometeo.dian import MonthlyPeriod

   session.get_retentions(2019, MonthlyPeriod.NOVEMBER)