from autojinja import *
from utility import *
import json

### Read the Postman collection
with open(os.environ["POSTMAN_COLLECTION"]) as f:
    collection = json.load(f)

# Prepare a template
handler_template = RawTemplate.from_string("""
{% for item in collection['item'] %}
@app.route('/{{ jsonitem.path(item) }}', methods=['{{ jsonitem.method(item) }}'])
def {{ jsonitem.name(item) }}():
    {% for def in jsonitem.defs(item) %}
    {{ def }}
    {% endfor %}
    {% for body in jsonitem.bodies(item) %}
    # {{ body }}
    {% endfor %}
    # <<[ impl_{{ jsonitem.name(item) }} ]>>
    #### TODO: implement me ####
    return "Not implemented", 501
    # <<[ end ]>>

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
    def defs(item):
        with ignore(KeyError):
            for arg in [x for x in item['request']['url']['query']]:
                yield f"{arg['key']} = request.args['{arg['key']}']"
        with ignore(KeyError):
            for form in [x for x in item['request']['body']['formdata']]:
                yield f"{form['key']} = request.form['{form['key']}']"
    def bodies(item):
        with ignore(KeyError):
            body = item['request']['body']['raw']
            yield "PAYLOAD EXAMPLE:"
            yield from body.replace('\r', '').split('\n')

# Generate the above template with the Postman collection.
# The template has direct access to the current Python scope
handlers = handler_template.context(**locals()).render()

### Insert result inside 'server.py'
file_template = CogTemplate.from_file("server.py")
file_template.context(handlers = handlers).render_file()
