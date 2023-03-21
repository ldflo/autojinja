import autojinja
from lxml import etree
import os
import utility

### Read XML
xroot: etree._Element = etree.parse(os.environ["SERVER_XML"])
xfunctions = xroot.xpath("Function")

#######################################
###           ServerApi.h           ###
#######################################

### Insert inside 'ServerApi.h'
file_template = autojinja.CogTemplate.from_file("ServerApi.h")
file_template.context(api_defs = utility.function_defs(xfunctions)).render_file()

#######################################
###          ServerApi.cpp          ###
#######################################

# Prepare a template for server API implementations
implementation = autojinja.RawTemplate.from_string("""
// <<[ impl_{{ Name }} ]>>
static_assert(false, "ServerApi::{{ Name }} is not implemented...");
// <<[ end ]>>
""".strip())

# Prepare a function for generating above template
def implementation_func(xfunction: etree._Element) -> str:
    return implementation.context(Name = xfunction.attrib['name']).render()

### Insert inside 'ServerApi.cpp'
file_template = autojinja.CogTemplate.from_file("ServerApi.cpp")
file_template.context(api_impls = utility.function_impls(xfunctions, implementation_func)).render_file()

#######################################
###            Server.cpp           ###
#######################################

# Prepare a template for server API forwardings
implementation = autojinja.RawTemplate.from_string("""
{% for xfunction in xfunctions %}
case {{ loop.index }}u: { /* {{ Name(xfunction) }} */
    {% for Arg in Args(xfunction) %}
    {{ Arg.type }} {{ Arg.name }} = deserialize<{{ Arg.type }}>(ptr);
    {% endfor %}
    {{ ReturnType(xfunction) }} result = ServerApi::{{ Call(xfunction) }};
    shared_memory::clear();
    serialize(result, shared_memory::ptr);
} break;
{% endfor %}
""".strip())

# Prepare some helpers for above template
def Name(xfunction: etree._Element) -> str:
    return xfunction.attrib['name']
def Args(xfunction: etree._Element) -> str:
    for xarg in xfunction.xpath("Arg"):
        class Arg:
            name = xarg.attrib['name']
            type = xarg.attrib['type'].replace("const", "").replace("&", "").replace("*", "").strip()
        yield Arg
def ReturnType(xfunction: etree._Element) -> str:
    return xfunction.xpath("ReturnType/@type")[0]
def Call(xfunction: etree._Element) -> str:
    return utility.function_call(xfunction)

# Generate the above template.
# The template has direct access to the current Python scope
server_impls = implementation.context(**locals()).render()

### Insert result inside 'Server.cpp'
file_template = autojinja.CogTemplate.from_file("Server.cpp")
file_template.context(server_impls = server_impls).render_file()
