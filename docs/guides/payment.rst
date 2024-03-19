Payment API
===========

Create a Payment Intent
-----------------------

To create a payment intent, you can use the ``create_intent`` method provided by the ``Client`` class in the Prometeo library. Here's an example:

.. code-block:: python

   from prometeo import Client

   # Initialize the Prometeo client with your API key and set the environment to 'production'
   client = Client('<YOUR_API_KEY>', environment='production')

   # Specify the necessary parameters for creating a payment intent
   widget_id = '<YOUR_WIDGET_ID>'
   data = client.payment.create_intent(
       widget_id=widget_id,
       currency="USD",
       amount="1.00",
       external_id=None,
       concept="PROM123452 REF454243",
       bank_codes=["test"],
   )

   # Print the generated payment intent ID
   print("Intent ID:", data.intent_id)


Get a Payment Intent by ID
---------------------------

To retrieve details about a specific payment intent, you can use the ``get_transaction_data`` method. Provide the payment ID as an argument. Here's an example:

.. code-block:: python

   from prometeo import Client

   # Initialize the Prometeo client with your API key and set the environment to 'production'
   client = Client('<YOUR_API_KEY>', environment='production')

   # Specify the payment ID for the desired payment intent
   payment_id = "<PAYMENT_ID>"
   data = client.payment.get_transaction_data(payment_id)


Additional Reference
--------------------

For more details on the Payment API and available parameters, refer to the :doc:`complete API reference </api/payment>`.
