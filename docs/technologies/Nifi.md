# Nifi Documentation

***

## Table of Contents

- [Nifi Documentation](#nifi-documentation)
  - [Table of Contents](#table-of-contents)
  - [Contributors](#contributors)
      - [Owner](#owner)
  - [About](#about)
  - [Processors](#processors)
      - [FetchAPI\_USGS (InvokeHTTP)](#fetchapi_usgs-invokehttp)
        - [About](#about-1)
        - [Scheduling](#scheduling)
        - [Properties](#properties)
      - [LogAttributeOnFailure (LogAttribute)](#logattributeonfailure-logattribute)
        - [About](#about-2)
        - [Settings](#settings)
        - [Properties](#properties-1)
      - [HashKeyAttribute (HashContent)](#hashkeyattribute-hashcontent)
        - [About](#about-3)
        - [Scheduling](#scheduling-1)
        - [Properties](#properties-2)
      - [CheckAttributes (RouteOnAttribute)](#checkattributes-routeonattribute)
        - [About](#about-4)
        - [Scheduling](#scheduling-2)
        - [Properties](#properties-3)
      - [AttributesToContent (UpdateRecord)](#attributestocontent-updaterecord)
        - [About](#about-5)
        - [Properties](#properties-4)
  - [Log Message Guide](#log-message-guide)
      - [Errors](#errors)
        - [WrongFormat](#wrongformat)
        - [HashFailure](#hashfailure)
        - [KafkaNotReachable](#kafkanotreachable)
        - [APIFailure](#apifailure)

***

## Contributors
#### Owner
- Silas Jung
- evoila GmbH
  
***

## About

Nifi is used in this project to extract data from an API which provides data about earthquake locations. Currently, the API of the  [USGS](https://earthquake.usgs.gov/fdsnws/event/1/) is in use. When adding new APIs, be sure to adjust the output to flat JSON accordingly. New processors can be connected analogously to the existing ones.

This document serves to explain and list the use and settings of the Nifi application and flows.

***

## Processors

#### FetchAPI_USGS (InvokeHTTP)

##### About
This processor is responsible for pulling data from an API via a corresponding HTTP method. The URL of the API is equipped with querys to limit the amount of data. Care must be taken to send requests at a reasonable rate.

##### Scheduling
- Scheduling strategy
  `CRON driven`
- Run Schedule
  `30 * * * * ?`
- Execution
  `Primary node`

##### Properties
- HTTP Method
  `GET`
- Remote URL
    ````
    https://earthquake.usgs.gov/fdsnws/event/1/query?
    format=geojson&
    starttime=
    ${now():toNumber():plus(3600000):format("yyyy-MM-dd", "UTC")}T${now():toNumber():plus(3600000):format("HH:00", "UTC")}%2B02:00&
    endtime=
    ${now():toNumber():plus(3600000):format("yyyy-MM-dd", "UTC")}T${now():toNumber():plus(3600000):format("HH:59", "UTC")}%2B02:00
    ````

---

#### LogAttributeOnFailure (LogAttribute)

##### About
This processor logs every failure to the nifi log, found in the container under logs.

##### Settings
- Automatically terminate relationships
  `success`

##### Properties
- Log Level
  `warn`

---

#### HashKeyAttribute (HashContent)

##### About
This processor is used to generate a unique key from the content of a request and add it as an attribute. This prevents the saving of duplicates and simplifies the handling of the data sets.

##### Scheduling
- Scheduling strategy
  `Event driver (experimental)`
- Execution
  `All nodes`

##### Properties
- Hash Attribute Name
  `eq_hash_key`
- Hash Algorithm
  `MD5`


---

#### CheckAttributes (RouteOnAttribute)

##### About
This processor is used to check that all required Attributes are available. Flow-files not containing these cannot be processed further.

##### Scheduling
- Scheduling strategy
  `Event driver (experimental)`

##### Properties
- Routing Strategy
  `Routed to "matched" if all match`
- all previously created and required attributes, e.g. api_name
  `${api_name}`


---

#### AttributesToContent (UpdateRecord)

##### About
This processor is used add all costum attributes to the content to be published to kafka. These attributes are attached to the root of the json content structure.

##### Properties
- Record Reader
  `JsonTreeReader`
- Record Writer
  `JsonRecordSetWriter`
- all previously created and required attributes, e.g. /api_name
  `${api_name}`


---

## Log Message Guide

#### Errors

##### WrongFormat
This error message indicates that one or more attributes or the content does not meet expectations. Please refer to the TODO: [Adding APIs](TODO) Guide.

##### HashFailure
This error message indicates that the HashContent processor is not able to create a hashed attribute out of the content. Please refer to the official documentation.

##### KafkaNotReachable
This error message indicates that the kafka broker to send the eq-data to is not reachable. Please check that the network and broker are working properly.

##### APIFailure
This error message indicates that the request send to an API failed. Please check that the APIs available in the flow are configured properply and the API destinations are available.