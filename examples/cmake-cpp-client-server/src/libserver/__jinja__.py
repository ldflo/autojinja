from autojinja import *
from lxml import etree
import utility

# Read XML
xroot = etree.parse(os.environ["SERVER_XML"])
xfunctions = xroot.xpath("Function")

#######################################
###           ServerApi.h           ###
#######################################

# Load 'ServerApi.h' file as a template
file_template = CogTemplate.from_file("ServerApi.h")
### Generate 'ServerApi.h'
file_template.context(api_defs = utility.function_defs(xfunctions)).render_file()

#######################################
###          ServerApi.cpp          ###
#######################################

### Prepare a template for server API implementations
implementation = RawTemplate.from_string("""
// <<[ impl_{{ Name }} ]>>
static_assert(false, "ServerApi::{{ Name }} is not implemented...");
// <<[ end ]>>
""".strip())

# Prepare a function for generating above template
def implementation_func(xfunction):
    return implementation.context(Name = xfunction.attrib['name']).render()

# Load 'ServerApi.cpp' file as a template
file_template = CogTemplate.from_file("ServerApi.cpp")
### Generate 'ServerApi.cpp'
file_template.context(api_impls = utility.function_impls(xfunctions, implementation_func)).render_file()

#######################################
###            Server.cpp           ###
#######################################

### Prepare a template for server API forwardings
implementation = RawTemplate.from_string("""
case {{ Index }}u: { /* {{ Name }} */
    {% for Arg in Args %}
    {{ Arg.type }} {{ Arg.name }} = deserialize<{{ Arg.type }}>(ptr);
    {% endfor %}
    {{ ReturnType }} result = ServerApi::{{ Call }};
    shared_memory::clear();
    serialize(result, shared_memory::ptr);
} break;
""".strip())

# Prepare a function for generating above template
def generate_implementations(xfunctions):
    for idx, xfunction in enumerate(xfunctions):
        yield implementation.context(Index = idx+1,
                                     Name = xfunction.attrib['name'],
                                     Args = generator_args(xfunction.xpath("Arg")),
                                     ReturnType = xfunction.xpath("ReturnType/@type")[0],
                                     Call = utility.function_call(xfunction)).render()

# Prepare a context generator for above template
def generator_args(xargs):
    for xarg in xargs:
        class Arg:
            name = xarg.attrib['name']
            type = xarg.attrib['type'].replace("const", "").replace("&", "").replace("*", "").strip()
        yield Arg

# Load 'Server.cpp' file as a template
file_template = CogTemplate.from_file("Server.cpp")
### Generate 'Server.cpp'
file_template.context(server_impls = generate_implementations(xfunctions)).render_file()
