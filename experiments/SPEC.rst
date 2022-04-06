Architectural restructuring specification
=========================================

User stories
------------

As a systems administrator tasked with installing and evaluating the
dtool-lookup-server I want to be able to install a minimal working system using
as few commands, databases and environment variables as possible so that I can
get a proof of concept up and running as quickly as possible.

As a DevOps engineer tasked with installing and maintaining a
dtool-lookup-server I want to be able to configure it to run in a way that is
consistent with my other production systems to keep my tool chain as lean and
consistent as possible. The dtool-lookup-server should therefore not have
strong opinions on things like systemd, docker-compose, kubernetes. Rather it
should be able to fit into any of these systems.

As a software engineer tasked with making a cloud native implementation of the
dtool-lookup-server I want to be able to swap out any components that rely on
databases so that I can make my own plug-ins that use cloud databases to
replace these components.

As a software engineer tasked with extending the dtool-lookup-server with new
functionality I want to be able to develop my own Python package that plugs
into the system without having to touch any of the code used to run the base
installation of the dtool-lookup-server, and I want to have access to abstract
base classes to inherit from to help guide my development efforts.

As a consumer of the dtool-lookup-server REST API I want to be able to create
clients that auto-discover the API to make it easier to maintain the clients
when the dtool-lookup-server REST API is updated.


Further reading
---------------

- `The Tweleve-Factor App <https://12factor.net/>`_
