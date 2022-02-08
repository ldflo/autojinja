from flask import Flask
from flask import request

app = Flask(__name__)

parameters = {}

###############################
###        Server API       ###
###############################

### [[[ {{ handlers }} ]]]
@app.route('/helloworld', methods=['GET'])
def HelloWorld():
    # <<[ impl_HelloWorld ]>>
    return "Hello world !", 200
    # <<[ end ]>>

@app.route('/parameter', methods=['GET'])
def GetParameter():
    name = request.args['name']
    # <<[ impl_GetParameter ]>>
    if name not in parameters:
        return "Paramater doesn't exist", 500
    return str(parameters[name]), 200
    # <<[ end ]>>

@app.route('/parameter', methods=['POST'])
def SetParameters():
    # PAYLOAD EXAMPLE:
    # [
    #     {"name": "param1", "value": "abc"},
    #     {"name": "param2", "value": "45"},
    #     {"name": "param3", "value": "test"}
    # ]
    # <<[ impl_SetParameters ]>>
    for data in request.json:
        parameters[data['name']] = data['value']
    return "Ok", 200
    # <<[ end ]>>

@app.route('/parameter', methods=['PUT'])
def SetParameter():
    name = request.form['name']
    value = request.form['value']
    # <<[ impl_SetParameter ]>>
    parameters[name] = value
    return "", 200
    # <<[ end ]>>

@app.route('/clear/parameters', methods=['PUT'])
def ClearAllParameters():
    # <<[ impl_ClearAllParameters ]>>
    parameters.clear()
    return "", 200
    # <<[ end ]>>

@app.route('/notimplemented', methods=['GET'])
def NotImplemented():
    # <<[ impl_NotImplemented ]>>
    return "Not implemented", 501
    # <<[ end ]>>

### [[[ end ]]]

if __name__ == "__main__":
    app.run(port=12345, debug=True, threaded=True)
