Account Validation API
======================

Validate Account
----------------

The following is a list of accounts defined for the sandbox environment:

.. list-table:: Sandbox Accounts
   :header-rows: 1
   :widths: 10 20 10 10 10 10 10 20

   * - **Example**
     - **account_number**
     - **bank_code**
     - **country_code**
     - **branch_code**
     - **account_type**
     - **document_number**
     - **document_type**

   * - Example for MX (Local)
     - `0`
     - `999`
     - `MX`
     - `000`
     - 
     - 
     - 

   * - Example for MX (CLABE)
     - `999000000000000001`
     - 
     - `MX`
     - 
     - 
     - 
     - 

   * - Example for BR (Local)
     - `1001`
     - `999`
     - `BR`
     - `00001`
     - `CHECKING`
     - `58.547.642/0001-95`
     - `CPF/CNPJ`

   * - Example for BR (IBAN)
     - `BR7299999999010100000001001C1`
     - 
     - `BR`
     - 
     - 
     - `58.547.642/0001-95`
     - 

   * - Example for PE (CCI)
     - `99900000000000000030`
     - 
     - `PE`
     - 
     - 
     - 
     - 

   * - Example for PE (Local)
     - `000000000000000`
     - `999`
     - `PE`
     - 
     - 
     - 
     - 

   * - Example for UY (Local)
     - `0000`
     - `999`
     - `UY`
     - 
     - 
     - 
     - 

Here is an example of a valid account:

.. code-block:: python

    from prometeo import Client

    # Initialize the Prometeo client with your API key and set the environment to 'sandbox'
    client = Client('<YOUR_API_KEY>', environment='sandbox')

    data = client.account_validation.validate(
        account_number="1001",
        country_code="BR",
        document_number="58.547.642/0001-95",
        branch_code="00001",
        bank_code="999",
        account_type="CHECKING",
    )

    print(data.beneficiary_name)
    # "JOÃO DAS NEVES"
    print(data.account_type)
    # "CHECKING"
    print(data.account_type)

Here is an example of an invalid account:

.. code-block:: python

    from prometeo import Client
    from prometeo.account_validation import exceptions

    # Initialize the Prometeo client with your API key and set the environment to 'sandbox'
    client = Client('<YOUR_API_KEY>', environment='sandbox')

    try:
        data = client.account_validation.validate(
            account_number="1002",
            country_code="BR",
            document_number="58.547.642/0001-95",
            branch_code="00001",
            bank_code="999",
            account_type="CHECKING",
        )
    except exceptions.InvalidAccountError as e:
        print(e.message)
