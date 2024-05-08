---
title: 'dtool-lookup-server: a REST API-centered Flask app for finding dtool datasets'
tags:
  - Python
  - Research data management
  - Findability
  - FAIR data
  - datasets
  - provenance
authors:
  - name: Johannes L. Hörmann
    orcid: 0000-0001-5867-695X
    affiliation: "1, 2" # (Multiple affiliations must be quoted)
  - name: Luis Yanes
    orcid: 0000-0003-1382-0166
    affiliation: 3
  - name: Ashwin Vazhappilly
    orcid: 0009-0009-6725-4367
    affiliation: "1, 2"
  - name: Lars Pastewka
    orcid: 0000-0001-8351-7336
    affiliation: "1, 2"
  - name: Matthew Hartley
    orcid: 0000-0001-6178-2884
    affiliation: 4
  - name: Tjelvar S. G. Olsson 
    orcid: 0000-0001-8791-4531
    corresponding: true # (This is how to denote the corresponding author)
    affiliation: 5
affiliations:
 - name: Cluster of Excellence livMatS, Freiburg Center for Interactive Materials and Bioinspired Technologies, University of Freiburg, Georges-Köhler-Allee 105, 79110 Freiburg, Germany
   index: 1
 - name: Department of Microsystems Engineering, University of Freiburg, Georges-Köhler-Allee 103, 79110 Freiburg, Germany
   index: 2
 - name: Earlham Institute, Norwich Research Park, Norwich NR4 7UZ, United Kingdom
   index: 3
 - name: European Molecular Biology Laboratory, European Bioinformatics Institute (EMBL-EBI), Hinxton, United Kingdom
   index: 4
 - name: John Innes Centre, Norwich Research Park, Norwich, NR4 7UH, United Kingdom
   index: 5
date: 18 April 2024
bibliography: paper.bib
---

Summary
=======

*dtool-lookup-server* is the core of a lean Flask app of the same name, or
short *dserver*. *dserver* provides a REST API for registering metadata for
*dtool* datasets and provides functionality to look up, list and search for
datasets.

Keywords: Research data management, Findability, FAIR data, datasets,
provenance

Statement of need
=================

*dtool* is a suite of software for managing scientific data and making it
accessible programmatically. It consists of a command line interface
[dtool](https://github.com/jic-dtool/dtool) and a Python API,
[dtoolcore](https://github.com/jic-dtool/dtoolcore).
*dtool* bundles data and metadata into a unified whole, the dataset,
without the need for a central database.

In the wide spectrum of disciplines in academia, many niche communities are far
removed from the ideal of FAIR data [@wilkinson2016fair].
Even in this context, individual researchers may benefit from
a little technical support in terms of research data management that just goes
a small step beyond custom file naming and folder hierarchy conventions
towards documentation with metadata, without scaring anyone away by enforcing
a corset of metadata schemas. Here, *dtool* has proven a helpful, lean utility
[@olsson2019lightweight; @hormann2022lightweight].

Making *dtool* datasets findable with *dserver* [@hormann2024dtool] helps to
bridge from entirely decentralized, individual data management towards
repositories on the small scale, e.g. on arbitrary group- or institute-wide
storage infrastructure.

Such repositories, even if instantiated ad-hoc on arbitrary storage
infrastructure at hand, are curated by more than two eyes and may add a layer of
quality control between an individual's local hard drive and fully FAIR data
publication platforms, helping both researcher and supervisor to stay on top of
their data, while simultaneously increasing the likelihood of high-quality data
making the (peer-reviewed) way into the public.

Just like *dtool* and *dtoolcore*, the design of
[*dtool-lookup-server*](https://github.com/jic-dtool/dtool-lookup-server)
and the surrounding plugin ecosystem puts a focus on simplicity and modularity.
*dtool* at its core is defined by a set of atomic operations performed on
datasets [@olsson2019lightweight]. Analogously,
[*dtool-lookup-server*](https://github.com/jic-dtool/dtool-lookup-server) is
defined by atomic operations on an index of dataset metadata, cast into a
minimal REST API that adheres to the
[OpenAPI Specification v3.1.0](https://spec.openapis.org/oas/v3.1.0).
[*dtool-lookup-server*](https://github.com/jic-dtool/dtool-lookup-server) is realized with the Python frameworks [Flask](https://flask.palletsprojects.com/)
and [flask-smorest](https://flask-smorest.readthedocs.io/en/latest/).

*dtool* and *dserver* fill an unoccupied niche between other distributed data
management ecosystems such as *DataLad*
[@halchenko2021datalad] and *RO-Crate* [@soiland-reyes2022packaging], having
found applications from improving individual data hygiene
to an important building block of complex computational workflows
in the fields of machine learning [@hartley2020dtoolai], solid mechanics
[@sanner2024why; @sanner2022crackfront], multiscale simulations
[@holey2022heightaveraged] and molecular dynamics simulations
[@hormann2023molecular].


Source code and documentation
=============================

Implementations of *dtool* and *dserver* are freely available under the
liberal MIT licence on GitHub. The codebases of *dtool* and *dserver*
are available at
[https://github.com/jic-dtool/](https://github.com/jic-dtool).
Importantly, *dtool-lookup-server*,
*dserver*'s core with extensive documentation, lives at
[https://github.com/jic-dtool/dtool-lookup-server](https://github.com/jic-dtool/dtool-lookup-server).
Several extension plugins are available at
<https://github.com/livMatS>. <https://demo.dtool.dev> exposes a
*dserver* demonstrator instance with a documentation of the REST API.

Competing interests
===================

The authors have no conflicts of interest to declare that are relevant
to the content of this article.

References
==========
