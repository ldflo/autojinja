from . import assert_exception, assert_clean_exception, Class1, Class2, Class3, DiffException

import autojinja
import jinja2
import os
import sys
import tempfile
from typing import Dict, Optional, Tuple, Type, Union

settingsRemoveMarkers = autojinja.ParserSettings(remove_markers = True)
settingsPreserveMarkers = autojinja.ParserSettings(remove_markers = False)

tmp = tempfile.TemporaryDirectory()
root = autojinja.path.DirPath(tmp.name)
input_file = root.join("input.txt")
output_file = root.join("output.txt")

def invalid_autojinja(input: str, exception_type: type, message: str, *args: str, **kwargs: str):
    def function(*args: str, **kwargs: str):
        template = autojinja.JinjaTemplate.from_string(input)
        template.context(*args, **kwargs).render()
    assert_clean_exception(function, exception_type, message, *args, **kwargs)

### RawTemplate

class Generator_RawTemplate:
    def render(template: autojinja.templates.BaseTemplate, expected: str, args: Tuple[str, ...], kwargs: Dict[str, str]):
        result = template.context(*args, **kwargs).render()
        if result != expected:
            raise DiffException(result, expected)

    def render_file(template: autojinja.templates.BaseTemplate, expected: str, output: Optional[str], encoding: Optional[str], newline: Optional[str], args: Tuple[str, ...], kwargs: Dict[str, str]):
        result = template.context(*args, **kwargs).render_file(output, encoding, newline)
        if result != expected:
            raise DiffException(result, expected)
        encoding = encoding or template.encoding
        newline = newline or template.newline
        with open(output_file, 'r', encoding = encoding, newline = newline) as f:
            content = f.read()
            if os.name == "nt": # Windows
                result = result.replace('\n', newline or '\n')
            if content != result:
                raise DiffException(content, result)

    def check(input: str, expected: str, *args: str, **kwargs: str):
        with open(input_file, 'w') as f:
            f.write(input)
        ### Output
        template = autojinja.RawTemplate.from_file(input_file, output_file, None, None, None)
        Generator_RawTemplate.render(template, expected, args, kwargs)
        template = autojinja.RawTemplate.from_string(input, None, None, None, None)
        Generator_RawTemplate.render_file(template, expected, output_file, None, None, args, kwargs)
        ### Encoding / Newline
        template = autojinja.RawTemplate.from_file(input_file, output_file, "ascii", "\r\n", None)
        Generator_RawTemplate.render(template, expected, args, kwargs)
        template = autojinja.RawTemplate.from_string(input, output_file, None, None, None)
        Generator_RawTemplate.render_file(template, expected, None, "ascii", "\r\n", args, kwargs)
        ### Globals
        template = autojinja.RawTemplate.from_file(input_file, output_file, None, None, kwargs)
        Generator_RawTemplate.render(template, expected, (), {})
        template = autojinja.RawTemplate.from_string(input, output_file, None, None, None)
        Generator_RawTemplate.render_file(template, expected, None, None, None, args, kwargs)

### CogTemplate / JinjaTemplate

class Generator:
    def render(template: autojinja.templates.BaseTemplate, output: Optional[str], expected: str, remove_markers: Optional[bool], args: Tuple[str, ...], kwargs: Dict[str, str]):
        result = template.context(*args, **kwargs).render(output, remove_markers)
        if result != expected:
            raise DiffException(result, expected)

    def render_file(template: autojinja.templates.BaseTemplate, output: str, expected, remove_markers: Optional[bool], encoding: Optional[str], newline: Optional[str], args: Tuple[str, ...], kwargs: Dict[str, str]):
        result = template.context(*args, **kwargs).render_file(output, remove_markers, encoding, newline)
        if result != expected:
            raise DiffException(result, expected)
        encoding = encoding or template.encoding
        newline = newline or template.newline
        with open(output_file, 'r', encoding = encoding, newline = newline) as f:
            content = f.read()
            result = result.replace('\n', newline or '\n')
            if content != result:
                raise DiffException(content, result)

    def check(class_type: Union[Type[autojinja.CogTemplate], Type[autojinja.JinjaTemplate]], input: str, output: Optional[str], expected: str, remove_markers: Optional[bool], *args: str, **kwargs: str):
        def prepare():
            if output_file.exists:
                os.remove(output_file)
            if output != None:
                with open(output_file, 'w') as f:
                    f.write(output)
        with open(input_file, 'w') as f:
            f.write(input)
        ### Output
        template = class_type.from_file(input_file, None, None, remove_markers, None, None, None)
        prepare(); Generator.render(template, output, expected, None, args, kwargs)
        template = class_type.from_string(input, None, None, remove_markers, None, None, None)
        prepare(); Generator.render_file(template, output_file, expected, None, None, None, args, kwargs)
        ### Settings
        template = class_type.from_file(input_file, None, autojinja.ParserSettings(), remove_markers, None, None, None)
        prepare(); Generator.render(template, output, expected, None, args, kwargs)
        template = class_type.from_string(input, output_file, autojinja.ParserSettings(), remove_markers, None, None, None)
        prepare(); Generator.render_file(template, None, expected, None, None, None, args, kwargs)
        ### Remove markers
        template = class_type.from_file(input_file, None, None, not remove_markers if remove_markers else None, None, None, None)
        prepare(); Generator.render(template, output, expected, remove_markers, args, kwargs)
        template = class_type.from_string(input, output_file, None, None, None, None, None)
        prepare(); Generator.render_file(template, None, expected, remove_markers, None, None, args, kwargs)
        ### Encoding / Newline
        template = class_type.from_file(input_file, None, None, remove_markers, "ascii", "\r\n", None)
        prepare(); Generator.render(template, output, expected, None, args, kwargs)
        template = class_type.from_string(input, output_file, None, remove_markers, None, None, None)
        prepare(); Generator.render_file(template, None, expected, None, "ascii", "\r\n", args, kwargs)
        ### Globals
        template = class_type.from_file(input_file, None, None, remove_markers, None, None, kwargs)
        prepare(); Generator.render(template, output, expected, None, (), {})
        template = class_type.from_string(input, output_file, None, remove_markers, None, None, None)
        prepare(); Generator.render_file(template, None, expected, None, None, None, args, kwargs)

class Test_RawTemplate:
    def test_1(self):
        input    = "  std::cout << {{ var }} << std::endl;  "
        expected = "  std::cout << \"Hello world\" << std::endl;  "
        Generator_RawTemplate.check(input, expected, var = "\"Hello world\"")

    def test_2(self):
        input    = "  {% for var in list %}\n" \
                   "    result : {{ var }}\n" \
                   "  {% endfor %}"
        expected = "    result : var1\n" \
                   "    result : var2\n"
        Generator_RawTemplate.check(input, expected, list = ["var1", "var2"])

    def test_3(self):
        input    = "  // [[[ {{ var }} ]]]\n" \
                   "  // [[[ end ]]]"
        expected = "  // [[[ \"Hello world\" ]]]\n" \
                   "  // [[[ end ]]]"
        Generator_RawTemplate.check(input, expected, var = "\"Hello world\"")

    def test_4(self):
        input    = "  // <<[ {{ var }} ]>>\n" \
                   "  // <<[ end ]>>"
        expected = "  // <<[ \"Hello world\" ]>>\n" \
                   "  // <<[ end ]>>"
        Generator_RawTemplate.check(input, expected, var = "\"Hello world\"")

    def test_5(self):
        input    = "  // [[[ {{ var }} ]]]\n" \
                   "  // [[[ end ]]]\n" \
                   "var\n" \
                   "  // <<[ {{ var }} ]>>\n" \
                   "  // <<[ end ]>>"
        expected = "  // [[[ \"Hello world\" ]]]\n" \
                   "  // [[[ end ]]]\n" \
                   "var\n" \
                   "  // <<[ \"Hello world\" ]>>\n" \
                   "  // <<[ end ]>>"
        Generator_RawTemplate.check(input, expected, var = "\"Hello world\"")

    def test_6(self):
        input    = "  [[[\n" \
                   "    <<[ {{ var }} ]>>\n" \
                   "    <<[ end ]>>\n" \
                   "  ]]]\n" \
                   "  [[[ end ]]]"
        expected = "  [[[\n" \
                   "    <<[ \"Hello world\" ]>>\n" \
                   "    <<[ end ]>>\n" \
                   "  ]]]\n" \
                   "  [[[ end ]]]"
        Generator_RawTemplate.check(input, expected, var = "\"Hello world\"")

    def test_7(self):
        input    = "  // [[[\n" \
                   "     {% for var in list %}\n" \
                   "     result : {{ var }}\n" \
                   "     {% endfor %}\n" \
                   "  // ]]]\n" \
                   "  // [[[ end ]]]"
        expected = "  // [[[\n" \
                   "     result : var1\n" \
                   "     result : var2\n" \
                   "  // ]]]\n" \
                   "  // [[[ end ]]]"
        Generator_RawTemplate.check(input, expected, list = ["var1", "var2"])

