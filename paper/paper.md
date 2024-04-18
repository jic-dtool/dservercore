---
title: 'dserver: a REST API-centered Flask app for finding dtool datasets'
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

*dtool* is a suite of software for managing scientific data and making it 
accessible programatically. It consists of a command line interface
[dtool](https://github.com/jic-dtool/dtool) and a Python API,
[dtoolcore](https://github.com/jic-dtool/dtoolcore).
*dtool* bundles data and metadata into a unified whole, the dataset,
without the need for a central database. However, if one has to manage more than 
a hundred datasets it can be helpful to have the datasets’ metadata stored in a
central server to enable one to quickly find datasets of interest.
*dserver*, shorthand for the *dtool lookup server*, provides a web API for
registering datasets’ metadata and provides functionality to look up, list and
search for datasets. Here, we introduce *dserver*'s core, the
[Flask](https://flask.palletsprojects.com/) app *dtool-lookup-server*. 
Just like *dtool* and *dtoolcore*, the design of *dtool-lookup-server* and the
surrounding plugin ecosystem puts a focus on simplicity and modularity.

Keywords: Research data management, Findability, FAIR data, datasets,
provenance

Statement of need
=================

In the wide spectrum of disciplines in academia, many niche communities are far
removed from the ideal of FAIR data. 

Even in this context, individual researchers may benefit from  
a little technical support in terms of research data management that just goes 
a single step beyond custom file naming and folder hierarchy conventions
towards documentation with metadata, without scaring anyone away by enforcing
a corset of metadata schemas and adherence to ontologies.

Here, *dtool* has proven a helpful, lean utility filling in a niche [cite].

Making *dtool* datasets findable with *dserver* helps to bridge from entirely 
decentralized, individual RDM towards repositories on the small scale, 
e.g. on arbitrary group- or institute-wide storage infrastructure.

Such repositories curated by more than two eyes add a layer of quality assurance
between an individual's local hard drive and fully FAIR data publication 
platforms, helping both researcher and supervisor to stay on top of their data,
while simultaneously increasing the likelihood of high-quality data actually
making the (peer-reviewed) way into the public.

Design
======

*dserver* is consumed by the *dtool-lookup-webapp*, *dtool-lookup-api*,
the *dtool-lookup-client*, and the *dtool-lookup-gui*.


Source code and documentation
=============================

Implementations of *dtool* and *dserver* are freely available under the
liberal MIT licence on GitHub. The codebases of *dtool* and *dserver*
are available at
[https://github.com/jic-dtool/](https://github.com/jic-dtool). Several
optional extension plugins and a standalone GUI are available at
<https://github.com/livMatS>. <https://demo.dtool.dev> exposes a
*dserver* demonstrator instance with a documentation of the REST API.

Competing interests
===================

The authors have no conflicts of interest to declare that are relevant
to the content of this article.

References
==========
