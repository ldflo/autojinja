### prevent discovery ###
from autojinja import *
from arg import *

#######################################
###       Function definition       ###
#######################################

### Template
function_def_t = RawTemplate.from_string("""
/// @brief {{ Description }}
{{ ReturnType }} {{ Name }}({{ ', '.join(Args) }});
""".strip())

### Generates one XML function
def function_def(xfunction):
    return function_def_t.context(Description = xfunction.xpath("Description/@value")[0],
                                  ReturnType = xfunction.xpath("ReturnType/@type")[0],
                                  Name = xfunction.attrib['name'],
                                  Args = function_arg_defs(xfunction.xpath("Arg"))).render()

### Generates several XML functions
def function_defs(xfunctions):
    for xfunction in xfunctions:
        yield function_def(xfunction)

#######################################
###     Function implementation     ###
#######################################

### Template
function_impl_t = RawTemplate.from_string("""
/// @brief {{ Description }}
{{ ReturnType }} {{ Name }}({{ ', '.join(Args) }}) {
    {% for line in Implementation.split('\n') %}
    {{ line }}
    {% endfor %}
}
""".strip())

### Generates one XML function
def function_impl(xfunction, implementation_func = lambda xfunction:None):
    return function_impl_t.context(Description = xfunction.xpath("Description/@value")[0],
                                   ReturnType = xfunction.xpath("ReturnType/@type")[0],
                                   Name = xfunction.attrib['name'],
                                   Args = function_arg_impls(xfunction.xpath("Arg")),
                                   Implementation = implementation_func(xfunction)).render()

### Generates several XML functions
def function_impls(xfunctions, implementation_func = lambda xfunction:None):
    for xfunction in xfunctions:
        yield function_impl(xfunction, implementation_func)

#######################################
###          Function call          ###
#######################################

### Template
function_call_t = RawTemplate.from_string("""
{{ Name }}({{ ', '.join(Args) }})
""".strip())

### Generates one XML function
def function_call(xfunction):
    return function_call_t.context(Name = xfunction.attrib['name'],
                                   Args = function_arg_calls(xfunction.xpath("Arg"))).render()

### Generates several XML functions
def function_calls(xfunctions):
    for xfunction in xfunctions:
        yield function_call(xfunction)
