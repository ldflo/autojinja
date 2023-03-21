### prevent discovery ###
import autojinja
from arg import *
from lxml import etree
from typing import Callable, Generator, List, Optional

#######################################
###       Function definition       ###
#######################################

### Template
function_def_t = autojinja.RawTemplate.from_string("""
/// @brief {{ Description }}
{{ ReturnType }} {{ Name }}({{ ', '.join(Args) }});
""".strip())

### Generates one XML function
def function_def(xfunction: etree._Element) -> str:
    return function_def_t.context(Description = xfunction.xpath("Description/@value")[0],
                                  ReturnType = xfunction.xpath("ReturnType/@type")[0],
                                  Name = xfunction.attrib['name'],
                                  Args = function_arg_defs(xfunction.xpath("Arg"))).render()

### Generates several XML functions
def function_defs(xfunctions: List[etree._Element]) -> Generator[str, None, None]:
    for xfunction in xfunctions:
        yield function_def(xfunction)

#######################################
###     Function implementation     ###
#######################################

### Template
function_impl_t = autojinja.RawTemplate.from_string("""
/// @brief {{ Description }}
{{ ReturnType }} {{ Name }}({{ ', '.join(Args) }}) {
    {% for line in Implementation.split('\n') %}
    {{ line }}
    {% endfor %}
}
""".strip())

### Generates one XML function
def function_impl(xfunction: etree._Element, implementation_func: Optional[Callable[[etree._Element], str]] = lambda xfunction: None) -> str:
    return function_impl_t.context(Description = xfunction.xpath("Description/@value")[0],
                                   ReturnType = xfunction.xpath("ReturnType/@type")[0],
                                   Name = xfunction.attrib['name'],
                                   Args = function_arg_impls(xfunction.xpath("Arg")),
                                   Implementation = implementation_func(xfunction)).render()

### Generates several XML functions
def function_impls(xfunctions: List[etree._Element], implementation_func: Optional[Callable[[etree._Element], str]] = lambda xfunction: None) -> str:
    for xfunction in xfunctions:
        yield function_impl(xfunction, implementation_func)

#######################################
###          Function call          ###
#######################################

### Template
function_call_t = autojinja.RawTemplate.from_string("""
{{ Name }}({{ ', '.join(Args) }})
""".strip())

### Generates one XML function
def function_call(xfunction: etree._Element) -> str:
    return function_call_t.context(Name = xfunction.attrib['name'],
                                   Args = function_arg_calls(xfunction.xpath("Arg"))).render()

### Generates several XML functions
def function_calls(xfunctions: List[etree._Element]) -> Generator[str, None, None]:
    for xfunction in xfunctions:
        yield function_call(xfunction)
