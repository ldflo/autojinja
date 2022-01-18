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
    print("Executing HelloWorld")
    rr = HelloWorld()
    print(f"Status code: {rr.status_code}")
    print(f"Content: {rr.text}")
    print()
    
    # GetParameter
    print("Executing GetParameter")
    rr = GetParameter("param1")
    print(f"Status code: {rr.status_code}")
    print(f"Content: {rr.text}")
    print()
    
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
    
    # SetParameter
    print("Executing SetParameter")
    rr = SetParameter("param1", "abc")
    print(f"Status code: {rr.status_code}")
    print(f"Content: {rr.text}")
    print()
    
    # ClearAllParameters
    print("Executing ClearAllParameters")
    rr = ClearAllParameters()
    print(f"Status code: {rr.status_code}")
    print(f"Content: {rr.text}")
    print()
    
    # NotImplemented
    print("Executing NotImplemented")
    rr = NotImplemented()
    print(f"Status code: {rr.status_code}")
    print(f"Content: {rr.text}")
    print()
    ### [[[ end ]]]
