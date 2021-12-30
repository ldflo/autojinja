from autojinja import *
from utility import *
import json

### Prepare a template for functions
function_template = RawTemplate.from_string("""
def {{ name }}({{ ', '.join(args) }}):
    {% for def in defs %}
    {{ def }}
    {% endfor %}
    {% for body in bodies %}
    # {{ body }}
    {% endfor %}
    return requests.{{ method.lower() }}(TARGET + '/{{ path }}'{{ ', '.join(binds) }})
""".strip())

# Prepare a function for generating above template
def generate_functions(collection):
    for item in collection['item']:
        yield function_template.context(name = item['name'].replace(' ', '_'),
                                        args = generator_function_args(item),
                                        defs = generator_function_defs(item),
                                        bodies = generator_function_bodies(item),
                                        method = item['request']['method'],
                                        path = '/'.join(item['request']['url']['path']),
                                        binds = generator_function_binds(item)).render()

# Prepare some context generator for above template
def generator_function_args(item):
    with ignore(KeyError):
        yield from [x['key'] for x in item['request']['url']['query']]
    with ignore(KeyError):
        yield from [x['key'] for x in item['request']['body']['formdata']]
    with ignore(KeyError):
        item['request']['body']['raw']
        yield "payload"

def generator_function_defs(item):
    with ignore(KeyError):
        params = [x for x in item['request']['url']['query']]
        yield "params = {}".format(bound_json(params))
    with ignore(KeyError):
        forms = [x for x in item['request']['body']['formdata']]
        yield "forms = {}".format(bound_json(forms))

def generator_function_bodies(item):
    with ignore(KeyError):
        body = item['request']['body']['raw']
        yield "PAYLOAD EXAMPLE:"
        yield from body.replace('\r', '').split('\n')

def generator_function_binds(item):
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
    object = {arg['key']: "@@{}@@".format(arg['key']) for arg in args} # Usage of @@ marker
    return json.dumps(object).replace('"@@', '').replace('@@"', '') # Remove quotes and @@ markers

### Prepare a template for examples
example_template = RawTemplate.from_string("""
# {{ name }}
print("Executing {}".format({{ name }}))
rr = {{ name }}({{ ', '.join(args) }})
print("Status code: {}".format(rr.status_code))
print("Content: {}".format(rr.text))
print()
""".strip())

# Prepare a function for generating above template
def generate_examples(item):
    for item in collection['item']:
        yield example_template.context(name = item['name'].replace(' ', '_'),
                                       args = generator_example_args(item)).render()

# Prepare a context generator for above template
def generator_example_args(item):
    with ignore(KeyError):
        yield from ['"{}"'.format(x['value']) for x in item['request']['url']['query']]
    with ignore(KeyError):
        yield from ['"{}"'.format(x['value']) for x in item['request']['body']['formdata']]
    with ignore(KeyError):
        yield item['request']['body']['raw'].replace('\r', '')

# Read Postman collection
with open(os.environ["POSTMAN_COLLECTION"]) as f:
    collection = json.load(f)

# Load 'client.py' file as a template
file_template = CogTemplate.from_file("client.py")

### Generate 'client.py'
file_template.context(functions = generate_functions(collection),
                      examples = generate_examples(collection)).render_file()

