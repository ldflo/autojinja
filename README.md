# autojinja

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

## Usage

```shell
$ autojinja script1.py script2.py
```
```shell
$ autojinja -a .
```

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

## Integration in build pipelines

**autojinja** generation mechanism can be integrated as a build step by listing all Python3 scripts that perform generation :

```shell
$ autojinja script1.py dir/script2.py ...
```

**autojinja** also provides discover mechanisms to find and execute the concerned Python3 scripts in listed directories :

- `-r -f` recursively executes all Python3 scripts named `__jinja__.py`

    ```shell
    $ autojinja -r -f .
    ```

- `-r -t` recursively executes all Python3 scripts whose first line contains `autojinja` keyword (can be for instance `import autojinja` or `from autojinja import *`)

    ```shell
    $ autojinja -r -t .
    ```

- `-a` equivalent to `-r -f -t`

    ```shell
    $ autojinja -a .
    ```

Centralized metadata files (such as XML or JSON files) can easily be accessed inside Python3 scripts using environment variables and environment files :

```shell
$ autojinja -a . -e FILE1=/tmp/file1.xml -e file.env
```

## Links
- [Documentation](https://github.com/ldflo/autojinja/blob/main/docs/doc_autojinja.md)
- [Examples](https://github.com/ldflo/autojinja/blob/main/examples)
- [Jinja2](https://github.com/pallets/jinja)
- [Cog](https://github.com/nedbat/cog)
