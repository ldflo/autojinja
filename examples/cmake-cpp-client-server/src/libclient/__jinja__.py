from autojinja import *
from lxml import etree
import utility

# Read XML
xroot = etree.parse(os.environ["SERVER_XML"])
xfunctions = xroot.xpath("Function")

#######################################
###           ClientApi.h           ###
#######################################

# Load 'ClientApi.h' file as a template
file_template = CogTemplate.from_file("ClientApi.h")
### Generate 'ClientApi.h'
file_template.context(api_defs = utility.function_defs(xfunctions)).render_file()

#######################################
###          ClientApi.cpp          ###
#######################################

### Prepare a template for client API implementations
implementation = RawTemplate.from_string("""
std::unique_lock<std::mutex> lock(shared_memory::mutex);
shared_memory::clear();
serialize({{ Index }}u /* {{ Name }} */, shared_memory::ptr);
{% for Arg in Args %}
serialize({{ Arg.attrib['name'] }}, shared_memory::ptr);
{% endfor %}
shared_memory::cv.notify_one(); // Send parameters
shared_memory::cv.wait(lock); // Wait for result
char* ptr = shared_memory::buffer;
return deserialize<{{ ReturnType }}>(ptr);
""".strip())

# Prepare a function for generating above template
idx = 0
def implementation_func(xfunction):
    global idx
    idx += 1
    return implementation.context(Index = idx,
                                  Name = xfunction.attrib['name'],
                                  Args = xfunction.xpath("Arg"),
                                  ReturnType = xfunction.xpath("ReturnType/@type")[0]).render()

# Load 'ClientApi.cpp' file as a template
file_template = CogTemplate.from_file("ClientApi.cpp")
### Generate 'ClientApi.cpp'
file_template.context(api_impls = utility.function_impls(xfunctions, implementation_func)).render_file()