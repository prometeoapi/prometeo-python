Banking API
===========


Initialize the client
---------------------

To initialize the client you'll need to provide your api key and the environment (either ``testing`` or ``production``)

.. code-block:: python

    from prometeo import Client

    client = Client('<YOUR_API_KEY>', environment='testing')


Log in
------


.. code-block:: python

    session = client.banking.login(
        provider='test',
        username='12345',
        password='gfdsa'
    )


To get a list of available provider codes, use :meth:`~prometeo.banking.client.BankingAPIClient.get_providers`


Select client
-------------

In some banks a user can have access to more than one profile (called client), in those cases, the session status after login will be ``select_client``. It is then necessary to select the client, for that, first list the available clients and pass one to ``session.select_client``

.. code-block:: python

   if session.get_status() == 'select_client':
       clients = session.get_clients()
       session.select_client(clients[0])
       assert session.status == 'logged_in'


If the bank doesn't uses multiple clients, calling ``get_clients`` will return an empty list.


Handling security questions and OTPs
------------------------------------

In cases where the bank requires additional steps to login, such as answering a personal security question or using a 2FA device like an :abbr:`OTP (One Time Password)`, the status of the session will be set as ``interaction_required``, which can be handled like this:

.. code-block:: python

   session = client.login(provider='test', username='user', password='pass')
   if session.get_status() == 'interaction_required':
       # necessary context, like the security question to answer.
       print(session.get_interactive_context())
       session.finish_login(
           provider='test',
           username='user',
           password='pass',
           answer='1234',
       )


Listing accounts and movements
------------------------------

.. code-block:: python

   from datetime import datetime

   accounts = session.get_accounts()
   for account in accounts:
       movements = account.get_movements(
           datetime(2019, 2, 1), datetime(2019, 15, 1)
       )


For more detailed information, refer to the docs for :meth:`~prometeo.banking.client.Session.get_accounts` and :meth:`~prometeo.banking.client.Account.get_movements`


Listing credit cards and their movements
----------------------------------------

Credit cards can have movements in more than one currency, so it's necessary to specify it when listing movements.

.. code-block:: python

   from datetime import datetime

   cards = session.get_credit_cards()
   for card in cards:
       movements = card.get_movements(
           'USD', datetime(2019, 2, 1), datetime(2019, 15, 1)
       )


Listing available banks
-----------------------

We recommend that the list of available banks be stored on a database and updated weekly.

.. code-block:: python

   providers = client.banking.get_providers()
