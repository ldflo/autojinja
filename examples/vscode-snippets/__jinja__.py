from autojinja import *
from collections import defaultdict
from typing import List

### Find recursively all files in 'snippets/' directory and group by extension
snippet_dict = defaultdict(list)
for snippet_file in Path("snippets/").files("**"):
    snippet_dict[snippet_file.ext].append(snippet_file)

### Prepare a template for creating each VSCode snippet file
file_template = JinjaTemplate.from_string("""
{
    // <<[ additional_snippets ]>>
    //// Insert snippets here ////
    // <<[ end ]>>

    // Generated snippets
    {% for snippet_file in snippet_files %}
    "{{ snippet_id(snippet_file) }}": {
        "prefix": ["{{ snippet_name(snippet_file) }}"],
        "body": ["{{ '",\n                 "'.join(snippet_lines(snippet_file)) }}"],
    },
    {% endfor %}
}
""".lstrip())

# Prepare some helpers for above template
def snippet_id(snippet_file: path.Path) -> str:
    return snippet_file.filename
def snippet_name(snippet_file: path.Path) -> str:
    return snippet_file.filename.no_ext
def snippet_lines(snippet_file: path.Path) -> List[str]:
    with open(snippet_file) as file:
        return file.read().replace('\\', '\\\\').replace('\t', '\\t').splitlines()

for extension in snippet_dict.keys():
    # Resolve destination file based on file extension
    filepath = f".vscode/{extension[1:]}.code-snippets"
    snippet_files = snippet_dict[extension]
    # Generate the above template.
    # The template has direct access to the current Python scope
    file_template.context(**locals()).render_file(filepath)
