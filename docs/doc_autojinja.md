# Documentation

# Introduction

**autojinja** is a Python3 module that allows generating code inside any file using [Jinja templates](https://github.com/pallets/jinja) in between comments. It aims to assist development workflows by using simple Python3 scripts that perform content generation of neighboring files, which enables generating code next to traditionally hand-made code efficiently.

It includes :
- Content generation in any file that accepts comments
- Ability to maintain hand-made code inside generated code
- Simple integration in build pipelines and existing codebases

**autojinja** can be seen as a _preprocessor_ for most file formats, and works great with any codebase as it automates writing code manually. It shines out even more when working with metadata files (such as XML or JSON files) that centralize information which later needs to be generated across various scattered files in the codebase.

## Installation

```shell
$ pip install autojinja
```

### Dependencies

**autojinja** only depends on [Jinja2](https://github.com/pallets/jinja) and consequently supports Python 3.6 and newer.

## Table of content

- [Overview](#overview)
- [Scripting API](#scripting-api)
  - [Content generation](#content-generation)
  - [Hand-made modifications](#hand-made-modifications)
  - [`RawTemplate` class](#class-autojinjarawtemplate)
  - [`CogTemplate` class](#class-autojinjacogtemplate)
  - [`JinjaTemplate` class](#class-autojinjajinjatemplate)
  - [`ParserSettings` class](#class-autojinjaparsersettings)
- [Markers](#markers)
  - [Indentation](#indentation)
  - [Exceptions](#exceptions)
  - [Syntax rules](#syntax-rules)
  - [Generation rules](#generation-rules)
  - [Markers removal](#markers-removal)
  - [Advanced usage](#advanced-usage)
- [Executable CLI](#executable-cli)
  - [Environment variables](#environment-variables)
- [Advanced Jinja2 features](#advanced-jinja2-features)

# Overview

**autojinja** is both a library module and an executable module :

### Library

The library part allows writing Python scripts that perform generation, using simple Python objects wrapped around Jinja templates. You can read [this blog](https://zetcode.com/python/jinja/) if you're not familiar with Jinja2 (and more generally templating engines), as it is the central part of **autojinja** [scripting API](#scripting-api).

For instance, a basic Jinja template usage with **autojinja** is written like so :

```python
from autojinja import RawTemplate

template = RawTemplate.from_string("My name is {{ firstname }} {{ lastname }} !")
result = template.context(firstname = "John", lastname = "Doe").render()

print(result) # My name is John Doe !
```

### Executable

The executable part allows to easily find and execute the written generation scripts. It also allows passing various options that make it easier to integrate such generation process in existing workflows.

Please note that these scripts can be directly executed with Python. Executing them with **autojinja** doesn't affect the generation output directly, besides providing environment variables, as described in the [executable CLI](#executable-cli) section.

For instance, explicitly calling generation scripts with **autojinja** CLI is done with the command :

```shell
$ autojinja script1.py dir/script2.py ...
```

The overall process can be summarized as such :

```
           autojinja [OPTIONS]                                        execute script1.py     →     generate file1.cpp
        (PYTHON_SCRIPT|DIRECTORY)     →     resolve scripts     →     execute script2.py     →     generate file2.h
                   ...                                                ...                    →     ...
```

# Scripting API

The scripting API provides 3 template classes to perform generation of various kinds, namely [`RawTemplate`](#class-autojinjarawtemplate), [`CogTemplate`](#class-autojinjacogtemplate) and [`JinjaTemplate`](#class-autojinjajinjatemplate), all using Jinja2 internally.

Each of these templates is loaded using the `from_string` or `from_file` static methods...

```python
from autojinja import *

t1 = RawTemplate.from_string("Hello {{ firstname }} {{ lastname }} !")
t1 = RawTemplate.from_file("template.txt")

t2 = CogTemplate.from_string("...")
t2 = CogTemplate.from_file("main.cpp")

t3 = JinjaTemplate.from_string("...")
t3 = JinjaTemplate.from_file("template.cpp")
```

...and performs generation using the `render` or `render_file` methods, given variables beforehand with the `context` method :

```python
r1 = t1.context(firstname = "John", lastname = "Doe").render()
r1 = t1.context(firstname = "John", lastname = "Doe").render_file("output.txt")

r2 = t2.context(...).render()
r2 = t2.context(...).render_file()

r3 = t3.context(...).render()
r3 = t3.context(...).render_file("output.cpp")
```

Here is a table summarizing what `RawTemplate`, `CogTemplate` and `JinjaTemplate` are capable of :

| Class           | Description | Content generation | Hand-made modifications |
|:---------------:|:-:|:-:|:-:|
| `RawTemplate`   | Renders native Jinja templates | ❌ | ❌ |
| `CogTemplate`   | Renders any file with special markers | ✔️ | ✔️ |
| `JinjaTemplate` | Renders native Jinja templates with special markers | ✔️ | ✔️ |

## Content generation

Content generation consists in generating parts of an existing file thanks to dedicated sections that delimit where the generation takes place. This technique is made possible for all files accepting comments, and allows defining [Jinja templates](https://github.com/pallets/jinja) directly in such files without breaking them.

For example, let's suppose we have a C++ file we want to generate inside. To do this, we need to write our Jinja template between `[[[` and `]]]` markers, followed by an `[[[end]]]` marker :

```cpp
// main.cpp
#include <iostream>

int main() {
  std::cout << "Hello world !" << std::endl;
  // [[[ std::cout << "{{ value }}" << std::endl; ]]]  // Jinja template
  // [[[ end ]]]                                       // Code will be generated in between
  return 0;
}
```

The template can then be generated with a Python3 script that provides the `value` variable :

```python
# main.py
from autojinja import CogTemplate

template = CogTemplate.from_file("main.cpp")
template.context(value = "Python here !").render_file()
```

Calling the script will modify our C++ file as such :

```cpp
// main.cpp
#include <iostream>

int main() {
  std::cout << "Hello world !" << std::endl;
  // [[[ std::cout << "{{ value }}" << std::endl; ]]]  // Jinja template
  std::cout << "Python here !" << std::endl;
  // [[[ end ]]]                                       // Code will be generated in between
  return 0;
}
```

This technique is greatly inspired by [Cog](https://github.com/nedbat/cog), but adapted to work with Jinja templating engine. When performing generation again, the content inside the markers is entirely replaced by the new generation.

For more information on markers between comments, see the [markers](#markers) section.

## Hand-made modifications

Modification by hand of generated code is made possible by using special sections that are preserved across new generations. To do this, we need to name a section between `<<[` and `]>>` markers, followed by an `<<[end]>>` marker :

```cpp
// main.cpp
#include <iostream>

// [[[
// int main() {
//
//   std::cout << "{{ value }}" << std::endl;
//   // <<[ impl ]>>  // Manually editable section named 'impl'
//   return 0;
//   // <<[ end ]>>   // End of section
//
// }
// ]]]
int main() {

  std::cout << "Python here !" << std::endl;
  // <<[ impl ]>>  // Manually editable section named 'impl'
  std::cout << "Modified by hand" << std::endl;
  return 1;
  // <<[ end ]>>   // End of section

}
// [[[ end ]]]
```

When a new generation occurs, all previous sections are retrieved from the destination file and then reinserted into the new generation, inside each corresponding section with same name.

All previous sections of a destination file must be reinserted when performing a new generation, otherwise it will be considered as code loss and generation will be aborted. Human intervention is required to deal with such scenarios.

For more information on these markers, see the [markers](#markers) section.

## _class_ autojinja.**RawTemplate**:

The `RawTemplate` object simply wraps a `jinja2.Template` which allows rendering native Jinja templates, just as you would do with Jinja2. These templates completely ignore special markers or hand-made modifications and are mostly used for generating simple intermediate results within Python scripts :

```python
# script.py
from autojinja import RawTemplate

template = RawTemplate.from_file("template.txt")
template.context(firstname = "John", lastname = "Doe").render_file("output.txt")
```

`template.txt` :

```
// template.txt
Hello, my name is {{firstname}} {{lastname}} !
```

`output.txt` :

```
// template.txt
Hello, my name is John Doe !
```

- ### _RawTemplate_.**from_file**(_input, output=None, encoding=None, newline=None, globals=None_):

    Loads a Jinja template from a file.

    Parameters :
    - **input: `str`** : filepath containing the Jinja template
    - **output: `Optional[str]`** : default output filepath when generating with `render_file` method
    - **encoding: `Optional[str]`** : default encoding used when reading the file and when generating with `render_file` method. Default value is `utf-8`
    - **newline: `Optional[str]`** : default newline when generating with `render_file` method. Default value is `\n`
    - **globals: `Optional[dict[str, Any]]`** : dictionary of variables available in the template

    Return type :
    - `autojinja.RawTemplate`

- ### _RawTemplate_.**from_string**(_string, output=None, encoding=None, newline=None, globals=None_):

    Loads a Jinja template from a string.

    Parameters :
    - **string: `str`** : Jinja template given as a string
    - **output: `Optional[str]`** : default output filepath when generating with `render_file` method
    - **encoding: `Optional[str]`** : default encoding when generating with `render_file` method. Default value is `utf-8`
    - **newline: `Optional[str]`** : default newline when generating with `render_file` method. Default value is `\n`
    - **globals: `Optional[dict[str, Any]]`** : dictionary of variables available in the template

    Return type :
    - `autojinja.RawTemplate`

- ### **context**(_self, &ast;args, &ast;&ast;kwargs_):

    Provides variables for rendering the template with the `render` / `render_file` methods.

    Parameters :
    - **&ast;args**, **&ast;&ast;kwargs** : variables available in the template

    Return type :
    - `autojinja.RawTemplateContext`

- ### **render_file**(_self, output=None, encoding=None, newline=None_):

    Renders the template to a file and returns the generation output.

    Parameters :
    - **output: `Optional[str]`** : output filepath for generated file. Default value is specified in constructor
    - **encoding: `Optional[str]`** : encoding for generated file. Default value is specified in constructor
    - **newline: `Optional[str]`** : newline for generated file. Default value is specified in constructor

    Return type :
    - `str`

- ### **render**(_self_):

    Renders the template and returns the generation output.

    Return type :
    - `str`

## _class_ autojinja.**CogTemplate**:

The `CogTemplate` object allows rendering a file that contains several Jinja templates delimited by [cog markers](#markers), and deals with hand-made modifications enclosed within [edit markers](#markers). Each Jinja template is individually generated with a [`RawTemplate`](#class-autojinjarawtemplate) and then re-evaluated using a `CogTemplate`, allowing recursive generation. The same applies when reinserting hand-made sections, which can recursively contain cog markers and edit markers :

```python
# script.py
from autojinja import CogTemplate

template = CogTemplate.from_file("main.cpp")
template.context(var1 = "Hello world !", var2 = "42").render_file()
```

`main.cpp` before generation :

```cpp
// main.cpp
#include <iostream>

void main() {
    std::cout << "{{ var1 }}" << std::endl;

    // [[[ std::cout << "{{ var1 }}" << std::endl; ]]]
    std::cout << "This has been modified" << std::endl;
    // [[[ end ]]]

    // <<[ edit1 ]>>
      std::cout << "{{ var1 }}" << std::endl;
      // [[[ std::cout << "{{ var2 }}" << std::endl; ]]]
      // [[[ end ]]]
    // <<[ edit1 ]>>

    int value = /*[[[ {{ var2 }} ]]]*/ /*[[[end]]]*/;
}
```

`main.cpp` after generation :

```cpp
// main.cpp
#include <iostream>

void main() {
    std::cout << "{{ var1 }}" << std::endl;

    // [[[ std::cout << "{{ var1 }}" << std::endl; ]]]
    std::cout << "Hello world !" << std::endl;
    // [[[ end ]]]

    // <<[ edit1 ]>>
      std::cout << "{{ var1 }}" << std::endl;
      // [[[ std::cout << "{{ var2 }}" << std::endl; ]]]
      std::cout << "42" << std::endl;
      // [[[ end ]]]
    // <<[ edit1 ]>>

    int value = /*[[[ {{ var2 }} ]]]*/ 42 /*[[[end]]]*/;
}
```

- ### _CogTemplate_.**from_file**(_input, output=None, settings=None, remove_markers=None, encoding=None, newline=None, globals=None_):

    Loads a file containing Jinja templates and hand-made sections enclosed within special markers.

    Parameters :
    - **input: `str`** : filepath containing Jinja templates and hand-made sections enclosed within special markers
    - **output: `Optional[str]`** : default output filepath when generating with `render_file` method. Default value is _input_ parameter value
    - **settings: `Optional[autojinja.parser.ParserSettings]`** : [`ParserSettings`](#class-autojinjaparsersettings) used to resolve markers. Default value is `ParserSettings()`remove_markers
    - **remove_markers: `Optional[bool]`** : removes cog and edits markers from generated output. Default value is _settings_ parameter
    - **encoding: `Optional[str]`** : default encoding used when reading the file and when generating with `render_file` method. Default value is _settings_ parameter
    - **newline: `Optional[str]`** : default newline when generating with `render_file` method. Default value is _settings_ parameter
    - **globals: `Optional[dict[str, Any]]`** : dictionary of variables available in the template

    Return type :
    - `autojinja.CogTemplate`

- ### _CogTemplate_.**from_string**(_string, output=None, settings=None, encoding=None, remove_markers=None, newline=None, globals=None_):

    Loads a string containing Jinja templates and hand-made sections enclosed within special markers.

    Parameters :
    - **string: `str`** : string containing Jinja templates and hand-made sections enclosed within special markers
    - **output: `Optional[str]`** : default output filepath when generating with `render_file` method
    - **settings: `Optional[autojinja.parser.ParserSettings]`** : [`ParserSettings`](#class-autojinjaparsersettings) used to resolve markers. Default value is `ParserSettings()`
    - **remove_markers: `Optional[bool]`** : removes cog and edits markers from generated output. Default value is _settings_ parameter
    - **encoding: `Optional[str]`** : default encoding when generating with `render_file` method. Default value is _settings_ parameter
    - **newline: `Optional[str]`** : default newline when generating with `render_file` method. Default value is _settings_ parameter
    - **globals: `Optional[dict[str, Any]]`** : dictionary of variables available in the template

    Return type :
    - `autojinja.CogTemplate`

- ### **context**(_self, &ast;args, &ast;&ast;kwargs_):

    Provides variables for rendering the template with the `render` / `render_file` methods.

    Parameters :
    - **&ast;args**, **&ast;&ast;kwargs** : variables available in the template

    Return type :
    - `autojinja.CogTemplateContext`

- ### **render_file**(_self, output=None, remove_markers=None, encoding=None, newline=None_):

    Renders the template to a file and returns the generation output. If the file already exists, hand-made modifications enclosed within edit markers in that file are retrieved and then reinserted into the generated output.

    Parameters :
    - **output: `Optional[str]`** : output filepath for generated file. Default value is specified in constructor
    - **remove_markers: `Optional[bool]`** : removes cog and edits markers from generated output. Default value is specified in constructor
    - **encoding: `Optional[str]`** : encoding for generated file. Default value is specified in constructor
    - **newline: `Optional[str]`** : newline for generated file. Default value is specified in constructor

    Return type :
    - `str`

- ### **render**(_self, output=None, remove_markers=None_):

    Renders the template and returns the generation output.

    Parameters :
    - **output: `Optional[str]`** : optional string of previous generation containing edit markers to reinsert
    - **remove_markers: `Optional[bool]`** : removes cog and edits markers from generated output. Default value is specified in constructor

    Return type :
    - `str`

## _class_ autojinja.**JinjaTemplate**:

The `JinjaTemplate` object is similar to [`RawTemplate`](#class-autojinjarawtemplate) with the added functionalities of [`CogTemplate`](#class-autojinjacogtemplate). Basically, it allows rendering a Jinja template that deals with hand-made modifications enclosed within [edit markers](#markers). It works the same as `CogTemplate`, except everything outside special markers is considered a Jinja template, which is generated with a `RawTemplate` and then re-evaluated using a `CogTemplate` :

```python
# script.py
from autojinja import JinjaTemplate

template = JinjaTemplate.from_file("template.cpp")
template.context(var1 = "Hello world !", var2 = "42").render_file("output.cpp")
```

`template.cpp` :

```cpp
// template.cpp
#include <iostream>

void main() {
    std::cout << "{{ var1 }}" << std::endl;

    // [[[ std::cout << "{{ var1 }}" << std::endl; ]]]
    // [[[ end ]]]

    // <<[ edit1 ]>>
    // <<[ edit1 ]>>

    int value = {{ var2 }};
    value += /*<<[ edit2 ]>*/ 1 /*<<[ end ]>>*/;
}
```

`output.cpp` before generation :

```cpp
// output.cpp
#include <iostream>

void main() {
    std::cout << "This has been modified" << std::endl;

    // [[[ std::cout << "{{ var1 }}" << std::endl; ]]]
    // [[[ end ]]]

    // <<[ edit1 ]>>
      std::cout << "{{ var1 }}" << std::endl;
      // [[[ std::cout << "{{ var2 }}" << std::endl; ]]]
      // [[[ end ]]]
    // <<[ edit1 ]>>

    int value = 42;
    value += /*<<[ edit2 ]>*/ 123 /*<<[ end ]>>*/;
}
```

`output.cpp` after generation :

```cpp
// template.cpp
#include <iostream>

void main() {
    std::cout << "Hello world !" << std::endl;

    // [[[ std::cout << "{{ var1 }}" << std::endl; ]]]
    std::cout << "Hello world !" << std::endl;
    // [[[ end ]]]

    // <<[ edit1 ]>>
      std::cout << "{{ var1 }}" << std::endl;
      // [[[ std::cout << "{{ var2 }}" << std::endl; ]]]
      std::cout << "42" << std::endl;
      // [[[ end ]]]
    // <<[ edit1 ]>>

    int value = 42;
    value += /*<<[ edit2 ]>*/ 123 /*<<[ end ]>>*/;
}
```

- ### _JinjaTemplate_.**from_file**(_input, output=None, settings=None, remove_markers=None, encoding=None, newline=None, globals=None_):

    Loads a Jinja template containing Jinja templates and hand-made sections enclosed within special markers.

    Parameters :
    - **input: `str`** : filepath containing the Jinja template with Jinja templates and hand-made sections enclosed within special markers
    - **output: `Optional[str]`** : default output filepath when generating with `render_file` method
    - **settings: `Optional[autojinja.parser.ParserSettings]`** : [`ParserSettings`](#class-autojinjaparsersettings) used to resolve markers. Default value is `ParserSettings()`
    - **remove_markers: `Optional[bool]`** : removes cog and edits markers from generated output. Default value is _settings_ parameter
    - **encoding: `Optional[str]`** : default encoding used when reading the file and when generating with `render_file` method. Default value is _settings_ parameter
    - **newline: `Optional[str]`** : default newline when generating with `render_file` method. Default value is _settings_ parameter
    - **globals: `Optional[dict[str, Any]]`** : dictionary of variables available in the template

    Return type :
    - `autojinja.JinjaTemplate`

- ### _JinjaTemplate_.**from_string**(_string, output=None, settings=None, encoding=None, remove_markers=None, newline=None, globals=None_):

    Loads a Jinja template as a string containing Jinja templates and hand-made sections enclosed within special markers.

    Parameters :
    - **string: `str`** : string containing the Jinja template with Jinja templates and hand-made sections enclosed within special markers
    - **output: `Optional[str]`** : default output filepath when generating with `render_file` method
    - **settings: `Optional[autojinja.parser.ParserSettings]`** : [`ParserSettings`](#class-autojinjaparsersettings) used to resolve markers. Default value is `ParserSettings()`
    - **remove_markers: `Optional[bool]`** : removes cog and edits markers from generated output. Default value is _settings_ parameter
    - **encoding: `Optional[str]`** : default encoding when generating with `render_file` method. Default value is _settings_ parameter
    - **newline: `Optional[str]`** : default newline when generating with `render_file` method. Default value is _settings_ parameter
    - **globals: `Optional[dict[str, Any]]`** : dictionary of variables available in the template

    Return type :
    - `autojinja.JinjaTemplate`

- ### **context**(_self, &ast;args, &ast;&ast;kwargs_):

    Provides variables for rendering the template with the `render` / `render_file` methods.

    Parameters :
    - **&ast;args**, **&ast;&ast;kwargs** : variables available in the template

    Return type :
    - `autojinja.JinjaTemplateContext`

- ### **render_file**(_self, output=None, remove_markers=None, encoding=None, newline=None_):

    Renders the template to a file and returns the generation output. If the file already exists, hand-made modifications enclosed within edit markers in that file are retrieved and then reinserted into the generated output.

    Parameters :
    - **output: `Optional[str]`** : output filepath for generated file. Default value is specified in constructor
    - **remove_markers: `Optional[bool]`** : removes cog and edits markers from generated output. Default value is specified in constructor
    - **encoding: `Optional[str]`** : encoding for generated file. Default value is specified in constructor
    - **newline: `Optional[str]`** : newline for generated file. Default value is specified in constructor

    Return type :
    - `str`

- ### **render**(_self, output=None, remove_markers=None_):

    Renders the template and returns the generation output.

    Parameters :
    - **output: `Optional[str]`** : optional string of previous generation containing edit markers to reinsert
    - **remove_markers: `Optional[bool]`** : removes cog and edits markers from generated output. Default value is specified in constructor

    Return type :
    - `str`

## _class_ autojinja.**ParserSettings**:

The `ParserSettings` object allows to specify the literal tokens used for resolving [markers](#markers) inside a file. Some generation settings are also configurable :

```python
# script.py
from autojinja import CogTemplate
from autojinja import ParserSettings

settings = ParserSettings(cog_open = "/**", cog_close = "**/", cog_as_comment = True)

template = CogTemplate.from_file("main.cpp", settings = settings)
template.context(var1 = "42").render_file()
```

`main.cpp` before generation :

```cpp
// main.cpp
int main() {
    return /** {{ var1 }} **/ 0 /** end **/;
}
```

`main.cpp` after generation :

```cpp
// main.cpp
int main() {
    return /** {{ var1 }} **/ 42 /** end **/;
}
```

- ### **&#95;&#95;init&#95;&#95;**(_self, &ast;args, &ast;&ast;kwargs_):

    Constructs a `ParserSettings` object with the provided arguments.

    Parameters :
    - **cog_open: `str`** : open token for cog markers. Default value is `[[[`
    - **cog_close: `str`** : close token for cog markers. Default value is `]]]`
    - **cog_end: `str`** : end token for cog markers. Default value is `end`
    - **cog_as_comment: `bool`** : indicates that cog markers are comment tokens. Default value is `False`. See the [markers](#markers) section for more information
    - **edit_open: `str`** : open token for edit markers. Default value is `<<[`
    - **edit_close: `str`** : close token for edit markers. Default value is `]>>`
    - **edit_end: `str`** : end token for edit markers. Default value is `end`
    - **edit_as_comment: `bool`** : indicates that edit markers are comment tokens. Default value is `False`. See the [markers](#markers) section for more information
    - **remove_markers: `Optional[bool]`** : removes cog and edits markers from generated output. Default value is `AUTOJINJA_REMOVE_MARKERS` environment variable value or `False`. See the [executable CLI](#executable-cli) section for more information
    - **encoding: `Optional[str]`** : default encoding when generating with `render_file` templates' method. Default value is `utf-8`
    - **newline: `Optional[str]`** : default newline when generating with `render_file` templates' method. Default value is `\n`

    Return type :
    - `ParserSettings`

# Markers

[Content generation](#content-generation) and [modification of generated code](#hand-made-modifications) are made possible by making use of special markers inside a file, namely _cog_ markers and _edit_ markers, which are always used in an _open-close-end_ sequence. These markers delimit sections that are composed of two parts :

- A _header_ part, delimited by the _open_ and _close_ markers
- A _body_ part, delimited by the _close_ and _end_ marker

| Attribute    | Jinja templates in between comments (cog markers) | Hand-made modifications (edit markers) |
|:------------:|:-:|:-:|
| Open marker  | `[[[` | `<<[` |
| Close marker | `]]]` | `]>>` |
| End marker   | `[[[ end ]]]` | `<<[ end ]>>` |
| Header       | Jinja template | Section name
| Body         | Generation output | Modifiable section

Here is a syntax summary :

```
Multiline forms :


    // [[[ ░░░░░░░░░░░░░░░░             // [[[
    // ░░░░░░░░░░░░░░░░░░░░             // ░░░░░░░░░░░░░░░░░░░░
    // ░░░░░░ Header ░░░░░░             // ░░░░░░ Header ░░░░░░             // <<[ ░░░░░ Header ░░░░░ ]>>
    // ░░░░░░░░░░░░░░░░░░░░             // ░░░░░░░░░░░░░░░░░░░░             ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    // ░░░░░░░░░░░░░░░░ ]]]             // ]]]                              ░░░░░░░░░░░░░ Body ░░░░░░░░░░░░░░
    ░░░░░░░░░░░░░░░░░░░░░░░░░░          ░░░░░░░░░░░░░░░░░░░░░░░░░░          ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    ░░░░░░░░░░ Body ░░░░░░░░░░          ░░░░░░░░░░ Body ░░░░░░░░░░          // <<[ end ]>>
    ░░░░░░░░░░░░░░░░░░░░░░░░░░          ░░░░░░░░░░░░░░░░░░░░░░░░░░
    // [[[ end ]]]                      // [[[ end ]]]

    ✔️ Cog markers                     ✔️ Cog markers                      ✔️ Cog markers
    ❌ Edit markers                    ❌ Edit markers                     ✔️ Edit markers


Inline form :

    // [[[ ░░░░░ Header ░░░░░ ]]] ░░░░░ Body ░░░░░ [[[ end ]]]

    ✔️ Cog markers
    ✔️ Edit markers

Extended inline form :

    /*<<[ ░░░░░ Header ░░░░░ ]>>*/ ░░░░░ Body ░░░░░ /*<<[ end ]>>*/

    ✔️ Cog markers
    ✔️ Edit markers
```

The _extended inline form_ is achieved by using any characters next to markers, other than spaces and tabulations.

## Indentation

For _multiline forms_, indentation of generated _bodies_ is automatically adjusted, based on the _open_ marker location or the preceding comment location if it exists :

```
- any character, space or tabulation
_ space or tabulation
+ any character

            ↱ resolved indentation
--------____++++____[[[ ░░░░░░░░░░░░░░░░
----------------____░░░░░░░░░░░░░░░░░░░░
----------------____░░░░░░ Header ░░░░░░
----------------____░░░░░░░░░░░░░░░░░░░░
----------------____░░░░░░░░░░░░ ]]]----
----[[[ end ]]]-------------------------  → indentation of end marker doesn't matter

Examples :

        [[[ ░░░░░░░░░░░░░░░░                    /**   [[[ ░░░░░░░░░░░░░░░░
        ░░░░░░░░░░░░░░░░░░░░                     *    ░░░░░░░░░░░░░░░░░░░░
        ░░░░░░ Header ░░░░░░                     *    ░░░░░░ Header ░░░░░░           // <<[ ░░░░░ Header ░░░░░ ]>>
        ░░░░░░░░░░░░░░░░░░░░                     *    ░░░░░░░░░░░░░░░░░░░░           ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
        ░░░░░░░░░░░░ ]]]                         *    ░░░░░░░░░░░░ ]]] **/           ░░░░░░░░░░░░░ Body ░░░░░░░░░░░░░░
        ░░░░░░░░░░░░░░░░░░░░░░░░░░              ░░░░░░░░░░░░░░░░░░░░░░░░░░           ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
        ░░░░░░░░░░ Body ░░░░░░░░░░              ░░░░░░░░░░ Body ░░░░░░░░░░           // <<[ end ]>>
        ░░░░░░░░░░░░░░░░░░░░░░░░░░              ░░░░░░░░░░░░░░░░░░░░░░░░░░
    [[[ end ]]]                             /*[[[ end ]]]*/
```

If the `cog_as_comment` or `edit_as_comment` option is enabled using a [`ParserSettings`](#class-autojinjaparsersettings) object, indentation is based on the _open_ marker location regardless of preceding comments. Since indentation and _header_ content are based on alignment, usage of tabulation characters must be replicated for each line at each exact same column. Substituting a tabulation with spaces is not allowed.

## Exceptions

Markers follow strict syntax rules in order to properly delimit the generated sections from the rest of the file, and also follow some generation rules to avoid bad generations from breaking the file or erasing parts of it.

Rules verification applies during creation of [`CogTemplate`](#class-autojinjacogtemplate) or [`JinjaTemplate`](#class-autojinjajinjatemplate) objects and when calling their `render` or `render_file` methods. When such verification fails, an exception is raised with a message explaining the failure and its location in the file :

```python
from autojinja import CogTemplate
from autojinja import exceptions

try:

    try:
        template = CogTemplate.from_file("main.cpp")
        template.context(...).render_file()
    except exceptions.ParsingException as e:
        raise e
    except exceptions.GenerationException as e:
        raise e

except exceptions.CommonException as e:
    raise e # Both 'parsing' and 'generation' exceptions
```

## Syntax rules

Parsing exceptions are raised for cog markers and edit markers indifferently, unless specified otherwise, in the following cases :

```
❌ Close marker is mandatory
    // [[[ ░░░░░ Header1 ░░░░░


❌ End marker is mandatory
    // [[[ ░░░░░ Header1 ░░░░░ ]]]


❌ Can't use an open marker on same line as the end marker of previous multiline forms
    // [[[ ░░░░░ Header1 ░░░░░ ]]]
    // [[[ end ]]] [[[ ░░░░░ Header2 ░░░░░ ]]] [[[ end ]]]


❌ Can't use a multiline form on same line as the end marker of previous inline forms
    // [[[ ░░░░░ Header1 ░░░░░ ]]] [[[ end ]]] [[[ ░░░░░ Header2 ░░░░░ ]]]
                                            // [[[ end ]]]


✔️ Valid if everything is inlined
    // [[[ ░░░░░ Header1 ░░░░░ ]]] [[[ end ]]] [[[ ░░░░░ Header2 ░░░░░ ]]] [[[ end ]]]


❌ Can't use an end marker on same line as the close marker of multiline headers
    // [[[
    // ░░░░░░░░░░░░░░░░░░░░
    // ░░░░░░ Header ░░░░░░
    // ░░░░░░░░░░░░░░░░░░░░
    // ]]] [[[ end ]]]


❌ Multiline headers and close markers must be properly indented
    // [[[
    ///░░░░░░░░░░░░░░░░░░░░
    // ░░░░░░ Header ░░░░░░
    // ░░░░░░░░░░░░░░░░░░░░
    //]]]
    // [[[ end ]]]

❌ Edit markers can't have multiline headers
    // <<[
    // ░░░░░░░░░░░░░░░░░░░░
    // ░░░░░░ Header ░░░░░░
    // ░░░░░░░░░░░░░░░░░░░░
    // ]>>
    // <<[ end ]>>

❌ Headers of edit markers must be unique among the whole file
    // <<[ ░░░░░ Header1 ░░░░░ ]>> <<[ end ]>>
    // <<[ ░░░░░ Header1 ░░░░░ ]>> <<[ end ]>>


❌ Can't break cog markers or edit markers enclosure
    // [[[ ░░░░░ Header1 ░░░░░ ]]]
        // <<[ ░░░░░ Header2 ░░░░░ ]>>
    // [[[ end ]]]
        // <<[ end ]>>


❌ Can't use edit markers directly inside other edit markers
    // <<[ ░░░░░ Header1 ░░░░░ ]>>
        // <<[ ░░░░░ Header2 ░░░░░ ]>>
        // <<[ end ]>>
    // <<[ end ]>>


✔️ Valid if edit markers are enclosed by cog markers
    // <<[ ░░░░░ Header1 ░░░░░ ]>>
        // [[[ ░░░░░ Header2 ░░░░░ ]]]
            // <<[ ░░░░░ Header3 ░░░░░ ]>>
            // <<[ end ]>>
        // [[[ end ]]]
    // <<[ end ]>>
```

## Generation rules

Generation exceptions are raised in the following cases :

```
❌ Can't generate a body containing several lines for inline forms
    // [[[ ░░░░░ Header1 ░░░░░ ]]] [[[ end ]]]     →     // [[[ ░░░░░ Header1 ░░░░░ ]]] ░░░░░░░░░░░░░░░░
                                                                                        ░░░░░ Body ░░░░░
                                                                                        ░░░░░░░░░░░░░░░░ [[[ end ]]]


❌ All previous edit markers must be generated again
    // [[[ ░░░░░ Header1 ░░░░░ ]]]         →     // [[[ ░░░░░ Header1 ░░░░░ ]]]
        // <<[ ░░░░░ Header2 ░░░░░ ]>>           // [[[ end ]]]
        // <<[ end ]>>
    // [[[ end ]]]

❌ Can't generate an edit marker twice in the whole file
    // [[[ ░░░░░ Header1 ░░░░░ ]]]         →     // [[[ ░░░░░ Header1 ░░░░░ ]]]
    // [[[ end ]]]                                   // <<[ ░░░░░ Header2 ░░░░░ ]>>
                                                     // <<[ end ]>>
                                                     // <<[ ░░░░░ Header2 ░░░░░ ]>>
                                                     // <<[ end ]>>
                                                 // [[[ end ]]]
```

## Markers removal

If the `remove_markers` option is enabled, all markers and headers are removed from generated outputs :

```
× line or character removed
→ generation

Multiline forms :

        [[[ ░░░░░░░░░░░░░░░░       ×              /**   [[[ ░░░░░░░░░░░░░░░░ ×
        ░░░░░░░░░░░░░░░░░░░░       ×               *    ░░░░░░░░░░░░░░░░░░░░ ×
        ░░░░░░ Header ░░░░░░       ×               *    ░░░░░░ Header ░░░░░░ ×           // <<[ ░░░░░ Header ░░░░░ ]>>     ×
        ░░░░░░░░░░░░░░░░░░░░       ×               *    ░░░░░░░░░░░░░░░░░░░░ ×           ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
        ░░░░░░░░░░░░ ]]]           ×               *    ░░░░░░░░░░░░ ]]] **/ ×           ░░░░░░░░░░░░░ Body ░░░░░░░░░░░░░░
        ░░░░░░░░░░░░░░░░░░░░░░░░░░                ░░░░░░░░░░░░░░░░░░░░░░░░░░             ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
        ░░░░░░░░░░ Body ░░░░░░░░░░                ░░░░░░░░░░ Body ░░░░░░░░░░             // <<[ end ]>>                    ×
        ░░░░░░░░░░░░░░░░░░░░░░░░░░                ░░░░░░░░░░░░░░░░░░░░░░░░░░
    [[[ end ]]]                    ×          /*[[[ end ]]]*/                 ×

                     ↓                                        ↓                                         ↓

        ░░░░░░░░░░░░░░░░░░░░░░░░░░                ░░░░░░░░░░░░░░░░░░░░░░░░░░             ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
        ░░░░░░░░░░ Body ░░░░░░░░░░                ░░░░░░░░░░ Body ░░░░░░░░░░             ░░░░░░░░░░░░░ Body ░░░░░░░░░░░░░░
        ░░░░░░░░░░░░░░░░░░░░░░░░░░                ░░░░░░░░░░░░░░░░░░░░░░░░░░             ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

Inline form :

    // [[[ ░░░░░ Header ░░░░░ ]]] ░░░░░ Body ░░░░░ [[[ end ]]]          →     // ░░░░░ Body ░░░░░
       ×××××××××××××××××××××××××××                ××××××××××××

Extended inline form :

    /*<<[ ░░░░░ Header ░░░░░ ]>>*/ ░░░░░ Body ░░░░░ /*<<[ end ]>>*/     →     ░░░░░ Body ░░░░░
    ×××××××××××××××××××××××××××××××                ××××××××××××××××
```

## Advanced usage

Sections delimited by edit markers can be retrieved as a dictionary by using the `edits_from_file` and `edits_from_string` functions, or by using the `edits` property of [`CogTemplate`](#class-autojinjacogtemplate) and [`JinjaTemplate`](#class-autojinjajinjatemplate) objects. Setting a dictionary back to the property will override the concerned values that are normally retrieved from the destination file and reinserted into the new generation :

```python
from autojinja import JinjaTemplate
from autojinja import utils

template = JinjaTemplate.from_file("template.cpp")
print(template.edits) # { "edit1" : None, "edit2" : "1" }

edits = utils.edits_from_file("output.cpp")
print(edits) # { "edit1" : "int value = 42;", "edit2" : "123" }

template.edits = { "edit1" : "int value = 0;", "edit2" : "321" }
template.context(var1 = "Hello world !", var2 = "42").render_file("output.cpp")
```

`template.cpp` :

```cpp
// template.cpp
#include <iostream>

void main() {
    std::cout << "{{ var1 }}" << std::endl;

    // <<[ edit1 ]>
    // <<[ end ]>>

    int value = {{ var2 }};
    value += /*<<[ edit2 ]>*/ 1 /*<<[ end ]>>*/;
}
```

`output.cpp` before generation :

```cpp
// output.cpp
#include <iostream>

void main() {
    std::cout << "Modified by hand" << std::endl;

    // <<[ edit1 ]>
    int value = 42;
    // <<[ end ]>>

    value += /*<<[ edit2 ]>*/ 123 /*<<[ end ]>>*/;
}
```

`output.cpp` after generation :

```cpp
// template.cpp
#include <iostream>

void main() {
    std::cout << "Hello world !" << std::endl;

    // <<[ edit1 ]>
    int value = 0;
    // <<[ end ]>>

    value += /*<<[ edit2 ]>*/ 321 /*<<[ end ]>>*/;
}
```

- ### _utils_.**edits_from_file**(_filepath, settings=None, encoding=None_):

    Returns the dictionary of all sections enclosed within edit markers inside a file.

    Parameters :
    - **filepath: `str`** : filepath containing edit markers
    - **settings: `Optional[autojinja.parser.ParserSettings]`** : [`ParserSettings`](#class-autojinjaparsersettings) used to resolve markers. Default value is `ParserSettings()`
    - **encoding: `Optional[str]`** : default encoding used when reading the file. Default value is `utf-8`

- ### _utils_.**edits_from_string**(_string, settings=None_):

    Returns the dictionary of all sections enclosed within edit markers inside a string.

    Parameters :
    - **string: `str`** : string containing edit markers
    - **settings: `Optional[autojinja.parser.ParserSettings]`** : [`ParserSettings`](#class-autojinjaparsersettings) used to resolve markers. Default value is `ParserSettings()`

# Executable CLI

The _Command Line Interface_ of **autojinja** allows finding and executing the Python scripts that perform generation. It provides discover mechanism to recursively find such scripts in listed directories, and also supports loading environment files which eases passing environment variables across generation scripts :

```console
$ autojinja --help
Visits directories and executes python scripts to perform content generation

Usage
-----
autojinja [OPTIONS] (PYTHON_SCRIPT | DIRECTORY)...

Examples
--------
autojinja script1.py script2.py
autojinja -a .

Arguments
---------
PYTHON_SCRIPT:
    Python script to execute
    The filepath must end with '.py' extension

DIRECTORY:
    Directory to visit
    Only works if '--search-filename' or '--search-tag' is enabled

OPTIONS:
    -f, --search-filename         Searches for python scripts named '__jinja__.py' in visited directories
    -t, --search-tag              Searches for python scripts tagged 'autojinja' in visited directories
    -r, --recursive               Recursively visits subdirectories of visited directories
    -a, --all                     All above options simultaneously (equivalent to '-ftr')
    --filename=FILENAME           Filename searched by '--search-filename'. Default value is '__jinja__.py'
    --tag=TAG                     Tag searched by '--search-tag'. Default value is 'autojinja'
                                  Python scripts' first line must contain this tag (ex: '### autojinja ###')
    -e, --env=NAME=VALUE/FILE     Additional environment variable or .env file
    -i, --includes=DIRECTORIES    Additional import directories for executed python scripts
                                  Directory list separated by ':' (Unix only) or ';' (Windows and Unix)
                                  Appended to environment variable 'PYTHONPATH'
    --remove-markers=ENABLE       Removes markers from generated outputs
                                  Default value is '0' or environment variable 'AUTOJINJA_REMOVE_MARKERS'
                                  Overrides environment variable 'AUTOJINJA_REMOVE_MARKERS'
    --silent                      Prevents executed python scripts from writing to stdout/stderr
                                  Enabled if environment variable 'AUTOJINJA_SILENT' == 1
                                  Overrides environment variable 'AUTOJINJA_SILENT'
    --debug                       Enhances stacktraces for exceptions raised from Jinja context variables
                                  Enabled if environment variable 'AUTOJINJA_DEBUG' == 1
                                  Overrides environment variable 'AUTOJINJA_DEBUG'
    --summary=VALUE/FLAGS         Enables notifications for generated files to stdout
                                  Overrides environment variable 'AUTOJINJA_SUMMARY'
                                  Default value is '1':
                                      0: nothing
                                      1: [autojinja]  -------  <abs_path>  (from <abs_path>)
                                  Also accepts 3 flags instead:
                                      100
                                      ^------ show (1) / hide (0) executing script path
                                              0: [autojinja]  -------  <path>
                                              1: [autojinja]  -------  <path>  (from <path>)
                                      010
                                       ^------ use absolute (1) / relative (0) paths
                                              0: [autojinja]  -------  <rel_path>  (from <rel_path>)
                                              1: [autojinja]  -------  <abs_path>  (from <abs_path>)
                                      001
                                        ^------ notification when changed only (1)
                                              0: [autojinja]  -------  <path>  (from <path>)
                                              1: [autojinja]  changed  <path>  (from <path>)
```

The first step of **autojinja** _CLI_ is to resolve an exhaustive list of all the Python scripts to execute, based on scripts, directories and options provided as arguments. These scripts are then successively executed by launching Python processes, as you would manually do with the command :

```shell
$ python script1.py && python script2.py && ...
```

Each script is executed with no arguments and with its _current working directory_ set to the directory containing the script, allowing local file access of neighboring files within the scripts, regardless of where the command has been launched.

Console streams (namely _stdin_, _stdout_ and _stderr_) are properly redirected unless the `--silent` option is enabled. In this case, _stdout_ and _stderr_ are not forwarded and script execution remain silent. However if a script fails, its output is still written to console for debugging purposes.

The whole process succeeds when all scripts have been successfully executed.

## Environment variables

Additional environment variables can be provided to Python scripts by using the `-e`, `--env` option. It can be repeatedly used to either directly provide environment variables or to load files containing environment variable definitions :

```shell
$ autojinja --env VAR1=42 --env file.env ...
```

Environments files are composed of one definition per line :

```bash
# file.env
VAR2=/tmp/dir1
VAR3=${THIS_DIRPATH}/input.txt
VAR4=${VAR2}/${VAR3}
```

The special environment variable `THIS_DIRPATH` can be used to refer to the environment file location, which allows to construct absolute paths that can be directly used inside the Python scripts.

# Advanced Jinja2 features

Jinja2 templating engine provides advanced mechanisms, such as template inheritance and filters, that require the use of the underlying `jinja2.Environment` which instantiates the `jinja2.Template` wrapped inside [`RawTemplate`](#class-autojinjarawtemplate) objects.

By default, such environment is automatically created on the fly the first time a `RawTemplate` is created, and is then reused for all future `RawTemplate` objects in the concerned script. This environment can be retrieved and modified by using the `environment` static member of the `RawTemplate` class :

```python
from autojinja import RawTemplate

env = RawTemplate.environment
print(env == None) # True, not created yet

template = RawTemplate.from_string("My name is {{ firstname }} {{ lastname }} !")

env = RawTemplate.environment
print(env != None) # True, the environment has been created
```

Template inheritance, for instance, requires that you create this environment yourself, with the proper arguments provided in its constructor. To achieve this, you can call the `create_environment` static methods of the `RawTemplate` class which will create and return a new `jinja2.Environment` with the provided arguments, as well as the default arguments that **autojinja** normally uses, if not overriden :

```python
from autojinja import RawTemplate
from jinja import FileSystemLoader

loader = FileSystemLoader('template_dir/') # Allows template inheritance
env = RawTemplate.create_environment(loader = loader)
RawTemplate.environment = env # Set the environment

template = RawTemplate.from_string("{% extends 'template.html' %}...")
...
```

- ### _RawTemplate_.**create_environment**(_&ast;args, &ast;&ast;kwargs_):

    Constructs a `jinja2.Environment` object with the provided arguments. If not specified, these arguments are also used :
    - `loader = autojinja.AutoLoader`
    - `keep_trailing_newline = True`
    - `lstrip_blocks = True`
    - `trim_blocks = True`
    - `undefined = jinja2.StrictUndefined`

    Parameters :
    - **&ast;args**, **&ast;&ast;kwargs** : arguments used to construct the object, see `jinja2.Environment` documentation

    Return type :
    - `jinja2.Environment`