class Test_CogTemplate:
    def test_newfile(self):
        if output_file.exists:
            os.remove(output_file)
        with open(input_file, 'w') as f:
            f.write("test")
        template = autojinja.CogTemplate.from_file(input_file)
        output = template.render_file(output_file)
        assert output == "test"

    def test_1(self):
        input    = "  std::cout << {{ var }} << std::endl;  "
        expected = input
        Generator.check(autojinja.CogTemplate, input, None, expected, None, var = "\"Hello world\"")
    def test_1_output(self):
        input    = "  std::cout << {{ var }} << std::endl;  "
        expected = input
        output   = "Test"
        Generator.check(autojinja.CogTemplate, input, output, expected, None, var = "\"Hello world\"")
    def test_1_remove_markers(self):
        input    = "  std::cout << {{ var }} << std::endl;  "
        expected = input
        Generator.check(autojinja.CogTemplate, input, None, expected, True, var = "\"Hello world\"")

    def test_2(self):
        input    = "  {% for var in list %}\n" \
                   "    result : {{ var }}\n" \
                   "  {% endfor %}"
        expected = input
        Generator.check(autojinja.CogTemplate, input, None, expected, None, list = ["var1", "var2"])
    def test_2_output(self):
        input    = "  {% for var in list %}\n" \
                   "    result : {{ var }}\n" \
                   "  {% endfor %}"
        expected = input
        output   = "Test"
        Generator.check(autojinja.CogTemplate, input, output, expected, None, list = ["var1", "var2"])
    def test_2_remove_markers(self):
        input    = "  {% for var in list %}\n" \
                   "    result : {{ var }}\n" \
                   "  {% endfor %}"
        expected = input
        Generator.check(autojinja.CogTemplate, input, None, expected, True, list = ["var1", "var2"])

    def test_3(self):
        input    = "  // [[[ {{ var }} ]]]\n" \
                   "  // [[[ end ]]]"
        expected = "  // [[[ {{ var }} ]]]\n" \
                   "  \"Hello world\"\n" \
                   "  // [[[ end ]]]"
        Generator.check(autojinja.CogTemplate, input, None, expected, None, var = "\"Hello world\"")
    def test_3_output(self):
        input    = "  // [[[ {{ var }} ]]]\n" \
                   "  // [[[ end ]]]"
        expected = "  // [[[ {{ var }} ]]]\n" \
                   "  \"Hello world\"\n" \
                   "  // [[[ end ]]]"
        output   = "Test"
        Generator.check(autojinja.CogTemplate, input, output, expected, None, var = "\"Hello world\"")
    def test_3_remove_markers(self):
        input    = "  // [[[ {{ var }} ]]]\n" \
                   "  // [[[ end ]]]"
        expected = "  \"Hello world\"\n"
        Generator.check(autojinja.CogTemplate, input, None, expected, True, var = "\"Hello world\"")

    def test_4(self):
        input    = "  // <<[ {{ var }} ]>>\n" \
                   "  // <<[ end ]>>"
        expected = input
        Generator.check(autojinja.CogTemplate, input, None, expected, None, var = "\"Hello world\"")
    def test_4_output(self):
        input    = "  // <<[ {{ var }} ]>>\n" \
                   "  // <<[ end ]>>"
        expected = "  // <<[ {{ var }} ]>>\n" \
                   "    Test\n" \
                   "  // <<[ end ]>>"
        output   = "<<[ {{ var }} ]>>\n" \
                   "  Test\n" \
                   "<<[ end ]>>"
        Generator.check(autojinja.CogTemplate, input, output, expected, None, var = "\"Hello world\"")
    def test_4_remove_markers(self):
        input    = "  // <<[ {{ var }} ]>>\n" \
                   "  // <<[ end ]>>"
        expected = ""
        Generator.check(autojinja.CogTemplate, input, None, expected, True, var = "\"Hello world\"")

    def test_5(self):
        input    = "  // [[[ {{ var }} ]]]\n" \
                   "  // [[[ end ]]]\n" \
                   "var\n" \
                   "  // <<[ {{ var }} ]>>\n" \
                   "  // <<[ end ]>>"
        expected = "  // [[[ {{ var }} ]]]\n" \
                   "  \"Hello world\"\n" \
                   "  // [[[ end ]]]\n" \
                   "var\n" \
                   "  // <<[ {{ var }} ]>>\n" \
                   "  // <<[ end ]>>"
        Generator.check(autojinja.CogTemplate, input, None, expected, None, var = "\"Hello world\"")
    def test_5_output(self):
        input    = "  // [[[ {{ var }} ]]]\n" \
                   "  // [[[ end ]]]\n" \
                   "var\n" \
                   "  // <<[ {{ var }} ]>>\n" \
                   "  // <<[ end ]>>"
        expected = "  // [[[ {{ var }} ]]]\n" \
                   "  \"Hello world\"\n" \
                   "  // [[[ end ]]]\n" \
                   "var\n" \
                   "  // <<[ {{ var }} ]>>\n" \
                   "    Test\n" \
                   "  // <<[ end ]>>"
        output   = "<<[ {{ var }} ]>>\n" \
                   "  Test\n" \
                   "<<[ end ]>>"
        Generator.check(autojinja.CogTemplate, input, output, expected, None, var = "\"Hello world\"")
    def test_5_remove_markers(self):
        input    = "  // [[[ {{ var }} ]]]\n" \
                   "  // [[[ end ]]]\n" \
                   "var\n" \
                   "  // <<[ {{ var }} ]>>\n" \
                   "  // <<[ end ]>>"
        expected = "  \"Hello world\"\n" \
                   "var\n"
        Generator.check(autojinja.CogTemplate, input, None, expected, True, var = "\"Hello world\"")

    def test_6(self):
        input    = "  [[[\n" \
                   "    <<[ {{ var }} ]>>\n" \
                   "    <<[ end ]>>\n" \
                   "  ]]]\n" \
                   "  [[[ end ]]]\n" \
                   "  {{ tmp }}"
        expected = "  [[[\n" \
                   "    <<[ {{ var }} ]>>\n" \
                   "    <<[ end ]>>\n" \
                   "  ]]]\n" \
                   "    <<[ \"Hello world\" ]>>\n" \
                   "    <<[ end ]>>\n" \
                   "  [[[ end ]]]\n" \
                   "  {{ tmp }}"
        Generator.check(autojinja.CogTemplate, input, None, expected, None, var = "\"Hello world\"", tmp = "test")
    def test_6_output(self):
        input    = "  [[[\n" \
                   "    <<[ {{ var }} ]>>\n" \
                   "    <<[ end ]>>\n" \
                   "  ]]]\n" \
                   "  [[[ end ]]]\n" \
                   "  {{ tmp }}"
        expected = "  [[[\n" \
                   "    <<[ {{ var }} ]>>\n" \
                   "    <<[ end ]>>\n" \
                   "  ]]]\n" \
                   "    <<[ \"Hello world\" ]>>\n" \
                   "    Test\n" \
                   "    <<[ end ]>>\n" \
                   "  [[[ end ]]]\n" \
                   "  {{ tmp }}"
        output   = "<<[ \"Hello world\" ]>> Test <<[ end ]>>"
        Generator.check(autojinja.CogTemplate, input, output, expected, None, var = "\"Hello world\"", tmp = "test")
    def test_6_remove_markers(self):
        input    = "  [[[\n" \
                   "    <<[ {{ var }} ]>>\n" \
                   "    <<[ end ]>>\n" \
                   "  ]]]\n" \
                   "  [[[ end ]]]\n" \
                   "  {{ tmp }}"
        expected = "    Test\n" \
                   "  {{ tmp }}"
        output   = "<<[ \"Hello world\" ]>> Test <<[ end ]>>"
        Generator.check(autojinja.CogTemplate, input, output, expected, True, var = "\"Hello world\"", tmp = "test")

    def test_7(self):
        input    = "  {{ tmp }}\n" \
                   "  // [[[\n" \
                   "     {% for var in list %}\n" \
                   "     result : {{ var }}\n" \
                   "     {% endfor %}\n" \
                   "  // ]]]\n" \
                   "  // [[[ end ]]]"
        expected = "  {{ tmp }}\n" \
                   "  // [[[\n" \
                   "     {% for var in list %}\n" \
                   "     result : {{ var }}\n" \
                   "     {% endfor %}\n" \
                   "  // ]]]\n" \
                   "  result : var1\n" \
                   "  result : var2\n" \
                   "  // [[[ end ]]]"
        Generator.check(autojinja.CogTemplate, input, None, expected, None, list = ["var1", "var2"], tmp = "test")
    def test_7_output(self):
        input    = "  {{ tmp }}\n" \
                   "  // [[[\n" \
                   "     {% for var in list %}\n" \
                   "     result : {{ var }}\n" \
                   "     {% endfor %}\n" \
                   "  // ]]]\n" \
                   "  // [[[ end ]]]"
        expected = "  {{ tmp }}\n" \
                   "  // [[[\n" \
                   "     {% for var in list %}\n" \
                   "     result : {{ var }}\n" \
                   "     {% endfor %}\n" \
                   "  // ]]]\n" \
                   "  result : var1\n" \
                   "  result : var2\n" \
                   "  // [[[ end ]]]"
        output   = "Test"
        Generator.check(autojinja.CogTemplate, input, output, expected, None, list = ["var1", "var2"], tmp = "test")
    def test_7_remove_markers(self):
        input    = "  {{ tmp }}\n" \
                   "  // [[[\n" \
                   "     {% for var in list %}\n" \
                   "     result : {{ var }}\n" \
                   "     {% endfor %}\n" \
                   "  // ]]]\n" \
                   "  // [[[ end ]]]"
        expected = "  {{ tmp }}\n" \
                   "  result : var1\n" \
                   "  result : var2\n"
        Generator.check(autojinja.CogTemplate, input, None, expected, True, list = ["var1", "var2"], tmp = "test")

    def test_8(self):
        input    = "[[[\n" \
                   "  <<[ a ]>>\n" \
                   "  <<[ end ]>>\n" \
                   "]]]\n" \
                   "[[[ end ]]]"
        expected = "[[[\n" \
                   "  <<[ a ]>>\n" \
                   "  <<[ end ]>>\n" \
                   "]]]\n" \
                   "  <<[ a ]>>\n" \
                   "  <<[ end ]>>\n" \
                   "[[[ end ]]]"
        Generator.check(autojinja.CogTemplate, input, None, expected, None, var = "\"Hello world\"")
    def test_8_output(self):
        input    = "[[[\n" \
                   "  <<[ a ]>>\n" \
                   "  <<[ end ]>>\n" \
                   "]]]\n" \
                   "[[[ end ]]]"
        expected = "[[[\n" \
                   "  <<[ a ]>>\n" \
                   "  <<[ end ]>>\n" \
                   "]]]\n" \
                   "  <<[ a ]>>\n" \
                   "    [[[ {{ var }} ]]]\n" \
                   "    \"Hello world\"\n" \
                   "    [[[ end ]]]\n" \
                   "  <<[ end ]>>\n" \
                   "[[[ end ]]]"
        output   = "[[[  ]]]\n" \
                   "  <<[ a ]>>\n" \
                   "    [[[ {{ var }} ]]]\n" \
                   "    [[[ end ]]]\n" \
                   "  <<[ end ]>>\n" \
                   "[[[ end ]]]"
        Generator.check(autojinja.CogTemplate, input, output, expected, None, var = "\"Hello world\"")
    def test_8_remove_markers(self):
        input    = "[[[\n" \
                   "  <<[ a ]>>\n" \
                   "  <<[ end ]>>\n" \
                   "]]]\n" \
                   "[[[ end ]]]"
        expected = "    \"Hello world\"\n"
        output   = "[[[  ]]]\n" \
                   "  <<[ a ]>>\n" \
                   "    [[[ {{ var }} ]]]\n" \
                   "    [[[ end ]]]\n" \
                   "  <<[ end ]>>\n" \
                   "[[[ end ]]]"
        Generator.check(autojinja.CogTemplate, input, output, expected, True, var = "\"Hello world\"")

    def test_9(self):
        input    = "  [[[\n" \
                   "    <<[ {{ var }} ]>>\n" \
                   "    <<[ end ]>>\n" \
                   "  ]]]\n" \
                   "  [[[ end ]]]\n" \
                   "  {{ tmp }}"
        expected = "  [[[\n" \
                   "    <<[ {{ var }} ]>>\n" \
                   "    <<[ end ]>>\n" \
                   "  ]]]\n" \
                   "    <<[ \"Hello world\" ]>>\n" \
                   "    azerty\n" \
                   "    <<[ end ]>>\n" \
                   "  [[[ end ]]]\n" \
                   "  {{ tmp }}"
        template = autojinja.CogTemplate.from_string(input)
        template.edits = { "\"Hello world\"":"azerty" }
        result = template.context(var = "\"Hello world\"", tmp = "test").render()
        if result != expected:
            raise DiffException(result, expected)
        assert len(template.blocks) == 1
        assert len(template.cog_blocks) == 1
        assert len(template.edit_blocks) == 0

    def test_10(self):
        input    = "  [[[\n" \
                   "    <<[ {{ var }} ]>>\n" \
                   "    <<[ end ]>>\n" \
                   "  ]]]\n" \
                   "  [[[ end ]]]\n" \
                   "  {{ tmp }}"
        expected = "  [[[\n" \
                   "    <<[ {{ var }} ]>>\n" \
                   "    <<[ end ]>>\n" \
                   "  ]]]\n" \
                   "    <<[ \"Hello world\" ]>>\n" \
                   "    azerty\n" \
                   "    <<[ end ]>>\n" \
                   "  [[[ end ]]]\n" \
                   "  {{ tmp }}"
        output   = "<<[ \"Hello world\" ]>> Test <<[ end ]>>"
        template = autojinja.CogTemplate.from_string(input)
        template.edits = { "\"Hello world\"":"azerty" }
        result = template.context(var = "\"Hello world\"", tmp = "test").render(output)
        if result != expected:
            raise DiffException(result, expected)
        assert len(template.blocks) == 1
        assert len(template.cog_blocks) == 1
        assert len(template.edit_blocks) == 0

    def test_11(self):
        input    = "  // [[[ {{ var }} ]]]\n" \
                   "  // [[[ end ]]]"
        expected = "  // [[[ {{ var }} ]]]\n" \
                   "  \"Hello world\"\n" \
                   "  // [[[ end ]]]"
        with open(input_file, 'w') as f:
            f.write(input)
        template = autojinja.CogTemplate.from_file(input_file)
        result = template.context(var = "\"Hello world\"").render_file()
        if result != expected:
            raise DiffException(result, expected)
        with open(input_file, 'r') as f:
            content = f.read()
            if content != result:
                raise DiffException(content, result)

    def test_12(self):
        input    = "<<[ abc ]>>\n" \
                   "test1\n" \
                   "<<[ end ]>>\n" \
                   "<<[ def ]>>\n" \
                   "test2\n" \
                   "<<[ end ]>>"
        expected = "<<[ abc ]>>\n" \
                   "dummy\n" \
                   "<<[ end ]>>\n" \
                   "<<[ def ]>>\n" \
                   "test2\n" \
                   "<<[ end ]>>"
        output   = "<<[ abc ]>> dummy <<[ end ]>>"
        template = autojinja.CogTemplate.from_string(input)
        dummy = template.edits
        result = template.context().render(output)
        if result != expected:
            raise DiffException(result, expected)
        assert len(template.blocks) == 2
        assert len(template.cog_blocks) == 0
        assert len(template.edit_blocks) == 2

