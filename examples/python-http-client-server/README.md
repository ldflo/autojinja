# Python HTTP client / server example

This example generates an HTTP server and its corresponding HTTP client, starting from the REST API described in the `example.postman_collection.json` [Postman](https://www.postman.com/collection) collection.

## Server

The HTTP server is made possible thanks to the [Flask](https://github.com/pallets/flask) module, which enables to easily define a REST API using simple Python functions.

Each item in the Postman collection...

```json5
"name": "HelloWorld",
"request": {
    "method": "GET",
    "url": {
        "path": [
            "helloworld"
        ],
        ...
    }
}
```

...will be generated in `server/server.py` as such :

```python
@app.route('/helloworld', methods=['GET'])
def HelloWorld():
    # <<[ impl_HelloWorld ]>>
    #### TODO: implement me ####
    return "Not implemented", 501
    # <<[ end ]>>
```

The implementation of the server API can then be manually provided within the dedicated sections.

## Client

The HTTP client uses the [Requests](https://github.com/psf/requests) module to make calls to the REST API.

Each item in the Postman collection...

```json5
"name": "SetParameters",
"request": {
    "method": "POST",
    "url": {
        "path": [
            "parameter"
        ],
        ...
    },
    "body": {
        "raw": "{ { \"name\": \"param1\", \"value\": \"abc\" }, ... }"
        ...
    },
}
```

...will be generated in `client/client.py` as a ready-to-use function :

```python
def SetParameters(payload):
    # PAYLOAD EXAMPLE:
    # [
    #     {"name": "param1", "value": "abc"},
    #     {"name": "param2", "value": "45"},
    #     {"name": "param3", "value": "test"}
    # ]
    return requests.post(TARGET + '/parameter', json = payload)
```

In the _main_ section of `client/client.py`, a call to each function is generated as such :

```python
if __name__ == "__main__":
    ### [[[ {{ examples }} ]]]
    # SetParameters
    print("Executing SetParameters")
    rr = SetParameters([
        {"name": "param1", "value": "abc"},
        {"name": "param2", "value": "45"},
        {"name": "param3", "value": "test"}
    ])
    print(f"Status code: {rr.status_code}")
    print(f"Content: {rr.text}")
    print()
    ...
    ### [[[ end ]]]
```

## Environment variables

Both the client and the server use environment variables defined inside the `autojinja.env` file :

- `POSTMAN_COLLECTION` environment variable : indicates where to find the Postman collection
- `PYTHONPATH` environment variable : allows to directly import all Python scripts located in the `utility/` directory

# Dependencies

All dependencies required for this example can be installed with the command :

```shell
$ pip install requirements.txt
```

# How to execute

The whole generation process takes place in `server/autojinja_server.py` and `client/autojinja_client.py` scripts, which can be manually executed or automatically discovered with the commands :

```shell
$ autojinja -e autojinja.env server/autojinja_server.py client/autojinja_client.py
```
```shell
$ autojinja -e autojinja.env -a .
```

The server and the client can then be launched with the commands :

```shell
$ python server/server.py
```
```shell
$ python client/client.py
```
