### prevent discovery ###
from autojinja import *

######################################
###         Arg definition         ###
######################################

### Template
function_arg_def_t = RawTemplate.from_string("""
{%- if Default != None -%}
{{ Type }} {{ Name }} = {{ Default }}
{%- else -%}
{{ Type }} {{ Name }}
{%- endif -%}
""".strip())

### Generates one XML argument
def function_arg_def(xarg):
    return function_arg_def_t.context(Type = xarg.attrib['type'],
                                      Name = xarg.attrib['name'],
                                      Default = xarg.attrib.get('default')).render()

### Generates several XML arguments
def function_arg_defs(xargs):
    for xarg in xargs:
        yield function_arg_def(xarg)

######################################
###       Arg implementation       ###
######################################

### Template
function_arg_impl_t = RawTemplate.from_string("""
{{ Type }} {{ Name }}
""".strip())

### Generates one XML argument
def function_arg_impl(xarg):
    return function_arg_impl_t.context(Type = xarg.attrib['type'],
                                       Name = xarg.attrib['name']).render()

### Generates several XML arguments
def function_arg_impls(xargs):
    for xarg in xargs:
        yield function_arg_impl(xarg)

######################################
###            Arg call            ###
######################################

### Template
function_arg_call_t = RawTemplate.from_string("""
{{ Name }}
""".strip())

### Generates one XML argument
def function_arg_call(xarg):
    return function_arg_call_t.context(Name = xarg.attrib['name']).render()

### Generates several XML arguments
def function_arg_calls(xargs):
    for xarg in xargs:
        yield function_arg_call(xarg)
