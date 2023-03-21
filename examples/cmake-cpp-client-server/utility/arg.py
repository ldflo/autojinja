### prevent discovery ###
import autojinja
from lxml import etree
from typing import Generator, List

######################################
###         Arg definition         ###
######################################

### Template
function_arg_def_t = autojinja.RawTemplate.from_string("""
{%- if Default != None -%}
{{ Type }} {{ Name }} = {{ Default }}
{%- else -%}
{{ Type }} {{ Name }}
{%- endif -%}
""".strip())

### Generates one XML argument
def function_arg_def(xarg: etree._Element) -> str:
    return function_arg_def_t.context(Type = xarg.attrib['type'],
                                      Name = xarg.attrib['name'],
                                      Default = xarg.attrib.get('default')).render()

### Generates several XML arguments
def function_arg_defs(xargs: List[etree._Element]) -> Generator[str, None, None]:
    for xarg in xargs:
        yield function_arg_def(xarg)

######################################
###       Arg implementation       ###
######################################

### Template
function_arg_impl_t = autojinja.RawTemplate.from_string("""
{{ Type }} {{ Name }}
""".strip())

### Generates one XML argument
def function_arg_impl(xarg: etree._Element) -> str:
    return function_arg_impl_t.context(Type = xarg.attrib['type'],
                                       Name = xarg.attrib['name']).render()

### Generates several XML arguments
def function_arg_impls(xargs: List[etree._Element]) -> Generator[str, None, None]:
    for xarg in xargs:
        yield function_arg_impl(xarg)

######################################
###            Arg call            ###
######################################

### Template
function_arg_call_t = autojinja.RawTemplate.from_string("""
{{ Name }}
""".strip())

### Generates one XML argument
def function_arg_call(xarg: etree._Element) -> str:
    return function_arg_call_t.context(Name = xarg.attrib['name']).render()

### Generates several XML arguments
def function_arg_calls(xargs: List[etree._Element]) -> Generator[str, None, None]:
    for xarg in xargs:
        yield function_arg_call(xarg)
