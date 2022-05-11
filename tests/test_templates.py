import autojinja
import os
import tempfile

class CustomException(Exception):
    def __init__(self, result, expected):
        result = str(result).replace('\t', "\\t").replace('\n', "\\n\n")
        expected = str(expected).replace('\t', "\\t").replace('\n', "\\n\n")
        message = f"--- Expected ---\n{expected}\\0\n--- Got ---\n{result}\\0"
        super().__init__(message)

settingsRemoveMarkers = autojinja.ParserSettings(remove_markers = True)
settingsPreserveMarkers = autojinja.ParserSettings(remove_markers = False)

tmp = tempfile.TemporaryDirectory()
root = autojinja.path[tmp.name]
input_file = root.join("input.txt")
output_file = root.join("output.txt")

### RawTemplate

class Generator_RawTemplate:
    def render(template, expected, args, kwargs):
        result = template.context(*args, **kwargs).render()
        if result != expected:
            raise CustomException(result, expected)

    def render_file(template, expected, output, encoding, newline, args, kwargs):
        result = template.context(*args, **kwargs).render_file(output, encoding, newline)
        if result != expected:
            raise CustomException(result, expected)
        encoding = encoding or template.encoding
        newline = newline or template.newline
        with open(output_file, 'r', encoding = encoding, newline = newline) as f:
            content = f.read()
            if os.name == "nt": # Windows
                result = result.replace('\n', newline or '\n')
            if content != result:
                raise CustomException(content, result)

    def check(input, expected, *args, **kwargs):
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
    def render(template, output, expected, remove_markers, args, kwargs):
        result = template.context(*args, **kwargs).render(output, remove_markers)
        if result != expected:
            raise CustomException(result, expected)

    def render_file(template, output, expected, remove_markers, encoding, newline, args, kwargs):
        result = template.context(*args, **kwargs).render_file(output, remove_markers, encoding, newline)
        if result != expected:
            raise CustomException(result, expected)
        encoding = encoding or template.encoding
        newline = newline or template.newline
        with open(output_file, 'r', encoding = encoding, newline = newline) as f:
            content = f.read()
            result = result.replace('\n', newline or '\n')
            if content != result:
                raise CustomException(content, result)

    def check(class_type, input, output, expected, remove_markers, *args, **kwargs):
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
            raise CustomException(result, expected)

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
            raise CustomException(result, expected)

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
            raise CustomException(result, expected)
        with open(input_file, 'r') as f:
            content = f.read()
            if content != result:
                raise CustomException(content, result)

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
            raise CustomException(result, expected)

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
            raise CustomException(result, expected)

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
            raise CustomException(result, expected)

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
        try:
            template = autojinja.JinjaTemplate.from_file(input_file)
            template.context(var = "\"Hello world\"").render_file()
        except BaseException as e:
            exception = e
        else:
            exception = None
        if exception == None:
            raise CustomException(None, AssertionError)

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
            raise CustomException(result, expected)

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
            raise CustomException(result, expected)

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
            raise CustomException(result, expected)

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
            raise CustomException(result, expected)

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
            raise CustomException(result, expected)

    def test_19(self):
        input    = "<<[ {{ value1 }} ]>> {{ value1 }} <<[ end ]>>\n" \
                   "{% for value in values %}\n" \
                   "<<[ {{ value }} ]>> {{ value }} <<[ end ]>>\n" \
                   "{% endfor %}"
        expected = "<<[ hhh ]>> zzz <<[ end ]>>\n" \
                   "<<[ abc ]>> abc <<[ end ]>>\n" \
                   "<<[ def ]>> def <<[ end ]>>\n" \
                   "<<[ ghi ]>> ghi <<[ end ]>>\n"
        output   = "<<[ hhh ]>> zzz <<[ end ]>>"
        template = autojinja.JinjaTemplate.from_string(input)
        result = template.context(values = ["abc", "def", "ghi"], value1 = "hhh").render(output)
        if result != expected:
            raise CustomException(result, expected)

    def test_20(self):
        input    = "<<[ {{ value1 }} ]>> {{ value1 }} <<[ end ]>>\n" \
                   "{% for value in values %}\n" \
                   "<<[ {{ value }} ]>> {{ value }} <<[ end ]>>\n" \
                   "{% endfor %}"
        expected = "<<[ hhh ]>> hhh <<[ end ]>>\n" \
                   "<<[ abc ]>> abc <<[ end ]>>\n" \
                   "<<[ def ]>> def <<[ end ]>>\n" \
                   "<<[ ghi ]>> zzz <<[ end ]>>\n"
        output   = "<<[ ghi ]>> zzz <<[ end ]>>"
        template = autojinja.JinjaTemplate.from_string(input)
        result = template.context(values = ["abc", "def", "ghi"], value1 = "hhh").render(output)
        if result != expected:
            raise CustomException(result, expected)

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
            raise CustomException(result, expected)

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
            raise CustomException(result, expected)
