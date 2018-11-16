.. rassh documentation master file, created by
   sphinx-quickstart on Mon Nov 13 18:21:36 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to rassh
================

Rassh is a Python framework for making REST APIs for command line systems. It includes an API for configuring "Bonaire-compatible" wireless controllers, which include the `Aruba Mobility`_ controller platform.

Introduction
------------

Rassh is a small set of Python scripts to assist in automating command line connections using expect. The intention is to hide an expect-capable system behind a REST API (as in the façade pattern). The REST APIs are built using flask-restful_. The expect connections are controlled using Pexpect_.

Because it may be desirable to know that configuration has been completed successsfully or has failed, a "feedback" REST API is also included.

A use case is described in which an application server needs to send commands to an SSH-managed resource.

Example usage
-------------

Rassh is installed on both the application server which needs to access an command line resource, and an API server (proxy) which runs the rassh REST API. This allows the application server to communicate intentions using http put and get commands, without needing direct access to the command line server. The command line server can then be protected (to a degree) from malicious connections using (for example) a firewall.

In the example, a web application server is used to manage a system which is configured via SSH. A web-based user interface (not provided) alows users to update system configuration options, and these options are stored in a configuration database. Rassh is then used to read and / or update the configuration on the managed system.

Sometimes, it may not be possible for rassh to run commands immediately. For example, the managed system may be busy or in another state that prevents configuration. In this case, rassh will enqueue commands and run them when the managed system is next available (the default is to retry every 2 minutes).

Rassh has the option of sending "feedback" to the application server via another REST API which can be run on the application server. If feedback is enabled when the managed system is updated, rassh will make an http put request back to the feedback API indicating the result of the update. The feedback API will then update the configuration database to note that configuration was successful.

.. image:: rassh.svg



.. toctree::
   :maxdepth: 2
   :caption: Contents:

   source/modules.rst



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _flask-restful: https://flask-restful.readthedocs.io/en/latest/
.. _Pexpect: https://pexpect.readthedocs.io/en/stable/
.. _`Aruba Mobility`: http://www.arubanetworks.com/en-gb/products/networking/controllers/
