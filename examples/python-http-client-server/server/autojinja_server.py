from autojinja import *
from utility import *
import json

### Prepare a template for handlers
handler_template = RawTemplate.from_string("""
@app.route('/{{ path }}', methods=['{{ method }}'])
def {{ name }}():
    {% for def in defs %}
    {{ def }}
    {% endfor %}
    {% for body in bodies %}
    # {{ body }}
    {% endfor %}
    # <<[ impl_{{name}} ]>>
    #### TODO: implement me ####
    return "Not implemented", 501
    # <<[ end ]>>
""".strip())

# Prepare a function for generating above template
def generate_handlers(collection):
    for item in collection['item']:
        yield handler_template.context(path = '/'.join(item['request']['url']['path']),
                                       method = item['request']['method'],
                                       name = item['name'].replace(' ', '_'),
                                       defs = generator_defs(item),
                                       bodies = generator_bodies(item)).render()

# Prepare some context generator for above template
def generator_defs(item):
    with ignore(KeyError):
        for arg in [x for x in item['request']['url']['query']]:
            yield f"{arg['key']} = request.args['{arg['key']}']"
    with ignore(KeyError):
        for form in [x for x in item['request']['body']['formdata']]:
            yield f"{form['key']} = request.form['{form['key']}']"

def generator_bodies(item):
    with ignore(KeyError):
        body = item['request']['body']['raw']
        yield "PAYLOAD EXAMPLE:"
        yield from body.replace('\r', '').split('\n')

# Read the Postman collection
with open(os.environ["POSTMAN_COLLECTION"]) as f:
    collection = json.load(f)

# Load 'server.py' file as a template
file_template = CogTemplate.from_file("server.py")

### Generate 'server.py'
file_template.context(handlers = generate_handlers(collection)).render_file()
