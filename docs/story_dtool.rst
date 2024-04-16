User stories that lead to *dtool*
=================================

Packaging data and metadata into a unified whole
------------------------------------------------

*“As an individual student or researcher, I want to keep data and its
documentation together according to best RDM practices. I am trying to
get into the habit of naming folders and files in a somewhat
standardised way and keeping notes on folder contents in README files
and I just want a little tool that formalises this good practice.”*

The core of good data management is data documentation
`[16] <https://paperpile.com/c/s8ZTYM/km0e>`__. Thus, bundling data and
documentation into a unified whole lies at the core of decentralised
data management ecosystems. *dtool* is no exception and the design
decisions for the *dtool* *dataset* have been described in detail by
Olsson and Hartley `[3] <https://paperpile.com/c/s8ZTYM/LcXt>`__.
Importantly, the datasets hold administrative (such as username, date of
creation, or file sizes) and descriptive (such as experimental
conditions or simulation parameters) metadata in machine-processable
plain text formats such as JavaScript Object Notation (JSON)
`[17] <https://paperpile.com/c/s8ZTYM/BvRD>`__ and Yet Another Markup
Language (YAML) `[18] <https://paperpile.com/c/s8ZTYM/epGs>`__. A
dataset’s README.yml file contains descriptive metadata that should be
formatted as machine-processable YAML. Plain text is not strictly
forbidden, but the file extension strongly encourages the use of YAML. A
dataset’s *manifest* holds structural metadata on all files contained
within the dataset. Each dataset contains documentation on its own
structure to make itself understandable even in the absence of any
*dtool* software. In the following, we will refer to aforementioned
descriptive and structural metadata as a dataset’s *readme* and a
dataset’s *manifest* respectively.

Abstraction of storage infrastructure
-------------------------------------

*“As a junior researcher, building my career means jumping from
institution to institution every few years. With every move, the
available storage infrastructure around me changes. I want to take my
data with me and store it on whatever storage infrastructure I have at
hand without the need to adapt my data handling workflows with every
environmental change.”*

*“As a senior group leader, the landscape of IT services around me
evolves at a much faster pace than my own research. 20 years ago, we
archived data on our own hard drives. 10 years ago, we started using
Windows shares provided by my institution’s central compute services.
Today, we use object storage for that purpose. Who knows what other
technology comes around in the next few years. Similar to the junior
researcher, I want to hold my group’s data on whatever storage
infrastructure I have at hand without the need to adapt our data
handling workflows with every technological change.”*

*dtool* abstracts away the storage infrastructure layer. At the core is
a set of atomic operations on datasets, like dataset creation or
copying. These operations are interfaced by simple shell commands like
dtool create or dtool cp or according Python API calls. *Storage
brokers* are responsible for translating these atomic actions to actual
operations on the underlying storage infrastructure of a specific
*storage endpoint*. Within the *dtool* context, a *storage endpoint* is
referred to as *base uniform resource identifier (base URI)*. Examples
of base URIs are,

-  file:///path/to/repository,

-  s3://some-bucket or

-  smb://some-network-share.

The base URI consists of a *scheme* that determines the *storage
broker*, in these examples file for the local storage, s3 for Amazon’s
Simple Storage System API and smb for Microsoft Windows Server Message
Block protocol, followed by a resource endpoint name like a server name
or a location within the specific storage system. The generic base URI
hence adheres to

{scheme}://{storage_endpoint_name}

A simple command like

dtool cp /path/to/local/dataset smb://group-wide-share

will copy a dataset from the local file system to a preconfigured
Windows network share.

Self-documentation
------------------

*“As an archivist, I want future generations of archivists to understand
a dataset’s contents, even if software for creating and reading the
specific dataset format is no longer available.”*

Datasets are understandable in their raw representation on a specific
storage system. Storage brokers are required to attach a simple textual
description and a machine-readable structure documentation of the
dataset representation specific to the storage infrastructure specific
to each dataset instance. For the example of hierarchical file systems,
textual description and machine-readable structural documentation are
found within the .dtool/README.txt and .dtool/structure.json files,
respectively.

URI, UUID, and freezing
-----------------------

*“As a researcher, I may have a copy of the same dataset on my local
machine, and another copy on my institution’s shared storage. I need to
uniquely identify those copies as the same dataset, but distinguish
their storage locations.”*

*“As a researcher that produces data in volumes at the order of GB per
single dataset and TB per year, I do not need the overhead of
sophisticated versioning. I just need a mechanism to distinguish between
incomplete and complete datasets. Once complete, I want to be able to
check the integrity of the dataset to identify if it has become
corrupted over time.”*

*“As a scientist, I regard data obtained from an experiment as
immutable. ”*

A dataset is globally identified by its universal unique identifier
(UUID). Instances of the same dataset may exist at several base URIs.
The consistency of a dataset across multiple instances is verifiable by
hashes that are stored in the manifest and computed when a *prototype*
dataset is made immutable by *freezing*. One instance of a dataset at a
particular storage location is uniquely identified by its URI. This URI
is composed of the base URI and a locally unique identifier, i.e. a
local folder name file:///home/my-user/some-dataset or the UUID as a
suffix s3://some-bucket/1a1f9fad-8589-413e-9602-5bbd66bfe675.

The generic scheme of a dataset URI hence adheres to

{scheme}://{storage_endpoint_name}/{localized_dataset_id}

Encouraging, not enforcing standardised metadata
------------------------------------------------

*“As a group leader, I want to encourage my group to stick to a few
simple, extensible bibliographic metadata fields such as data owners and
funding body information.”*

This is achieved by distributing README.yml templates such as

.. code-block::yaml
    project: Project name
    description: Project description
    owners:
    - name: Johannes L. Hörmann
      email: johannes.hoermann@imtek.uni-freiburg.de
      orcid: 0000-0001-5867-695X
    funders:
    - organisation: Deutsche Forschungsgemeinschaft (DFG)
      program: Clusters of Excellence
      code: EXC 2193

and recommending or requiring their use among group members.