SAT API
=======

Log in
------

.. code-block:: python

   from prometeo.sat import LoginScope

   session = client.sat.login(
       rfc='ABCD1234EFGH',
       password='password',
       scope=LoginScope.CFDI,
   )


Restoring a session
-------------------

In some cases it may be useful to serialize the session to be used later or to transfer to another process, like in a task queue job. For this use :meth:`~prometeo.base_client.BaseSession.get_session_key` and :meth:`~prometeo.base_client.BaseClient.get_session`:

.. code-block:: python

   session_key = session.get_session_key()

   # save session_key somewhere...

   restored_session = client.sat.get_session(session_key)


Listing bills
-------------

To list emitted bills, supply a date range and the :class:`~prometeo.sat.client.BillStatus`

.. code-block:: python

    from prometeo.sat import BillStatus

    emitted_bills = session.get_emitted_bills(
        date_start=datetime(2020, 1, 1),
        date_end=datetime(2020, 2, 1),
        status=BillStatus.ANY,
    )


And for received bills, supply the year, month and the :class:`~prometeo.sat.client.BillStatus`

.. code-block:: python

    received_bills = session.get_received_bills(
        year=2020,
        month=1,
        status=BillStatus.ANY,
    )

Check the documentation for :class:`~prometeo.sat.models.CFDIBill` to see a list of all fields available for a bill.

Downlading bills
----------------

.. code-block:: python

   import time
   from prometeo.sat import BillStatus

   download_requests = session.download_emitted_bills(
       date_start=datetime(2020, 1, 1),
       date_end=datetime(2020, 2, 1),
       status=BillStatus.ANY,
   )
   for request in download_requests:
       while not request.is_ready():
           time.sleep(5)
       download = request.get_download()
       content = download.get_file().read()


Download acknowledgements
-------------------------

.. code-block:: python

   from prometeo.sat import Motive, DocumentType, Status, SendType

   acks = session.get_acknowledgement(
       year=2020,
       month_start=1,
       month_end=2,
       motive=Motive.ALL,
       document_type=DocumentType.ALL,
       status=Status.ALL,
       send_type=SendType.ALL,
   )
   for ack in acks:
       download = ack.download().get_file()