class Test_JinjaTemplate:
    def test_newfile(self):
        if output_file.exists:
            os.remove(output_file)
        with open(input_file, 'w') as f:
            f.write("test")
        template = autojinja.JinjaTemplate.from_file(input_file)
        output = template.render_file(output_file)
        assert output == "test"

    def test_1(self):
        input    = "  std::cout << {{ var }} << std::endl;  "
        expected = "  std::cout << \"Hello world\" << std::endl;  "
        Generator.check(autojinja.JinjaTemplate, input, None, expected, None, var = "\"Hello world\"")
    def test_1_output(self):
        input    = "  std::cout << {{ var }} << std::endl;  "
        expected = "  std::cout << \"Hello world\" << std::endl;  "
        output   = "Test"
        Generator.check(autojinja.JinjaTemplate, input, output, expected, None, var = "\"Hello world\"")
    def test_1_remove_markers(self):
        input    = "  std::cout << {{ var }} << std::endl;  "
        expected = "  std::cout << \"Hello world\" << std::endl;  "
        Generator.check(autojinja.JinjaTemplate, input, None, expected, True, var = "\"Hello world\"")

    def test_2(self):
        input    = "  {% for var in list %}\n" \
                   "    result : {{ var }}\n" \
                   "  {% endfor %}"
        expected = "    result : var1\n" \
                   "    result : var2\n"
        Generator.check(autojinja.JinjaTemplate, input, None, expected, None, list = ["var1", "var2"])
    def test_2_output(self):
        input    = "  {% for var in list %}\n" \
                   "    result : {{ var }}\n" \
                   "  {% endfor %}"
        expected = "    result : var1\n" \
                   "    result : var2\n"
        output   = "Test"
        Generator.check(autojinja.JinjaTemplate, input, output, expected, None, list = ["var1", "var2"])
    def test_2_remove_markers(self):
        input    = "  {% for var in list %}\n" \
                   "    result : {{ var }}\n" \
                   "  {% endfor %}"
        expected = "    result : var1\n" \
                   "    result : var2\n"
        Generator.check(autojinja.JinjaTemplate, input, None, expected, True, list = ["var1", "var2"])

    def test_3(self):
        input    = "  // [[[ {{ var }} ]]]\n" \
                   "  // [[[ end ]]]"
        expected = "  // [[[ {{ var }} ]]]\n" \
                   "  \"Hello world\"\n" \
                   "  // [[[ end ]]]"
        Generator.check(autojinja.JinjaTemplate, input, None, expected, None, var = "\"Hello world\"")
    def test_3_output(self):
        input    = "  // [[[ {{ var }} ]]]\n" \
                   "  // [[[ end ]]]"
        expected = "  // [[[ {{ var }} ]]]\n" \
                   "  \"Hello world\"\n" \
                   "  // [[[ end ]]]"
        output   = "Test"
        Generator.check(autojinja.JinjaTemplate, input, output, expected, None, var = "\"Hello world\"")
    def test_3_remove_markers(self):
        input    = "  // [[[ {{ var }} ]]]\n" \
                   "  // [[[ end ]]]"
        expected = "  \"Hello world\"\n"
        Generator.check(autojinja.JinjaTemplate, input, None, expected, True, var = "\"Hello world\"")

    def test_4(self):
        input    = "  // <<[ {{ var }} ]>>\n" \
                   "  // <<[ end ]>>"
        expected = "  // <<[ \"Hello world\" ]>>\n" \
                   "  // <<[ end ]>>"
        Generator.check(autojinja.JinjaTemplate, input, None, expected, None, var = "\"Hello world\"")
    def test_4_output(self):
        input    = "  // <<[ {{ var }} ]>>\n" \
                   "  // <<[ end ]>>"
        expected = "  // <<[ \"Hello world\" ]>>\n" \
                   "    Test\n" \
                   "  // <<[ end ]>>"
        output   = "<<[ \"Hello world\" ]>>\n" \
                   "  Test\n" \
                   "<<[ end ]>>"
        Generator.check(autojinja.JinjaTemplate, input, output, expected, None, var = "\"Hello world\"")
    def test_4_remove_markers(self):
        input    = "  // <<[ {{ var }} ]>>\n" \
                   "  // <<[ end ]>>"
        expected = ""
        Generator.check(autojinja.JinjaTemplate, input, None, expected, True, var = "\"Hello world\"")

    def test_5(self):
        input    = "  // [[[ {{ var }} ]]]\n" \
                   "  // [[[ end ]]]\n" \
                   "var\n" \
                   "  // <<[ \"Hello world\" ]>>\n" \
                   "  // <<[ end ]>>"
        expected = "  // [[[ {{ var }} ]]]\n" \
                   "  \"Hello world\"\n" \
                   "  // [[[ end ]]]\n" \
                   "var\n" \
                   "  // <<[ \"Hello world\" ]>>\n" \
                   "  // <<[ end ]>>"
        Generator.check(autojinja.JinjaTemplate, input, None, expected, None, var = "\"Hello world\"")
    def test_5_output(self):
        input    = "  // [[[ {{ var }} ]]]\n" \
                   "  // [[[ end ]]]\n" \
                   "var\n" \
                   "  // <<[ \"Hello world\" ]>>\n" \
                   "  // <<[ end ]>>"
        expected = "  // [[[ {{ var }} ]]]\n" \
                   "  \"Hello world\"\n" \
                   "  // [[[ end ]]]\n" \
                   "var\n" \
                   "  // <<[ \"Hello world\" ]>>\n" \
                   "    Test\n" \
                   "  // <<[ end ]>>"
        output   = "<<[ \"Hello world\" ]>>\n" \
                   "  Test\n" \
                   "<<[ end ]>>"
        Generator.check(autojinja.JinjaTemplate, input, output, expected, None, var = "\"Hello world\"")
    def test_5_remove_markers(self):
        input    = "  // [[[ {{ var }} ]]]\n" \
                   "  // [[[ end ]]]\n" \
                   "var\n" \
                   "  // <<[ {{ var }} ]>>\n" \
                   "  // <<[ end ]>>"
        expected = "  \"Hello world\"\n" \
                   "var\n"
        Generator.check(autojinja.JinjaTemplate, input, None, expected, True, var = "\"Hello world\"")

    def test_6(self):
        input    = "  [[[\n" \
                   "    <<[ {{ var }} ]>>\n" \
                   "    <<[ end ]>>\n" \
                   "  ]]]\n" \
                   "  [[[ end ]]]\n" \
                   "  {{ tmp }}"
        expected = "  [[[\n" \
                   "    <<[ {{ var }} ]>>\n" \
                   "    <<[ end ]>>\n" \
                   "  ]]]\n" \
                   "    <<[ \"Hello world\" ]>>\n" \
                   "    <<[ end ]>>\n" \
                   "  [[[ end ]]]\n" \
                   "  test"
        Generator.check(autojinja.JinjaTemplate, input, None, expected, None, var = "\"Hello world\"", tmp = "test")
    def test_6_output(self):
        input    = "  [[[\n" \
                   "    <<[ {{ var }} ]>>\n" \
                   "    <<[ end ]>>\n" \
                   "  ]]]\n" \
                   "  [[[ end ]]]\n" \
                   "  {{ tmp }}"
        expected = "  [[[\n" \
                   "    <<[ {{ var }} ]>>\n" \
                   "    <<[ end ]>>\n" \
                   "  ]]]\n" \
                   "    <<[ \"Hello world\" ]>>\n" \
                   "    Test\n" \
                   "    <<[ end ]>>\n" \
                   "  [[[ end ]]]\n" \
                   "  test"
        output   = "<<[ \"Hello world\" ]>> Test <<[ end ]>>"
        Generator.check(autojinja.JinjaTemplate, input, output, expected, None, var = "\"Hello world\"", tmp = "test")
    def test_6_remove_markers(self):
        input    = "  [[[\n" \
                   "    <<[ {{ var }} ]>>\n" \
                   "    <<[ end ]>>\n" \
                   "  ]]]\n" \
                   "  [[[ end ]]]\n" \
                   "  {{ tmp }}"
        expected = "    Test\n" \
                   "  test"
        output   = "<<[ \"Hello world\" ]>> Test <<[ end ]>>"
        Generator.check(autojinja.JinjaTemplate, input, output, expected, True, var = "\"Hello world\"", tmp = "test")

    def test_7(self):
        input    = "  {{ tmp }}\n" \
                   "  // [[[\n" \
                   "     {% for var in list %}\n" \
                   "     result : {{ var }}\n" \
                   "     {% endfor %}\n" \
                   "  // ]]]\n" \
                   "  // [[[ end ]]]"
        expected = "  test\n" \
                   "  // [[[\n" \
                   "     {% for var in list %}\n" \
                   "     result : {{ var }}\n" \
                   "     {% endfor %}\n" \
                   "  // ]]]\n" \
                   "  result : var1\n" \
                   "  result : var2\n" \
                   "  // [[[ end ]]]"
        Generator.check(autojinja.JinjaTemplate, input, None, expected, None, list = ["var1", "var2"], tmp = "test")
    def test_7_output(self):
        input    = "  {{ tmp }}\n" \
                   "  // [[[\n" \
                   "     {% for var in list %}\n" \
                   "     result : {{ var }}\n" \
                   "     {% endfor %}\n" \
                   "  // ]]]\n" \
                   "  // [[[ end ]]]"
        expected = "  test\n" \
                   "  // [[[\n" \
                   "     {% for var in list %}\n" \
                   "     result : {{ var }}\n" \
                   "     {% endfor %}\n" \
                   "  // ]]]\n" \
                   "  result : var1\n" \
                   "  result : var2\n" \
                   "  // [[[ end ]]]"
        output   = "Test"
        Generator.check(autojinja.JinjaTemplate, input, output, expected, None, list = ["var1", "var2"], tmp = "test")
    def test_7_remove_markers(self):
        input    = "  {{ tmp }}\n" \
                   "  // [[[\n" \
                   "     {% for var in list %}\n" \
                   "     result : {{ var }}\n" \
                   "     {% endfor %}\n" \
                   "  // ]]]\n" \
                   "  // [[[ end ]]]"
        expected = "  test\n" \
                   "  result : var1\n" \
                   "  result : var2\n"
        Generator.check(autojinja.JinjaTemplate, input, None, expected, True, list = ["var1", "var2"], tmp = "test")

    def test_8(self):
        input    = "[[[\n" \
                   "  <<[ a ]>>\n" \
                   "  <<[ end ]>>\n" \
                   "]]]\n" \
                   "[[[ end ]]]"
        expected = "[[[\n" \
                   "  <<[ a ]>>\n" \
                   "  <<[ end ]>>\n" \
                   "]]]\n" \
                   "  <<[ a ]>>\n" \
                   "  <<[ end ]>>\n" \
                   "[[[ end ]]]"
        Generator.check(autojinja.JinjaTemplate, input, None, expected, None, var = "\"Hello world\"")
    def test_8_output(self):
        input    = "[[[\n" \
                   "  <<[ a ]>>\n" \
                   "  <<[ end ]>>\n" \
                   "]]]\n" \
                   "[[[ end ]]]"
        expected = "[[[\n" \
                   "  <<[ a ]>>\n" \
                   "  <<[ end ]>>\n" \
                   "]]]\n" \
                   "  <<[ a ]>>\n" \
                   "    [[[ {{ var }} ]]]\n" \
                   "    \"Hello world\"\n" \
                   "    [[[ end ]]]\n" \
                   "  <<[ end ]>>\n" \
                   "[[[ end ]]]"
        output   = "[[[  ]]]\n" \
                   "  <<[ a ]>>\n" \
                   "    [[[ {{ var }} ]]]\n" \
                   "    [[[ end ]]]\n" \
                   "  <<[ end ]>>\n" \
                   "[[[ end ]]]"
        Generator.check(autojinja.JinjaTemplate, input, output, expected, None, var = "\"Hello world\"")
    def test_8_remove_markers(self):
        input    = "[[[\n" \
                   "  <<[ a ]>>\n" \
                   "  <<[ end ]>>\n" \
                   "]]]\n" \
                   "[[[ end ]]]"
        expected = "    \"Hello world\"\n"
        output   = "[[[  ]]]\n" \
                   "  <<[ a ]>>\n" \
                   "    [[[ {{ var }} ]]]\n" \
                   "    [[[ end ]]]\n" \
                   "  <<[ end ]>>\n" \
                   "[[[ end ]]]"
        Generator.check(autojinja.JinjaTemplate, input, output, expected, True, var = "\"Hello world\"")

    def test_9(self):
        input    = "  [[[\n" \
                   "    <<[ {{ var }} ]>>\n" \
                   "    <<[ end ]>>\n" \
                   "  ]]]\n" \
                   "  [[[ end ]]]\n" \
                   "  {{ tmp }}"
        expected = "  [[[\n" \
                   "    <<[ {{ var }} ]>>\n" \
                   "    <<[ end ]>>\n" \
                   "  ]]]\n" \
                   "    <<[ \"Hello world\" ]>>\n" \
                   "    azerty\n" \
                   "    <<[ end ]>>\n" \
                   "  [[[ end ]]]\n" \
                   "  test"
        template = autojinja.JinjaTemplate.from_string(input)
        template.edits = { "\"Hello world\"":"azerty" }
        result = template.context(var = "\"Hello world\"", tmp = "test").render()
        if result != expected:
            raise DiffException(result, expected)
        assert len(template.blocks) == 1
        assert len(template.cog_blocks) == 1
        assert len(template.edit_blocks) == 0

    def test_10(self):
        input    = "  [[[\n" \
                   "    <<[ {{ var }} ]>>\n" \
                   "    <<[ end ]>>\n" \
                   "  ]]]\n" \
                   "  [[[ end ]]]\n" \
                   "  {{ tmp }}"
        expected = "  [[[\n" \
                   "    <<[ {{ var }} ]>>\n" \
                   "    <<[ end ]>>\n" \
                   "  ]]]\n" \
                   "    <<[ \"Hello world\" ]>>\n" \
                   "    azerty\n" \
                   "    <<[ end ]>>\n" \
                   "  [[[ end ]]]\n" \
                   "  test"
        output   = "<<[ \"Hello world\" ]>> Test <<[ end ]>>"
        template = autojinja.JinjaTemplate.from_string(input)
        template.edits = { "\"Hello world\"":"azerty" }
        result = template.context(var = "\"Hello world\"", tmp = "test").render(output)
        if result != expected:
            raise DiffException(result, expected)
        assert len(template.blocks) == 1
        assert len(template.cog_blocks) == 1
        assert len(template.edit_blocks) == 0

    def test_11(self):
        input    = "  // [[[ {{ var }} ]]]\n" \
                   "  // [[[ end ]]]\n" \
                   "var\n" \
                   "  {{ var2 }}"
        expected = "  // [[[ {{ var }} ]]]\n" \
                   "  \"Hello world\"\n" \
                   "  // [[[ end ]]]\n" \
                   "var\n" \
                   "  [[[ test ]]] test [[[ end ]]]"
        Generator.check(autojinja.JinjaTemplate, input, None, expected, None, var = "\"Hello world\"", var2 = "[[[ test ]]][[[ end ]]]")
    def test_11_output(self):
        input    = "  // [[[ {{ var }} ]]]\n" \
                   "  // [[[ end ]]]\n" \
                   "var\n" \
                   "  {{ var2 }}"
        expected = "  // [[[ {{ var }} ]]]\n" \
                   "  \"Hello world\"\n" \
                   "  // [[[ end ]]]\n" \
                   "var\n" \
                   "  [[[ test ]]] test [[[ end ]]]"
        output   = "Test"
        Generator.check(autojinja.JinjaTemplate, input, output, expected, None, var = "\"Hello world\"", var2 = "[[[ test ]]][[[ end ]]]")
    def test_11_remove_markers(self):
        input    = "  // [[[ {{ var }} ]]]\n" \
                   "  // [[[ end ]]]\n" \
                   "var\n" \
                   "  {{ var2 }}"
        expected = "  \"Hello world\"\n" \
                   "var\n" \
                   "  test"
        Generator.check(autojinja.JinjaTemplate, input, None, expected, True, var = "\"Hello world\"", var2 = "[[[ test ]]][[[ end ]]]")

    def test_12(self):
        input    = "{{ var2 }} [[[ {{ var }} ]]] [[[ end ]]] {{ var2 }} [[[ {{ var }} ]]] [[[ end ]]]"
        expected = "[[[ test ]]] test [[[ end ]]] [[[ {{ var }} ]]] \"Hello world\" [[[ end ]]] [[[ test ]]] test [[[ end ]]] [[[ {{ var }} ]]] \"Hello world\" [[[ end ]]]"
        Generator.check(autojinja.JinjaTemplate, input, None, expected, None, var = "\"Hello world\"", var2 = "[[[ test ]]][[[ end ]]]")
    def test_12_output(self):
        input    = "{{ var2 }} [[[ {{ var }} ]]] [[[ end ]]] {{ var2 }} [[[ {{ var }} ]]] [[[ end ]]]"
        expected = "[[[ test ]]] test [[[ end ]]] [[[ {{ var }} ]]] \"Hello world\" [[[ end ]]] [[[ test ]]] test [[[ end ]]] [[[ {{ var }} ]]] \"Hello world\" [[[ end ]]]"
        output   = "Test"
        Generator.check(autojinja.JinjaTemplate, input, output, expected, None, var = "\"Hello world\"", var2 = "[[[ test ]]][[[ end ]]]")
    def test_12_remove_markers(self):
        input    = "{{ var2 }} [[[ {{ var }} ]]] [[[ end ]]] {{ var2 }} [[[ {{ var }} ]]] [[[ end ]]]"
        expected = "test \"Hello world\" test \"Hello world\""
        Generator.check(autojinja.JinjaTemplate, input, None, expected, True, var = "\"Hello world\"", var2 = "[[[ test ]]][[[ end ]]]")

    def test_13(self):
        input = "  // [[[ {{ var }} ]]]\n" \
                "  // [[[ end ]]]"
        with open(input_file, 'w') as f:
            f.write(input)
        def callable():
            template = autojinja.JinjaTemplate.from_file(input_file)
            template.context(var = "\"Hello world\"").render_file()
        msg = "output filepath parameter can't be None"
        assert_exception(callable, AssertionError, msg)

    def test_14(self):
        input    = "<<[ abc ]>>\n" \
                   "test1\n" \
                   "<<[ end ]>>\n" \
                   "<<[ def ]>>\n" \
                   "test2\n" \
                   "<<[ end ]>>"
        expected = "<<[ abc ]>>\n" \
                   "dummy\n" \
                   "<<[ end ]>>\n" \
                   "<<[ def ]>>\n" \
                   "test2\n" \
                   "<<[ end ]>>"
        output   = "<<[ abc ]>> dummy <<[ end ]>>"
        template = autojinja.JinjaTemplate.from_string(input)
        dummy = template.edits
        result = template.context().render(output)
        if result != expected:
            raise DiffException(result, expected)
        assert len(template.blocks) == 2
        assert len(template.cog_blocks) == 0
        assert len(template.edit_blocks) == 2

    def test_15(self):
        input    = "{% for value in values %}\n" \
                   "<<[ {{ value }} ]>> a <<[ end ]>>\n" \
                   "{% endfor %}"
        expected = "<<[ abc ]>> a <<[ end ]>>\n" \
                   "<<[ def ]>> a <<[ end ]>>\n" \
                   "<<[ ghi ]>> a <<[ end ]>>\n"
        template = autojinja.JinjaTemplate.from_string(input)
        result = template.context(values = ["abc", "def", "ghi"]).render()
        if result != expected:
            raise DiffException(result, expected)

    def test_16(self):
        input    = "{% for value in values %}\n" \
                   "<<[ {{ value }} ]>> {{ value }} <<[ end ]>>\n" \
                   "{% endfor %}"
        expected = "<<[ abc ]>> abc <<[ end ]>>\n" \
                   "<<[ def ]>> def <<[ end ]>>\n" \
                   "<<[ ghi ]>> ghi <<[ end ]>>\n"
        template = autojinja.JinjaTemplate.from_string(input)
        result = template.context(values = ["abc", "def", "ghi"]).render()
        if result != expected:
            raise DiffException(result, expected)

    def test_17(self):
        input    = "<<[ {{ value1 }} ]>> {{ value1 }} <<[ end ]>>\n" \
                   "{% for value in values %}\n" \
                   "<<[ {{ value }} ]>> {{ value }} <<[ end ]>>\n" \
                   "{% endfor %}"
        expected = "<<[ hhh ]>> hhh <<[ end ]>>\n" \
                   "<<[ abc ]>> abc <<[ end ]>>\n" \
                   "<<[ def ]>> def <<[ end ]>>\n" \
                   "<<[ ghi ]>> ghi <<[ end ]>>\n"
        template = autojinja.JinjaTemplate.from_string(input)
        result = template.context(values = ["abc", "def", "ghi"], value1 = "hhh").render()
        if result != expected:
            raise DiffException(result, expected)

    def test_18(self):
        input    = "<<[ {{ value1 }} ]>>\n" \
                   "a\n" \
                   "[[[ {{ value2 }} ]]][[[ end ]]]\n" \
                   "b\n" \
                   "<<[ end ]>>"
        expected = "<<[ hhh ]>>\n" \
                   "a\n" \
                   "[[[ {{ value2 }} ]]] abc [[[ end ]]]\n" \
                   "b\n" \
                   "<<[ end ]>>"
        template = autojinja.JinjaTemplate.from_string(input)
        result = template.context(value1 = "hhh", value2 = "abc").render()
        if result != expected:
            raise DiffException(result, expected)

    def test_19(self):
        input    = "<<[ {{ value1 }} ]>> {{ value1 }} <<[ end ]>>\n" \
                   "{% for value in values %}\n" \
                   "<<[ {{ value }} ]>> {{ value }} <<[ end ]>>\n" \
                   "{% endfor %}"
        expected = "<<[ hhh ]>> zzz <<[ end ]>>\n" \
                   "<<[ abc ]>> abc <<[ end ]>>\n" \
                   "<<[ def ]>> def <<[ end ]>>\n" \
                   "<<[ ghi ]>> ghi <<[ end ]>>\n"
        output   = "<<[ hhh ]>> zzz <<[ end ]>>\n"
        template = autojinja.JinjaTemplate.from_string(input)
        result = template.context(values = ["abc", "def", "ghi"], value1 = "hhh").render(output)
        if result != expected:
            raise DiffException(result, expected)

    def test_20(self):
        input    = "<<[ {{ value1 }} ]>> {{ value1 }} <<[ end ]>>\n" \
                   "{% for value in values %}\n" \
                   "<<[ {{ value }} ]>> {{ value }} <<[ end ]>>\n" \
                   "{% endfor %}"
        expected = "<<[ hhh ]>> hhh <<[ end ]>>\n" \
                   "<<[ abc ]>> abc <<[ end ]>>\n" \
                   "<<[ def ]>> def <<[ end ]>>\n" \
                   "<<[ ghi ]>> zzz <<[ end ]>>\n"
        output   = "<<[ ghi ]>> zzz <<[ end ]>>\n"
        template = autojinja.JinjaTemplate.from_string(input)
        result = template.context(values = ["abc", "def", "ghi"], value1 = "hhh").render(output)
        if result != expected:
            raise DiffException(result, expected)

    def test_21(self):
        input    = "  <<[ {{ value1 }} ]>>\n" \
                   "  a\n" \
                   "  [[[ {{ value2 }} ]]][[[ end ]]]\n" \
                   "  b\n" \
                   "  <<[ end ]>>"
        expected = "  <<[ hhh ]>>\n" \
                   "  zzz\n" \
                   "  <<[ end ]>>"
        output   = "<<[ hhh ]>> zzz <<[ end ]>>"
        template = autojinja.JinjaTemplate.from_string(input)
        result = template.context(value1 = "hhh", value2 = "abc").render(output)
        if result != expected:
            raise DiffException(result, expected)

    def test_22(self):
        input    = "  <<[ {{ value1 }} ]>>\n" \
                   "  a\n" \
                   "      [[[ {{ value2 }} ]]]\n" \
                   "      [[[ end ]]]\n" \
                   "  b\n" \
                   "  <<[ end ]>>"
        expected = "  <<[ hhh ]>>\n" \
                   "  a\n" \
                   "      [[[ {{ value2 }} ]]]\n" \
                   "      abc\n" \
                   "      [[[ end ]]]\n" \
                   "  b\n" \
                   "  <<[ end ]>>"
        template = autojinja.JinjaTemplate.from_string(input)
        result = template.context(value1 = "hhh", value2 = "abc").render()
        if result != expected:
            raise DiffException(result, expected)

    def test_23(self):
        input    = "  <<[ {{ value }} ]>>\n" \
                   "  a\n" \
                   "      [[[ {{ value }} ]]]\n" \
                   "      [[[ end ]]]\n" \
                   "  b\n" \
                   "  <<[ end ]>>"
        expected = "  <<[ hhh ]>>\n" \
                   "  a\n" \
                   "      [[[ {{ value }} ]]]\n" \
                   "      hhh\n" \
                   "      [[[ end ]]]\n" \
                   "  b\n" \
                   "  <<[ end ]>>"
        template = autojinja.JinjaTemplate.from_string(input)
        result = template.context(value = "hhh").render()
        if result != expected:
            raise DiffException(result, expected)

    def test_24(self):
        input    = "  <<[ {{ value1 }} ]>>\n" \
                   "  a\n" \
                   "      [[[ <<[ {{ value2 }} ]>><<[ end ]>> ]]]\n" \
                   "      [[[ end ]]]\n" \
                   "  b\n" \
                   "  <<[ end ]>>"
        expected = "  <<[ hhh ]>>\n" \
                   "  a\n" \
                   "      [[[ <<[ {{ value2 }} ]>><<[ end ]>> ]]]\n" \
                   "      <<[ zzz ]>>  <<[ end ]>>\n" \
                   "      [[[ end ]]]\n" \
                   "  b\n" \
                   "  <<[ end ]>>"
        template = autojinja.JinjaTemplate.from_string(input)
        result = template.context(value1 = "hhh", value2 = "zzz").render()
        if result != expected:
            raise DiffException(result, expected)

    def test_25(self):
        input    = "{% for value in values %}\n" \
                   "[[[ {{ value }} ]]] [[[ end ]]]\n" \
                   "{% endfor %}"
        expected = "[[[ {{ value }} ]]] zzz [[[ end ]]]\n" \
                   "[[[ {{ value }} ]]] zzz [[[ end ]]]\n" \
                   "[[[ {{ value }} ]]] zzz [[[ end ]]]\n"
        template = autojinja.JinjaTemplate.from_string(input)
        result = template.context(values = ["abc", "def", "ghi"], value = "zzz").render()
        if result != expected:
            raise DiffException(result, expected)

    def test_26(self):
        input    = "    <<[ abc ]>>\n" \
                   "    dummy\n" \
                   "    <<[ end ]>>\n" \
                   "  <<[ def ]>>\n" \
                   "  test2\n" \
                   "  <<[ end ]>>"
        expected = "    <<[ abc ]>>\n" \
                   "    A\n" \
                   "    \n" \
                   "    B\n" \
                   "    \n" \
                   "    C\n" \
                   "    <<[ end ]>>\n" \
                   "  <<[ def ]>>\n" \
                   "  test2\n" \
                   "  <<[ end ]>>"
        output   = "    <<[ abc ]>>\n" \
                   "    A\n" \
                   "    \n" \
                   "    B\n" \
                   "    \n" \
                   "    C\n" \
                   "    <<[ end ]>>"
        template = autojinja.JinjaTemplate.from_string(input)
        dummy = template.edits
        result = template.context().render(output)
        if result != expected:
            raise DiffException(result, expected)
        assert len(template.blocks) == 2
        assert len(template.cog_blocks) == 0
        assert len(template.edit_blocks) == 2

    def test_27(self):
        input    = "    <<[ abc ]>>\n" \
                   "    dummy\n" \
                   "    <<[ end ]>>\n" \
                   "  <<[ def ]>>\n" \
                   "  test2\n" \
                   "  <<[ end ]>>"
        expected = "    <<[ abc ]>>\n" \
                   "    A\n" \
                   "    \n" \
                   "    B\n" \
                   "    \n" \
                   "    C\n" \
                   "    <<[ end ]>>\n" \
                   "  <<[ def ]>>\n" \
                   "  test2\n" \
                   "  <<[ end ]>>"
        output   = "    <<[ abc ]>>\n" \
                   "    A\n" \
                   "\n" \
                   "    B\n" \
                   "\n" \
                   "    C\n" \
                   "    <<[ end ]>>"
        template = autojinja.JinjaTemplate.from_string(input)
        dummy = template.edits
        result = template.context().render(output)
        if result != expected:
            raise DiffException(result, expected)

    def test_28(self):
        input    = "    <<[ abc ]>>\n" \
                   "    dummy\n" \
                   "    <<[ end ]>>\n" \
                   "  <<[ def ]>>\n" \
                   "  test2\n" \
                   "  <<[ end ]>>"
        expected = "    <<[ abc ]>>\n" \
                   "    A\n" \
                   "    \n" \
                   "    B\n" \
                   "    <<[ end ]>>\n" \
                   "  <<[ def ]>>\n" \
                   "  test2\n" \
                   "  <<[ end ]>>"
        output   = "    <<[ abc ]>>\n" \
                   "    A\n" \
                   "  \n" \
                   "    B\n" \
                   "\n" \
                   "    <<[ end ]>>"
        template = autojinja.JinjaTemplate.from_string(input)
        dummy = template.edits
        result = template.context().render(output)
        if result != expected:
            raise DiffException(result, expected)
        assert len(template.blocks) == 2
        assert len(template.cog_blocks) == 0
        assert len(template.edit_blocks) == 2

    def test_29(self):
        input    = "    <<[ abc ]>>\n" \
                   "    dummy\n" \
                   "    <<[ end ]>>\n" \
                   "  <<[ def ]>>\n" \
                   "  test2\n" \
                   "  <<[ end ]>>"
        expected = "    <<[ abc ]>>\n" \
                   "    A\n" \
                   "    d\n" \
                   "    B\n" \
                   "    f\n" \
                   "    C\n" \
                   "    <<[ end ]>>\n" \
                   "  <<[ def ]>>\n" \
                   "  test2\n" \
                   "  <<[ end ]>>"
        output   = "    <<[ abc ]>>\n" \
                   "    A\n" \
                   "  d\n" \
                   "    B\n" \
                   "  f\n" \
                   "    C\n" \
                   "    <<[ end ]>>"
        template = autojinja.JinjaTemplate.from_string(input)
        dummy = template.edits
        result = template.context().render(output)
        if result != expected:
            raise DiffException(result, expected)

    def test_30(self):
        input    = "    <<[ abc ]>>\n" \
                   "    dummy <<[ end ]>>\n" \
                   "  <<[ def ]>>\n" \
                   "  test2\n" \
                   "  <<[ end ]>>"
        expected = "    <<[ abc ]>>\n" \
                   "    A\n" \
                   "    \n" \
                   "    B\n" \
                   "    \n" \
                   "    C\n" \
                   "    dummy <<[ end ]>>\n" \
                   "  <<[ def ]>>\n" \
                   "  test2\n" \
                   "  <<[ end ]>>"
        output   = "    <<[ abc ]>>\n" \
                   "    A\n" \
                   "    \n" \
                   "    B\n" \
                   "    \n" \
                   "    C\n" \
                   "    <<[ end ]>>"
        template = autojinja.JinjaTemplate.from_string(input)
        dummy = template.edits
        result = template.context().render(output)
        if result != expected:
            raise DiffException(result, expected)
        assert len(template.blocks) == 2
        assert len(template.cog_blocks) == 0
        assert len(template.edit_blocks) == 2

