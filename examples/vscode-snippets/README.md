# VSCode snippets example

This example generates [Visual Studio Code snippets](https://code.visualstudio.com/docs/editor/userdefinedsnippets), starting from all the files located in the `snippets/` directory.

Each file `snippets/<name>.<extension>` with content...

```
line1
line2
line3
```

...will be generated in `.vscode/<extension>.code-snippets` as such :

```json5
"<name>.<extension>": {
    "prefix": ["<name>"],
    "body": ["line1",
             "line2",
             "line3"],
},
```

Hand-made VSCode snippets can also be maintained inside the generated files thanks to the `additional_snippets` section :

```json5
{
    // <<[ additional_snippets ]>>
    //// Insert snippets here ////
    // <<[ end ]>>

    // Generated snippets
    "<name>.<extension>": {
        "prefix": ["<name>"],
        "body": ["line1",
                 "line2",
                 "line3"],
    },
    ...
}
```

# How to execute

The whole generation process takes place in the `__jinja__.py` script, which can be manually executed or automatically discovered with the commands :

```shell
$ autojinja __jinja__.py
```
```shell
$ autojinja -a .
```
