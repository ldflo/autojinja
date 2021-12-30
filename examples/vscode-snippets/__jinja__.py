from autojinja import *
from collections import defaultdict

### Prepare a template for creating VSCode snippet files
file_template = JinjaTemplate.from_string("""
{
    // <<[ additional_snippets ]>>
    //// Insert snippets here ////
    // <<[ end ]>>

    // Generated snippets
    {% for snippet in snippets %}
    "{{ snippet.id }}": {
        "prefix": ["{{ snippet.name }}"],
        "body": ["{{ '",\n                 "'.join(snippet.lines) }}"],
    },
    {% endfor %}
}
""".lstrip())

# Prepare a context generator for above template
def generator_snippets(snippet_files):
    for snippet_file in snippet_files:
        with open(snippet_file) as file:
            class Snippet:
                id = snippet_file.filename
                name = snippet_file.filename.no_ext
                lines = file.read().replace('\\', '\\\\').replace('\t', '\\t').splitlines()
            yield Snippet

# Find recursively all files in 'snippets/' directory
snippets_files = path("snippets/").files("**")

# Group by file extension
snippet_dict = defaultdict(list)
for snippet_file in snippets_files:
    snippet_dict[snippet_file.ext].append(snippet_file)

for extension in snippet_dict.keys():
    # Resolve destination file based on file extension
    filepath = f".vscode/{extension[1:]}.code-snippets"
    ### Generate the destination snippet file
    file_template.context(snippets = generator_snippets(snippet_dict[extension])).render_file(filepath)
