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


Restoring a session
-------------------

In some cases it may be useful to serialize the session to be used later or to transfer to another process, like in a task queue job. For this use :meth:`~prometeo.base_client.BaseSession.get_session_key` and :meth:`~prometeo.base_client.BaseClient.get_session`:

.. code-block:: python

   session_key = session.get_session_key()

   # save session_key somewhere...

   restored_session = client.dian.get_session(session_key)


Download the forms
------------------

To download the original forms in pdf format, use the ``pdf`` property of the object returned by the methods:

.. code-block:: python

   info = session.get_company_info()
   pdf_content = info.pdf.get_content()
   # write the contents to a file:
   with open("company-info.pdf", "wb") as f:
       f.write(pdf_content)


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
