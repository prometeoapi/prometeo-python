CURP API
========


Checking the existence of a curp
--------------------------------

.. code-block:: python

   from prometeo import Client
   from prometeo.curp import exceptions

   client = Client('<YOUR_API_KEY>', environment='sandbox')
   try:
       result = client.curp.query('ABCD12345EFGH')
   except exceptions.CurpError as e:
       print("CURP does not exist:", e.message)


Looking for a CURP by personal info
-----------------------------------

.. code-block:: python

    from datetime import datetime
    from prometeo.curp import exceptions, Gender, State

    curp = 'ABCD12345EFGH'
    state = State.SINALOA
    birthdate = datetime(1988, 3, 4)
    name = 'JOHN'
    first_surname = 'DOE'
    last_surname = 'PONCE'
    gender = Gender.MALE
    try:
        result = client.curp.reverse_query(
            state, birthdate, name, first_surname, last_surname, gender
        )
    except exceptions.CurpError as e:
        print("CURP does not exist:", e.message)


Check the :doc:`reference </api/curp>` for a list of possible values for ``State``