### Miscellaneous

class Test_Miscellaneous:
    def test_1(self):
        class test:
            def generate(self):
                expected = str(self)
                template = autojinja.RawTemplate.from_string("{{ this }}")
                result = template.context(**locals()).render()
                if result != expected:
                    raise DiffException(result, expected)
        test().generate()

    def test_2(self):
        class test:
            def generate(self):
                expected = "[[[ {{ this }} ]]] " + str(self) + " [[[ end]]]"
                template = autojinja.CogTemplate.from_string("[[[ {{ this }} ]]][[[ end]]]")
                result = template.context(**locals()).render()
                if result != expected:
                    raise DiffException(result, expected)
        test().generate()

    def test_3(self):
        class test:
            def generate(self):
                expected = str(self)
                template = autojinja.JinjaTemplate.from_string("{{ this }}")
                result = template.context(**locals()).render()
                if result != expected:
                    raise DiffException(result, expected)
        test().generate()

    def test_wrap_objects_debug_off(self):
        os.environ[autojinja.defaults.AUTOJINJA_DEBUG] = "0"
        class1 = Class1()
        class2 = Class2()
        class3 = Class3()

        msg = "\n  File \"\", line ?, in top-level template code\n" \
                "'tests.Class1 object' has no attribute 'x'"
        invalid_autojinja("{{ class1.x }}", jinja2.exceptions.UndefinedError, msg, **locals())
        if sys.version_info[1] < 11:
            msg = "\n  File \"\", line ?, in top-level template code\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return self.missing_f\n" \
                    "'Class1' object has no attribute 'missing_f'"
        else:
            msg = "\n  File \"\", line ?, in top-level template code\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return self.missing_f\n" \
                    "           ^^^^^^^^^^^^^^\n" \
                    "'Class1' object has no attribute 'missing_f'"
        invalid_autojinja("{{ class1.f() }}", AttributeError, msg, **locals())
        msg = "\n  File \"\", line ?, in ex\n" \
                "    raise Exception(\"ex\")\n" \
                "ex"
        invalid_autojinja("{{ class1.ex }}", Exception, msg, **locals())
        msg = "\n  File \"\", line ?, in top-level template code\n" \
                "  File \"\", line ?, in ef\n" \
                "    raise Exception(\"ef\")\n" \
                "ef"
        invalid_autojinja("{{ class1.ef() }}", Exception, msg, **locals())

        msg = "\n  File \"\", line ?, in top-level template code\n" \
                "'tests.Class2 object' has no attribute 'x'"
        invalid_autojinja("{{ class2.x }}", jinja2.exceptions.UndefinedError, msg, **locals())
        if sys.version_info[1] < 11:
            msg = "\n  File \"\", line ?, in top-level template code\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return Class1().f()\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return self.missing_f\n" \
                    "'Class1' object has no attribute 'missing_f'"
        else:
            msg = "\n  File \"\", line ?, in top-level template code\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return Class1().f()\n" \
                    "           ^^^^^^^^^^^^\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return self.missing_f\n" \
                    "           ^^^^^^^^^^^^^^\n" \
                    "'Class1' object has no attribute 'missing_f'"
        invalid_autojinja("{{ class2.f() }}", AttributeError, msg, **locals())
        if sys.version_info[1] < 11:
            msg = "\n  File \"\", line ?, in ex\n" \
                    "    return Class1().ex\n" \
                    "  File \"\", line ?, in ex\n" \
                    "    raise Exception(\"ex\")\n" \
                    "ex"
        else:
            msg = "\n  File \"\", line ?, in ex\n" \
                    "    return Class1().ex\n" \
                    "           ^^^^^^^^^^^\n" \
                    "  File \"\", line ?, in ex\n" \
                    "    raise Exception(\"ex\")\n" \
                    "ex"
        invalid_autojinja("{{ class2.ex }}", Exception, msg, **locals())
        if sys.version_info[1] < 11:
            msg = "\n  File \"\", line ?, in top-level template code\n" \
                    "  File \"\", line ?, in ef\n" \
                    "    return Class1().ef()\n" \
                    "  File \"\", line ?, in ef\n" \
                    "    raise Exception(\"ef\")\n" \
                    "ef"
        else:
            msg = "\n  File \"\", line ?, in top-level template code\n" \
                    "  File \"\", line ?, in ef\n" \
                    "    return Class1().ef()\n" \
                    "           ^^^^^^^^^^^^^\n" \
                    "  File \"\", line ?, in ef\n" \
                    "    raise Exception(\"ef\")\n" \
                    "ef"
        invalid_autojinja("{{ class2.ef() }}", Exception, msg, **locals())

        msg = "\n  File \"\", line ?, in top-level template code\n" \
                "'tests.Class3 object' has no attribute 'x'"
        invalid_autojinja("{{ class3.x }}", jinja2.exceptions.UndefinedError, msg, **locals())
        if sys.version_info[1] < 11:
            msg = "\n  File \"\", line ?, in top-level template code\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return Class2().f()\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return Class1().f()\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return self.missing_f\n" \
                    "'Class1' object has no attribute 'missing_f'"
        else:
            msg = "\n  File \"\", line ?, in top-level template code\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return Class2().f()\n" \
                    "           ^^^^^^^^^^^^\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return Class1().f()\n" \
                    "           ^^^^^^^^^^^^\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return self.missing_f\n" \
                    "           ^^^^^^^^^^^^^^\n" \
                    "'Class1' object has no attribute 'missing_f'"
        invalid_autojinja("{{ class3.f() }}", AttributeError, msg, **locals())
        if sys.version_info[1] < 11:
            msg = "\n  File \"\", line ?, in ex\n" \
                    "    return Class2().ex\n" \
                    "  File \"\", line ?, in ex\n" \
                    "    return Class1().ex\n" \
                    "  File \"\", line ?, in ex\n" \
                    "    raise Exception(\"ex\")\n" \
                    "ex"
        else:
            msg = "\n  File \"\", line ?, in ex\n" \
                    "    return Class2().ex\n" \
                    "           ^^^^^^^^^^^\n" \
                    "  File \"\", line ?, in ex\n" \
                    "    return Class1().ex\n" \
                    "           ^^^^^^^^^^^\n" \
                    "  File \"\", line ?, in ex\n" \
                    "    raise Exception(\"ex\")\n" \
                    "ex"
        invalid_autojinja("{{ class3.ex }}", Exception, msg, **locals())
        if sys.version_info[1] < 11:
            msg = "\n  File \"\", line ?, in top-level template code\n" \
                    "  File \"\", line ?, in ef\n" \
                    "    return Class2().ef()\n" \
                    "  File \"\", line ?, in ef\n" \
                    "    return Class1().ef()\n" \
                    "  File \"\", line ?, in ef\n" \
                    "    raise Exception(\"ef\")\n" \
                    "ef"
        else:
            msg = "\n  File \"\", line ?, in top-level template code\n" \
                    "  File \"\", line ?, in ef\n" \
                    "    return Class2().ef()\n" \
                    "           ^^^^^^^^^^^^^\n" \
                    "  File \"\", line ?, in ef\n" \
                    "    return Class1().ef()\n" \
                    "           ^^^^^^^^^^^^^\n" \
                    "  File \"\", line ?, in ef\n" \
                    "    raise Exception(\"ef\")\n" \
                    "ef"
        invalid_autojinja("{{ class3.ef() }}", Exception, msg, **locals())
        del os.environ[autojinja.defaults.AUTOJINJA_DEBUG]

    def test_wrap_objects_debug_on(self):
        os.environ[autojinja.defaults.AUTOJINJA_DEBUG] = "1"
        class1 = Class1()
        class2 = Class2()
        class3 = Class3()

        if sys.version_info[1] < 11:
            msg = "\n  File \"\", line ?, in autojinja_wrapped_fcall\n" \
                    "    raise DebugAttributeError(message) from None\n" \
                    "  File \"\", line ?, in x\n" \
                    "    return self.missing_x\n" \
                    "AttributeError: 'Class1' object has no attribute 'missing_x'"
        else:
            msg = "\n  File \"\", line ?, in autojinja_wrapped_fcall\n" \
                    "    raise DebugAttributeError(message) from None\n" \
                    "  File \"\", line ?, in x\n" \
                    "    return self.missing_x\n" \
                    "           ^^^^^^^^^^^^^^\n" \
                    "AttributeError: 'Class1' object has no attribute 'missing_x'"
        invalid_autojinja("{{ class1.x }}", autojinja.exceptions.DebugAttributeError, msg, **locals())
        if sys.version_info[1] < 11:
            msg = "\n  File \"\", line ?, in top-level template code\n" \
                    "  File \"\", line ?, in autojinja_wrapped_fcall\n" \
                    "    raise DebugAttributeError(message) from None\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return self.missing_f\n" \
                    "AttributeError: 'Class1' object has no attribute 'missing_f'"
        else:
            msg = "\n  File \"\", line ?, in top-level template code\n" \
                    "  File \"\", line ?, in autojinja_wrapped_fcall\n" \
                    "    raise DebugAttributeError(message) from None\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return self.missing_f\n" \
                    "           ^^^^^^^^^^^^^^\n" \
                    "AttributeError: 'Class1' object has no attribute 'missing_f'"
        invalid_autojinja("{{ class1.f() }}", autojinja.exceptions.DebugAttributeError, msg, **locals())
        msg = "\n  File \"\", line ?, in autojinja_wrapped_fcall\n" \
                "    raise wrap_exception(e, message).with_traceback(None)\n" \
                "  File \"\", line ?, in ex\n" \
                "    raise Exception(\"ex\")\n" \
                "Exception: ex"
        invalid_autojinja("{{ class1.ex }}", Exception, msg, **locals())
        msg = "\n  File \"\", line ?, in top-level template code\n" \
                "  File \"\", line ?, in autojinja_wrapped_fcall\n" \
                "    raise wrap_exception(e, message).with_traceback(None)\n" \
                "  File \"\", line ?, in ef\n" \
                "    raise Exception(\"ef\")\n" \
                "Exception: ef"
        invalid_autojinja("{{ class1.ef() }}", Exception, msg, **locals())

        if sys.version_info[1] < 11:
            msg = "\n  File \"\", line ?, in autojinja_wrapped_fcall\n" \
                    "    raise wrap_exception(e, message).with_traceback(None)\n" \
                    "  File \"\", line ?, in x\n" \
                    "    return Class1().x\n" \
                    "  File \"\", line ?, in x\n" \
                    "    return self.missing_x\n" \
                    "AttributeError: 'Class1' object has no attribute 'missing_x'"
        else:
            msg = "\n  File \"\", line ?, in autojinja_wrapped_fcall\n" \
                    "    raise wrap_exception(e, message).with_traceback(None)\n" \
                    "  File \"\", line ?, in x\n" \
                    "    return Class1().x\n" \
                    "           ^^^^^^^^^^\n" \
                    "  File \"\", line ?, in x\n" \
                    "    return self.missing_x\n" \
                    "           ^^^^^^^^^^^^^^\n" \
                    "AttributeError: 'Class1' object has no attribute 'missing_x'"
        invalid_autojinja("{{ class2.x }}", autojinja.exceptions.DebugAttributeError, msg, **locals())
        if sys.version_info[1] < 11:
            msg = "\n  File \"\", line ?, in top-level template code\n" \
                    "  File \"\", line ?, in autojinja_wrapped_fcall\n" \
                    "    raise DebugAttributeError(message) from None\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return Class1().f()\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return self.missing_f\n" \
                    "AttributeError: 'Class1' object has no attribute 'missing_f'"
        else:
            msg = "\n  File \"\", line ?, in top-level template code\n" \
                    "  File \"\", line ?, in autojinja_wrapped_fcall\n" \
                    "    raise DebugAttributeError(message) from None\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return Class1().f()\n" \
                    "           ^^^^^^^^^^^^\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return self.missing_f\n" \
                    "           ^^^^^^^^^^^^^^\n" \
                    "AttributeError: 'Class1' object has no attribute 'missing_f'"
        invalid_autojinja("{{ class2.f() }}", autojinja.exceptions.DebugAttributeError, msg, **locals())
        if sys.version_info[1] < 11:
            msg = "\n  File \"\", line ?, in autojinja_wrapped_fcall\n" \
                    "    raise wrap_exception(e, message).with_traceback(None)\n" \
                    "  File \"\", line ?, in ex\n" \
                    "    return Class1().ex\n" \
                    "  File \"\", line ?, in ex\n" \
                    "    raise Exception(\"ex\")\n" \
                    "Exception: ex"
        else:
            msg = "\n  File \"\", line ?, in autojinja_wrapped_fcall\n" \
                    "    raise wrap_exception(e, message).with_traceback(None)\n" \
                    "  File \"\", line ?, in ex\n" \
                    "    return Class1().ex\n" \
                    "           ^^^^^^^^^^^\n" \
                    "  File \"\", line ?, in ex\n" \
                    "    raise Exception(\"ex\")\n" \
                    "Exception: ex"
        invalid_autojinja("{{ class2.ex }}", Exception, msg, **locals())
        if sys.version_info[1] < 11:
            msg = "\n  File \"\", line ?, in top-level template code\n" \
                    "  File \"\", line ?, in autojinja_wrapped_fcall\n" \
                    "    raise wrap_exception(e, message).with_traceback(None)\n" \
                    "  File \"\", line ?, in ef\n" \
                    "    return Class1().ef()\n" \
                    "  File \"\", line ?, in ef\n" \
                    "    raise Exception(\"ef\")\n" \
                    "Exception: ef"
        else:
            msg = "\n  File \"\", line ?, in top-level template code\n" \
                    "  File \"\", line ?, in autojinja_wrapped_fcall\n" \
                    "    raise wrap_exception(e, message).with_traceback(None)\n" \
                    "  File \"\", line ?, in ef\n" \
                    "    return Class1().ef()\n" \
                    "           ^^^^^^^^^^^^^\n" \
                    "  File \"\", line ?, in ef\n" \
                    "    raise Exception(\"ef\")\n" \
                    "Exception: ef"
        invalid_autojinja("{{ class2.ef() }}", Exception, msg, **locals())

        if sys.version_info[1] < 11:
            msg = "\n  File \"\", line ?, in autojinja_wrapped_fcall\n" \
                    "    raise wrap_exception(e, message).with_traceback(None)\n" \
                    "  File \"\", line ?, in x\n" \
                    "    return Class2().x\n" \
                    "  File \"\", line ?, in x\n" \
                    "    return Class1().x\n" \
                    "  File \"\", line ?, in x\n" \
                    "    return self.missing_x\n" \
                    "AttributeError: 'Class1' object has no attribute 'missing_x'"
        else:
            msg = "\n  File \"\", line ?, in autojinja_wrapped_fcall\n" \
                    "    raise wrap_exception(e, message).with_traceback(None)\n" \
                    "  File \"\", line ?, in x\n" \
                    "    return Class2().x\n" \
                    "           ^^^^^^^^^^\n" \
                    "  File \"\", line ?, in x\n" \
                    "    return Class1().x\n" \
                    "           ^^^^^^^^^^\n" \
                    "  File \"\", line ?, in x\n" \
                    "    return self.missing_x\n" \
                    "           ^^^^^^^^^^^^^^\n" \
                    "AttributeError: 'Class1' object has no attribute 'missing_x'"
        invalid_autojinja("{{ class3.x }}", autojinja.exceptions.DebugAttributeError, msg, **locals())
        if sys.version_info[1] < 11:
            msg = "\n  File \"\", line ?, in top-level template code\n" \
                    "  File \"\", line ?, in autojinja_wrapped_fcall\n" \
                    "    raise DebugAttributeError(message) from None\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return Class2().f()\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return Class1().f()\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return self.missing_f\n" \
                    "AttributeError: 'Class1' object has no attribute 'missing_f'"
        else:
            msg = "\n  File \"\", line ?, in top-level template code\n" \
                    "  File \"\", line ?, in autojinja_wrapped_fcall\n" \
                    "    raise DebugAttributeError(message) from None\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return Class2().f()\n" \
                    "           ^^^^^^^^^^^^\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return Class1().f()\n" \
                    "           ^^^^^^^^^^^^\n" \
                    "  File \"\", line ?, in f\n" \
                    "    return self.missing_f\n" \
                    "           ^^^^^^^^^^^^^^\n" \
                    "AttributeError: 'Class1' object has no attribute 'missing_f'"
        invalid_autojinja("{{ class3.f() }}", autojinja.exceptions.DebugAttributeError, msg, **locals())
        if sys.version_info[1] < 11:
            msg = "\n  File \"\", line ?, in autojinja_wrapped_fcall\n" \
                    "    raise wrap_exception(e, message).with_traceback(None)\n" \
                    "  File \"\", line ?, in ex\n" \
                    "    return Class2().ex\n" \
                    "  File \"\", line ?, in ex\n" \
                    "    return Class1().ex\n" \
                    "  File \"\", line ?, in ex\n" \
                    "    raise Exception(\"ex\")\n" \
                    "Exception: ex"
        else:
            msg = "\n  File \"\", line ?, in autojinja_wrapped_fcall\n" \
                    "    raise wrap_exception(e, message).with_traceback(None)\n" \
                    "  File \"\", line ?, in ex\n" \
                    "    return Class2().ex\n" \
                    "           ^^^^^^^^^^^\n" \
                    "  File \"\", line ?, in ex\n" \
                    "    return Class1().ex\n" \
                    "           ^^^^^^^^^^^\n" \
                    "  File \"\", line ?, in ex\n" \
                    "    raise Exception(\"ex\")\n" \
                    "Exception: ex"
        invalid_autojinja("{{ class3.ex }}", Exception, msg, **locals())
        if sys.version_info[1] < 11:
            msg = "\n  File \"\", line ?, in top-level template code\n" \
                    "  File \"\", line ?, in autojinja_wrapped_fcall\n" \
                    "    raise wrap_exception(e, message).with_traceback(None)\n" \
                    "  File \"\", line ?, in ef\n" \
                    "    return Class2().ef()\n" \
                    "  File \"\", line ?, in ef\n" \
                    "    return Class1().ef()\n" \
                    "  File \"\", line ?, in ef\n" \
                    "    raise Exception(\"ef\")\n" \
                    "Exception: ef"
        else:
            msg = "\n  File \"\", line ?, in top-level template code\n" \
                    "  File \"\", line ?, in autojinja_wrapped_fcall\n" \
                    "    raise wrap_exception(e, message).with_traceback(None)\n" \
                    "  File \"\", line ?, in ef\n" \
                    "    return Class2().ef()\n" \
                    "           ^^^^^^^^^^^^^\n" \
                    "  File \"\", line ?, in ef\n" \
                    "    return Class1().ef()\n" \
                    "           ^^^^^^^^^^^^^\n" \
                    "  File \"\", line ?, in ef\n" \
                    "    raise Exception(\"ef\")\n" \
                    "Exception: ef"
        invalid_autojinja("{{ class3.ef() }}", Exception, msg, **locals())
        del os.environ[autojinja.defaults.AUTOJINJA_DEBUG]

    def test_multicontext_RawTemplate(self):
        input    = "{{ var1 }},{{ var2 }},{{ var3 }}"
        expected = "1,2,33"
        template = autojinja.RawTemplate.from_string(input)
        result   = template.context(var1 = 1, var3 = 3).context(var2 = 2, var3 = 33).render()
        assert result == expected

    def test_multicontext_CogTemplate(self):
        input    = "[[[{{ var1 }},{{ var2 }},{{ var3 }}]]][[[end]]]"
        expected = "[[[{{ var1 }},{{ var2 }},{{ var3 }}]]] 1,2,33 [[[end]]]"
        template = autojinja.CogTemplate.from_string(input)
        result   = template.context(var1 = 1, var3 = 3).context(var2 = 2, var3 = 33).render()
        assert result == expected

    def test_multicontext_JinjaTemplate(self):
        input    = "{{ var1 }},{{ var2 }},{{ var3 }}[[[{{ var1 }},{{ var2 }},{{ var3 }}]]][[[end]]]"
        expected = "1,2,33[[[{{ var1 }},{{ var2 }},{{ var3 }}]]] 1,2,33 [[[end]]]"
        template = autojinja.JinjaTemplate.from_string(input)
        result = template.context(var1 = 1, var3 = 3).context(var2 = 2, var3 = 33).render()
        assert result == expected
