# Crowdsourced Bathymetry Pointstore API

### Warning
*This application is in active development and is being offered as a technology preview. No expectations should be made as to it's availability and the API may change prior to public release.*

## Introduction

This API exposes three resources, the primary being **order** which represents a request to extract a subset of soundings from the pointstore and optionally grid them. The soundings are delivered as points in a comma separated value (CSV) format file which is described below. The generated grid is provided in a user specified format and resolution. The two additional resources, **count** and **platforms**, return the number of soundings and a list of platforms respectively.

The order process is asynchronous with the flow being:

1. submit order via HTTP POST request. The response to the POST request will contain an acknowlegement if order is accepted and an URL that can be used to check processing status.
2. Once the order is complete, an email will be received with pickup instructions. If no email is provided, no notification is provided and the user is responsible for checking the order status to get the download URL. Processing time is generally less than 30 minutes.

## Limitations and known issues

* if a grid is requested there is a limit on the number of points and grid cells which can be processed.
* the area of interest (i.e. bounding box) cannot cross the antimeridian
* base URL is temporarily hosted at https://q81rej0j12.execute-api.us-east-1.amazonaws.com/

## API

**POST** /order

Create a new **order**. Must include JSON payload described in the schema below. The *url* in the response can be used to check the status.

responses:

* 201 - order created
* 400 - invalid request

example response:

```json
{
    "message": "extract request 03917a0b-898c-4d26-8f88-f3305a29b878 created.",
    "url": "https://q81rej0j12.execute-api.us-east-1.amazonaws.com/order/03917a0b-898c-4d26-8f88-f3305a29b878"
}
```

**GET** /order/:id

Return the status of an existing **order** in JSON format. Must include the order id in the request path

responses:

* 200 - success
* 400 - no order id provided
* 404 - invalid order id provided

example response:

```json
{
    "output_location": "s3://order-pickup/1bbc5137-9459-440c-aee6-c28c73af3f60.csv",
    "last_update": "2024-09-19T23:34:01+00:00",
    "status": "complete"
}
```

**GET** /count

Return the number of points (soundings) matching the given search criteria. Search criteria are optional and provided as URL query parameters:
 
* bbox (minx,miny,maxx,maxy format)
* providers (comma-separated list of provider names)
* platforms  (comma-separated list of platform names)
* collection_date_start (YYYY-MM-DD format)
* collection_date_end (YYYY-MM-DD format)
* archive_date_start (YYYY-MM-DD format)
* archive_date_end (YYYY-MM-DD format)
* unique_id (single value to identify a specific provider's platform)

example response:

```json 
{"count": "275375042"}
```

**GET** /platforms

Return a list of platforms (grouped by provider) associated with soundings matching the given search criteria. Search criteria are optional and provided as URL query parameters:
 
* bbox (minx,miny,maxx,maxy format)
* providers (comma-separated list of provider names)
* platforms  (comma-separated list of platform names)
* collection_date_start (YYYY-MM-DD format)
* collection_date_end (YYYY-MM-DD format)
* archive_date_start (YYYY-MM-DD format)
* archive_date_end (YYYY-MM-DD format)
* unique_id (single value to identify a specific provider's platform)

sample response:
```json
{
  "count": 4,
  "data": [
    {
      "provider": "Rosepoint",
      "platform": "Dulce Vida"
    },
    {
      "provider": "Rosepoint",
      "platform": "Laperouse"
    },
    {
      "provider": "Rosepoint",
      "platform": "S/V Aphrodite"
    },
    {
      "provider": "AquaMap",
      "platform": "Astrid"
    }
  ]
}
```

## JSON schema for Order payload
[access](https://raw.githubusercontent.com/CI-CMG/pointstore-api-docs/refs/heads/main/pointstore_payload_schema.json) from GitHub repository

## Examples

### create a new order

create a new order to extract all soundings from the platform *Ramform Vanguard* within the bounding box with a southwest corner of 5.0 degrees longitude, 60.0 degrees latitude and a northeast corner of 6.0 degrees longitude, 61.0 degrees latitude.

**request**

```bash
curl -X POST https://q81rej0j12.execute-api.us-east-1.amazonaws.com/order \
   -H 'Content-Type: application/json' \
   -d '{
  "email": "your.email.address@example.com",
  "bbox": "5,60,6,61",
  "datasets": [
    {
      "label": "csb",
      "platforms": ["Ramform Vanguard"]
    }
  ]
}'
```

**response**

```json
{
  "message": "extract request 408429b1-8cb0-41c5-93ee-2f15d51e1594 created.",
  "url": "https://q81rej0j12.execute-api.us-east-1.amazonaws.com/order/408429b1-8cb0-41c5-93ee-2f15d51e1594"
}
```

### check the status of a previously submitted order

**request**

```bash
curl -X GET https://q81rej0j12.execute-api.us-east-1.amazonaws.com/order/408429b1-8cb0-41c5-93ee-2f15d51e1594
```

**response**

```json
{
  "output_location": "s3://order-pickup/703b8ecd-7012-4ee3-83ba-6d50501ba4a4.csv",
  "last_update": "2023-05-31T22:57:04+00:00",
  "status": "complete"
}
```

## Output data format

the points are delivered in a CSV-format file with the following attributes:

* LON - longitude of the sounding in decimal degrees. Coordinate precision varies based on instrument and trusted node and does not necessarily reflect positional accuracy	
* LAT - latitude of the sounding in decimal degrees. Coordinate precision varies based on instrument and trusted node and does not necessarily reflect positional accuracy
* DEPTH - depth in meters
* TIME - datetime of the sounding in ISO-8601 format
* PLATFORM_NAME - name of the platform. Not necessarily unique.
* PROVIDER - trusted node which supplied the data
* UNIQUE_ID - identifier intended to uniquely identify a given provider's platform
* FILE_UUID - unique identifier for file from which the given sounding originated
  
## Grid formats

if an output grid is requested, the output format can be any of those supported by the *-G* parameter in the [MB-System](https://www.mbari.org/technology/mb-system/) *mbgrid* command. See the [man page](https://www3.mbari.org/data/mbsystem/html/mbgrid.html) for more information.

* 1:   ASCII table
* 2:   binary file (GMT version 1 GRD file)
* 3:   netCDF file (GMT version 2 GRD file)
* 4:   Arc/Info and ArcView ASCII grid
* 100: GMT netCDF 4-byte float format [Default]
* 101: Native binary single precision floats in scanlines with leading grd header
* 102: Native binary short integers in scanlines with leading grd header
* 103: 8-bit standard Sun rasterfile (colormap ignored)
* 104: Native binary unsigned char in scanlines with leading grd header
* 105: Native binary bits in scanlines with leading grd header
* 106: Native binary ``surfer'' grid files
* 107: netCDF 1-byte byte format
* 108: netCDF 1-byte char format
* 109: netCDF 2-byte int format
* 110: netCDF 4-byte int format
* 111: netCDF 8-byte double format
