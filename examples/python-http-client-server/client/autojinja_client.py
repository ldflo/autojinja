from autojinja import *
from utility import *
import json

### Read the Postman collection
with open(os.environ["POSTMAN_COLLECTION"]) as f:
    collection = json.load(f)

#####################################
###           functions           ###
#####################################

# Prepare a template
function_template = RawTemplate.from_string("""
{% for item in collection['item'] %}
def {{ jsonitem.name(item) }}({{ ', '.join(jsonitem.args(item)) }}):
    {% for def in jsonitem.defs(item) %}
    {{ def }}
    {% endfor %}
    {% for body in jsonitem.bodies(item) %}
    # {{ body }}
    {% endfor %}
    return requests.{{ jsonitem.method(item).lower() }}(TARGET + '/{{ jsonitem.path(item) }}'{{ ', '.join(jsonitem.binds(item)) }})
{% endfor %}
""".strip())

# Prepare some helpers for above template
class jsonitem:
    def path(item):
        return '/'.join(item['request']['url']['path'])
    def method(item):
        return item['request']['method']
    def name(item):
        return item['name'].replace(' ', '_')
    def args(item):
        with ignore(KeyError):
            yield from [x['key'] for x in item['request']['url']['query']]
        with ignore(KeyError):
            yield from [x['key'] for x in item['request']['body']['formdata']]
        with ignore(KeyError):
            item['request']['body']['raw']
            yield "payload"
    def defs(item):
        with ignore(KeyError):
            params = [x for x in item['request']['url']['query']]
            yield f"params = {jsonitem.bound_json(params)}"
        with ignore(KeyError):
            forms = [x for x in item['request']['body']['formdata']]
            yield f"forms = {jsonitem.bound_json(forms)}"
    def bodies(item):
        with ignore(KeyError):
            body = item['request']['body']['raw']
            yield "PAYLOAD EXAMPLE:"
            yield from body.replace('\r', '').split('\n')
    def binds(item):
        nobinds = True
        with ignore(KeyError):
            item['request']['url']['query']
            if nobinds: nobinds = False; yield '' # First comma
            yield "params = params"
        with ignore(KeyError):
            item['request']['body']['formdata']
            if nobinds: nobinds = False; yield '' # First comma
            yield "data = forms"
        with ignore(KeyError):
            item['request']['body']['raw']
            if nobinds: nobinds = False; yield '' # First comma
            yield "json = payload"
            
    def bound_json(args):
        """ Allows to create a Json binding to the given arguments, without quotes
        """
        object = {arg['key']: f"@@{arg['key']}@@" for arg in args} # Usage of @@ marker
        return json.dumps(object).replace('"@@', '').replace('@@"', '') # Remove quotes and @@ markers

# Generate the above template with the Postman collection.
# The template has direct access to the current Python scope
functions = function_template.context(**locals()).render()

####################################
###           examples           ###
####################################

# Prepare a template
example_template = RawTemplate.from_string("""
{% for item in collection['item'] %}
# {{ jsonitem.name(item) }}
print("Executing {{ jsonitem.name(item) }}")
rr = {{ jsonitem.name(item) }}({{ ', '.join(jsonitem.args(item)) }})
print(f"Status code: {rr.status_code}")
print(f"Content: {rr.text}")
print()

{% endfor %}
""".strip())

# Prepare some helpers for above template
class jsonitem:
    def name(item):
        return item['name'].replace(' ', '_')
    def args(item):
        with ignore(KeyError):
            yield from [f"\"{x['value']}\"" for x in item['request']['url']['query']]
        with ignore(KeyError):
            yield from [f"\"{x['value']}\"" for x in item['request']['body']['formdata']]
        with ignore(KeyError):
            yield item['request']['body']['raw'].replace('\r', '')

# Generate the above template with the Postman collection.
# The template has direct access to the current Python scope
examples = example_template.context(**locals()).render()

### Insert results inside 'client.py'
file_template = CogTemplate.from_file("client.py")
file_template.context(functions = functions, examples = examples).render_file()
