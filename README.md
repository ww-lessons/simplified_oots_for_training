# Implication of this example

The example being proposed in this repository should help students to understand some considerations about registry and repository based distributed
systems like for example the OOTS being proposed by European Union to be the foundation for sharing official documents between different
units of public administration without technical barriers.

Therefore the example is being simplified and modified in different areas. One core simplification is, that it does not have encryption, authentication and authorization at all. Anotherone is that there is no mechanism for users, to securely authorize the usage of documents by other units of public administration. 

That means it is no exact implementation of OOTS. Instead it does things different to help students to understand the design implications of OOTS in several upcoming lessons.

Also the mixture of different languages being used in the system is intended to show the problem of internationalization.

# General information about OOTS

To learn about how the real OOTS is specified by European Union, there are some links to the official documenation.

*Article 14 of the Single Digital Gateway Regulation [REF30] states that the Commission, in cooperation with the Member States, shall establish a technical system for the cross-border automated exchange of evidences between competent authorities in different Member States. The draft "once-only" Implementing Act [REF38] further sets out the technical and operational specifications of the technical system necessary for the implementation of this Article. (References to this draft will be replaced by the references to the IR once it is adopted by the Commission and published in the Official Journal).*

*This document complements the Implementing Act by providing a high-level architecture. This high level architecture is complemented by, and serves as an introduction to, further technical and operational design documents. References to current versions of this documentation are provided in this document. Together, these documents and the interface documentation they provide deliver the interoperability necessary to support the implementation and interconnection of the distributed components that constitute the Once-Only Technical System (OOTS).*

(Source: https://ec.europa.eu/digital-building-blocks/sites/display/TDD/1.+Once-Only+Technical+System+High+Level+Architecture+-+Snapshot+Q3#id-1.OnceOnlyTechnicalSystemHighLevelArchitectureSnapshotQ3-1.Introduction, Zugegriffen 20.12.2023)

# Architectural overview of OOTS

In this section, there are some of the proposed links to the official documentation of OOTS.

* https://ec.europa.eu/digital-building-blocks/sites/display/OOTS/Technical+Design+Documents
* https://ec.europa.eu/digital-building-blocks/sites/pages/viewpage.action?pageId=706382128

# Technical specification of the core parts of OOTS

In this section, there are some of the proposed links to the official documentation of OOTS.

## Evidence Broker:

* https://oots.pages.code.europa.eu/tdd/apidoc/evidence-broker/get-requirements
* https://oots.pages.code.europa.eu/tdd/apidoc/evidence-broker/get-evidence-types

## Data Services Directory:

* https://oots.pages.code.europa.eu/tdd/apidoc/data-services-directory/find-data-services

## Semantic Repository:

* https://oots.pages.code.europa.eu/tdd/apidoc/semantic-repository/get-asset-metadata
* https://oots.pages.code.europa.eu/tdd/apidoc/semantic-repository/redirect-to-asset-accessURL


# Handling the example

## Make the example run on your system

First of all make sure that there is a current installation of git, docker and docker compose 
at your system.

If that is done, proceed like the following listing shows:

```shell
mkdir demo
cd demo
git clone https://github.com/ww-lessons/simplified_oots_for_training.git
docker compose up
# then wait until the app is up
# then you can go to http://localhost:8080 with your favourite browser
```

If you want to have some example data in your system feel free to run one of

* test.py
* generate_demodata.py
* generate_massdata.py

directly from your shell on your local system. The scripts will connect to the
backends using localhost:8081 and localhost:8082.

## How to find eIDs with more than one deregistrations

Connect a shell to the mongodb database for the backends, login and select the right database:

```
university_de> db.deregistration_store.aggregate([{"$group": { _id: "$eid", count:{$sum:1}}}, {$sort: {"count":-1}}])
[
  { _id: '12345582102@id.bund.de', count: 3 },
  { _id: '12345978046@id.bund.de', count: 2 },
  { _id: '12345980794@id.bund.de', count: 2 },
  { _id: '12345993501@id.bund.de', count: 2 },
  { _id: '12345628114@id.bund.de', count: 2 },
  { _id: '12345788414@id.bund.de', count: 2 },
  { _id: '12345922705@id.bund.de', count: 2 },
  { _id: '12345778902@id.bund.de', count: 2 },
  { _id: '12345474923@id.bund.de', count: 2 },
  { _id: '12345524100@id.bund.de', count: 2 },
  { _id: '12345236965@id.bund.de', count: 2 },
  { _id: '12345379572@id.bund.de', count: 2 },
  { _id: '12345820327@id.bund.de', count: 2 },
  { _id: '12345910183@id.bund.de', count: 2 },
  { _id: '12345955958@id.bund.de', count: 2 },
  { _id: '12345677597@id.bund.de', count: 2 },
  { _id: '12345297670@id.bund.de', count: 2 },
  { _id: '12345612559@id.bund.de', count: 2 },
  { _id: '12345200558@id.bund.de', count: 2 },
  { _id: '12345597118@id.bund.de', count: 2 }
```