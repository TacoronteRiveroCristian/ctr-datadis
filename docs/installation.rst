Installation
============

Requirements
------------

* Python 3.8+
* Internet connection for API access

Install from PyPI
-----------------

The easiest way to install the Datadis Python SDK is via pip:

.. code-block:: bash

   pip install datadis-python

Using Poetry
------------

If you're using Poetry for dependency management:

.. code-block:: bash

   poetry add datadis-python

Development Installation
------------------------

For development or to get the latest features:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/your-username/datadis-python.git
   cd datadis-python

   # Install with Poetry
   poetry install

   # Activate virtual environment
   poetry shell

Verify Installation
-------------------

To verify that the installation was successful:

.. code-block:: python

   import datadis_python
   print(datadis_python.__version__)

Dependencies
------------

The SDK has the following main dependencies:

* ``requests`` - For HTTP requests
* ``pydantic`` - For data validation and serialization
* ``python-dateutil`` - For date parsing

All dependencies are automatically installed when you install the package.