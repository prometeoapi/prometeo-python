Banking API
===========


Initialize the client
---------------------

To initialize the client you'll need to provide your api key and the environment (either ``sandbox`` or ``production``)

.. code-block:: python

  from prometeo import Client

  client = Client('<YOUR_API_KEY>', environment='sandbox')
  session = client.banking.new_session()


Log in
------


.. code-block:: python

  session.login(
      provider='test',
      username='12345',
      password='gfdsa',
  )


To get a list of available provider codes, use :meth:`~prometeo.banking.client.BankingAPIClient.get_providers`

Because some banks require extra fields to log in, these must be provided inside ``kwargs`` as a dictionary. To see if a provider requires extra auth fields to log in, use :meth:`~prometeo.banking.client.BankingAPIClient.get_provider_detail`

Example with extra auth fields:

.. code-block:: python

  session.login(
      provider='test',
      username='12345otp',
      password='asdfg',
      otp=8888
  )

The following is a list of accounts defined for the sandbox environment:

.. list-table:: Sandbox Accounts
   :header-rows: 1
   :widths: 15 20 15 15 30

   * - **País**
     - **provider_code**
     - **username**
     - **password**
     - **MFA**

   * -
     - `test`
     - `12345`
     - `gfdsa`
     - 

   * -
     - `test`
     - `12345otp`
     - `asdfg`
     - Token - `8888`

   * -
     - `test`
     - `12345pq`
     - `asdfg`
     - Pregunta Personal - `8888`

   * - 🇺🇾 - Uruguay
     - `brou_pers_uy_mock`
     - `12345`
     - `asdfg`
     - Token - `prometeo`

   * - 🇵🇪 - Peru
     - `bcp_pers_pe_mock`
     - `12345`
     - `asdfg`
     - Token - `123456`

For all the additional fields check our documentation in `official docs <https://docs.prometeoapi.com/docs/introducci%C3%B3n-1>`_.

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

  session.login(provider='test', username='user', password='pass')
  if session.get_status() == 'interaction_required':
      # necessary context, like the security question to answer.
      print(session.get_interactive_context())
      session.finish_login(
          provider='test',
          username='user',
          password='pass',
          answer='1234',
      )


Restoring a session
-------------------

In some cases it may be useful to serialize the session to be used later or to transfer to another process, like in a task queue job. For this use :meth:`~prometeo.base_client.BaseSession.get_session_key` and :meth:`~prometeo.base_client.BaseClient.get_session`:

.. code-block:: python

  session_key = session.get_session_key()

  # save session_key somewhere...

  restored_session = client.banking.get_session(session_key)


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

  providers = session.get_providers()


Preprocess transfer
---------------------

.. code-block:: python

    preprocess = session.preprocess_transfer(
      origin_account='002206345988',
      destination_institution='0',
      destination_account='001002363321',
      currency='UYU',
      amount='1.3',
      concept='transfer description',
      destination_owner_name='John Doe',
      branch='62', 
    )

    print(preprocess)


Confirm transfer
---------------------

.. code-block:: python

  confirmation = session.confirm_transfer(
    request_id='0b7d6b32d1be4c11bde21e7ddc08cc36',
    authorization_type='cardCode',
    authorization_data='1, 2, 3',
  )

  print(confirmation)


List transfer institutions
--------------------------

.. code-block:: python

  institutions_list = session.list_transfer_institutions()
  for intitution in institutions_list:
    print(intitution)
