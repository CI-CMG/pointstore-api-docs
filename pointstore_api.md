# Crowdsourced Bathymetry Pointstore API

### Warning
*This application in active development and is being offered as a technology preview. No expectations should be made as to it's availability and the API may change prior to public release.*

## Introduction

This API exposes one resource, *order*, which represents a request to extract a subset of soundings from the pointstore and optionally grid them. The soundings are delivered as points in a comma separated value (CSV) format file. The generated grid is provided in a user specified format and resolution.

The process is asynchronous with the flow being:

1. submit order via HTTP POST request. The response to the POST request will contain an acknowlegement if order is accepted and an URL that can be used to check processing status.
2. Once the order is complete, an email will be received with pickup instructions. Processing time is generally less than 30 minutes.

## Limitations and known issues

* if a grid is requested there is a limit on the number of points and grid cells which can be processed.
* the area of interest (i.e. bounding box) cannot cross the antimeridian
* base URL is temporarily hosted at https://q81rej0j12.execute-api.us-east-1.amazonaws.com/

## API

**POST** /order

must include JSON payload described in the schema below. The *url* in the response can be used to check the status.

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

must include the order id in the request path

responses:

* 200 - success
* 400 - no order id provided
* 404 - invalid order id provided

## JSON schema for Order payload

```json
{
"$schema": "https://json-schema.org/draft/2020-12/schema",
"title": "Pointstore order payload",
"description": "payload to create a new pointstore request",
"type": "object",
  "properties": {
    "bbox": {
      "type": "string",
      "description": "comma-separated list of geographic coordinates in units of decimal degrees. format: minx, miny, maxx, maxy"
    },
    "email": {
      "description": "email address which will receive order notifications",
    "type": "string"
    },
    "grid": {
      "type": "object",
      "description": "properties for (optional) generated grid. If this element is not provided, only soundings will be produced",
      "properties": {
        "resolution": {
        "description": "generated grid cell size in meters",
        "type": "number"
            },
            "format": {
              "description": "format code for generated grid",
              "type": "number"
            }
          },
          "required": [ "resolution", "format"]
        },
        "datasets": {
         	"type": "array",
            "items": { "$ref": "#/$defs/dataset" },
            "minItems": 1
        }
          
    },
    "additionalProperties": false,
    "required": [ "email", "bbox"],
      
    "$defs": {
      "dataset": {
        "type": "object",
        "required": [ "type" ],
        "properties": {
          "type": {
            "type": "string",
            "description": "dataset type",
            "enum": ["csb", "multibeam" ]
          },
          "provider": {
            "type": "string",
            "description": "trusted node name. only used for csb"
          },
          "platform" : {
            "type": "string",
            "description": "platform, aka ship or vessel name"
          },
          "unique_id" : {
            "type": "string",
            "description": "identifier assigned by the provider which should uniquely identify the combination of provider and platform name"
          },
          "collection_date": {
            "type": "string",
            "description": "date on which the data were collected. Format: YYYY-MM-DD"
          },
          "archive_date": {
            "type": "string",
            "description": "date on which the data were received at the DCDB. Format: YYYY-MM-DD"
          },
          "cruise": {
            "type": "string",
            "description": "cruise on which the data were collected. Only used for multibeam"
          },
        },
        "additionalProperties": false,      
      },
      "required": [ "type" ]
    
  }
}
```

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
      "type": "csb",
      "platform": "Ramform Vanguard"
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
