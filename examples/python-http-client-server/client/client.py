import requests

TARGET = "http://127.0.0.1:12345"

################################
###        Client API        ###
################################

### [[[ {{ '\n'.join(functions) }} ]]]
def HelloWorld():
    return requests.get(TARGET + '/helloworld')
def GetParameter(name):
    params = {"name": name}
    return requests.get(TARGET + '/parameter', params = params)
def SetParameters(payload):
    # PAYLOAD EXAMPLE:
    # [
    #     {"name": "param1", "value": "abc"},
    #     {"name": "param2", "value": "45"},
    #     {"name": "param3", "value": "test"}
    # ]
    return requests.post(TARGET + '/parameter', json = payload)
def SetParameter(name, value):
    forms = {"name": name, "value": value}
    return requests.put(TARGET + '/parameter', data = forms)
def ClearAllParameters():
    return requests.put(TARGET + '/clear/parameters')
def NotImplemented():
    return requests.get(TARGET + '/notimplemented')
### [[[ end ]]]

################################
###         Examples         ###
################################

if __name__ == "__main__":
    ### [[[ {{ '\n\n'.join(examples) }} ]]]
    # HelloWorld
    print("Executing {}".format(HelloWorld))
    rr = HelloWorld()
    print("Status code: {}".format(rr.status_code))
    print("Content: {}".format(rr.text))
    print()
    
    # GetParameter
    print("Executing {}".format(GetParameter))
    rr = GetParameter("param1")
    print("Status code: {}".format(rr.status_code))
    print("Content: {}".format(rr.text))
    print()
    
    # SetParameters
    print("Executing {}".format(SetParameters))
    rr = SetParameters([
        {"name": "param1", "value": "abc"},
        {"name": "param2", "value": "45"},
        {"name": "param3", "value": "test"}
    ])
    print("Status code: {}".format(rr.status_code))
    print("Content: {}".format(rr.text))
    print()
    
    # SetParameter
    print("Executing {}".format(SetParameter))
    rr = SetParameter("param1", "abc")
    print("Status code: {}".format(rr.status_code))
    print("Content: {}".format(rr.text))
    print()
    
    # ClearAllParameters
    print("Executing {}".format(ClearAllParameters))
    rr = ClearAllParameters()
    print("Status code: {}".format(rr.status_code))
    print("Content: {}".format(rr.text))
    print()
    
    # NotImplemented
    print("Executing {}".format(NotImplemented))
    rr = NotImplemented()
    print("Status code: {}".format(rr.status_code))
    print("Content: {}".format(rr.text))
    print()
    ### [[[ end ]]]
