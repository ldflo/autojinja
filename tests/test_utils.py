from . import assert_clean_exception, Class1, Class2, Class3

import autojinja
import io
import os
import sys
import tempfile

settings1 = autojinja.parser.ParserSettings()
settings2 = autojinja.parser.ParserSettings(cog_open = autojinja.defaults.AUTOJINJA_DEFAULT_COG_OPEN,
                                            cog_close = autojinja.defaults.AUTOJINJA_DEFAULT_COG_CLOSE,
                                            cog_end = autojinja.defaults.AUTOJINJA_DEFAULT_COG_END,
                                            cog_as_comment = False,
                                            edit_open = autojinja.defaults.AUTOJINJA_DEFAULT_EDIT_OPEN,
                                            edit_close = autojinja.defaults.AUTOJINJA_DEFAULT_EDIT_CLOSE,
                                            edit_end = autojinja.defaults.AUTOJINJA_DEFAULT_EDIT_END,
                                            edit_as_comment = False,
                                            remove_markers = None,
                                            encoding = None,
                                            newline = None)

tmp = tempfile.TemporaryDirectory()
root = autojinja.path.DirPath(tmp.name)
file1 = root.join("file1.txt")
file2 = root.join("file2.txt")
file3 = root.join("file3.txt")
file4 = root.join("file4.env")
with open(file3, 'w') as f:
    f.write("// [[[\n" \
            "//     // <<[ abc ]>>\n" \
            "//     // <<[ end ]>>\n" \
            "// ]]]\n" \
            "    // <<[ abc ]>>\n" \
            "    hello\n" \
            "    // <<[ end ]>>\n" \
            "// [[[ end ]]]")
with open(file4, 'w') as f:
    f.write("VAR1=42\n" \
            "VAR3 = ${VAR1}\n" \
            "VAR4 = Test string \n" \
            "   VAR5 =${THIS_DIRPATH}/")

def invalid_autojinja(input: str, exception_type: type, message: str, *args: str, **kwargs: str):
    def function(*args: str, **kwargs: str):
        template = autojinja.CogTemplate.from_string(input)
        template.context(*args, **kwargs).render()
    assert_clean_exception(function, exception_type, message, *args, **kwargs)

class Test:
    def test_is_file_tagged(self):
        with open(file1, 'w') as f:
            f.write("import autojinja\n")
            f.write("\n")
        assert autojinja.utils.is_file_tagged(file1) == True
        with open(file1, 'w', encoding=None) as f:
            f.write("from autojinja import *\n")
            f.write("\n")
        assert autojinja.utils.is_file_tagged(file1, encoding=None) == True
        with open(file1, 'w', encoding="ascii") as f:
            f.write("autojinja\n")
            f.write("\n")
        assert autojinja.utils.is_file_tagged(file1, encoding="ascii") == True
        with open(file1, 'w', encoding="ascii") as f:
            f.write("import os.path\n")
            f.write("\n")
        assert autojinja.utils.is_file_tagged(file1, encoding="ascii") == False
        with open(file1, 'w', encoding="ascii") as f:
            f.write("\n")
            f.write("import autojinja\n")
        assert autojinja.utils.is_file_tagged(file1, encoding="ascii") == False

    def test_generate_file_0(self):
        os.environ[autojinja.defaults.AUTOJINJA_SUMMARY] = "0"
        if file2.exists:
            os.remove(file2)
        try:
            sys.stdout = io.StringIO()
            autojinja.utils.generate_file(file2, "Test1", encoding="ascii")
            with open(file2, 'r', encoding="ascii") as f:
                old_content = f.read()
                assert old_content == "Test1"
            assert sys.stdout.getvalue() == ""
            sys.stdout.truncate(0)
            sys.stdout.seek(0)
            autojinja.utils.generate_file(file2, "Test1", old_content, encoding="ascii")
            with open(file2, 'r', encoding="ascii") as f:
                old_content = f.read()
                assert old_content == "Test1"
            assert sys.stdout.getvalue() == ""
            sys.stdout.truncate(0)
            sys.stdout.seek(0)
            autojinja.utils.generate_file(file2, "Test2\nTest2", None, encoding="ascii", newline="\r\n")
            with open(file2, 'r', encoding="ascii", newline="\r\n") as f:
                old_content = f.read()
                assert old_content == "Test2\r\nTest2"
            assert sys.stdout.getvalue() == ""
        finally:
            sys.stdout = sys.__stdout__

    def test_generate_file_1(self):
        os.environ[autojinja.defaults.AUTOJINJA_SUMMARY] = "1"
        if file2.exists:
            os.remove(file2)
        try:
            sys.stdout = io.StringIO()
            autojinja.utils.generate_file(file2, "Test1", encoding="ascii")
            with open(file2, 'r', encoding="ascii") as f:
                old_content = f.read()
                assert old_content == "Test1"
            assert sys.stdout.getvalue() == f"[autojinja]    new    {file2}\n"
            sys.stdout.truncate(0)
            sys.stdout.seek(0)
            autojinja.utils.generate_file(file2, "Test1", old_content, encoding="ascii")
            with open(file2, 'r', encoding="ascii") as f:
                old_content = f.read()
                assert old_content == "Test1"
            assert sys.stdout.getvalue() == f"[autojinja]  -------  {file2}\n"
            sys.stdout.truncate(0)
            sys.stdout.seek(0)
            autojinja.utils.generate_file(file2, "Test2\nTest2", None, encoding="ascii", newline="\r\n")
            with open(file2, 'r', encoding="ascii", newline="\r\n") as f:
                old_content = f.read()
                assert old_content == "Test2\r\nTest2"
            assert sys.stdout.getvalue() == f"[autojinja]  changed  {file2}\n"
        finally:
            sys.stdout = sys.__stdout__

    def test_generate_file_2(self):
        os.environ[autojinja.defaults.AUTOJINJA_SUMMARY] = "011"
        if file2.exists:
            os.remove(file2)
        try:
            sys.stdout = io.StringIO()
            autojinja.utils.generate_file(file2, "Test1", encoding="ascii")
            with open(file2, 'r', encoding="ascii") as f:
                old_content = f.read()
                assert old_content == "Test1"
            assert sys.stdout.getvalue() == f"[autojinja]    new    {file2}  (from {autojinja.path.no_antislash(sys.argv[0])})\n"
            sys.stdout.truncate(0)
            sys.stdout.seek(0)
            autojinja.utils.generate_file(file2, "Test1", old_content, encoding="ascii")
            with open(file2, 'r', encoding="ascii") as f:
                old_content = f.read()
                assert old_content == "Test1"
            assert sys.stdout.getvalue() == f"[autojinja]  -------  {file2}  (from {autojinja.path.no_antislash(sys.argv[0])})\n"
            sys.stdout.truncate(0)
            sys.stdout.seek(0)
            autojinja.utils.generate_file(file2, "Test2\nTest2", None, encoding="ascii", newline="\r\n")
            with open(file2, 'r', encoding="ascii", newline="\r\n") as f:
                old_content = f.read()
                assert old_content == "Test2\r\nTest2"
            assert sys.stdout.getvalue() == f"[autojinja]  changed  {file2}  (from {autojinja.path.no_antislash(sys.argv[0])})\n"
        finally:
            sys.stdout = sys.__stdout__

    def test_generate_file_3(self):
        os.environ[autojinja.defaults.AUTOJINJA_SUMMARY] = "010"
        if file2.exists:
            os.remove(file2)
        try:
            sys.stdout = io.StringIO()
            autojinja.utils.generate_file(file2, "Test1", encoding="ascii")
            with open(file2, 'r', encoding="ascii") as f:
                old_content = f.read()
                assert old_content == "Test1"
            assert sys.stdout.getvalue() == f"[autojinja]    new    {file2}\n"
            sys.stdout.truncate(0)
            sys.stdout.seek(0)
            autojinja.utils.generate_file(file2, "Test1", old_content, encoding="ascii")
            with open(file2, 'r', encoding="ascii") as f:
                old_content = f.read()
                assert old_content == "Test1"
            assert sys.stdout.getvalue() == f"[autojinja]  -------  {file2}\n"
            sys.stdout.truncate(0)
            sys.stdout.seek(0)
            autojinja.utils.generate_file(file2, "Test2\nTest2", None, encoding="ascii", newline="\r\n")
            with open(file2, 'r', encoding="ascii", newline="\r\n") as f:
                old_content = f.read()
                assert old_content == "Test2\r\nTest2"
            assert sys.stdout.getvalue() == f"[autojinja]  changed  {file2}\n"
        finally:
            sys.stdout = sys.__stdout__

    def test_generate_file_4(self):
        os.environ[autojinja.defaults.AUTOJINJA_SUMMARY] = "000"
        if file2.exists:
            os.remove(file2)
        try:
            sys.stdout = io.StringIO()
            autojinja.utils.generate_file(file2, "Test1", encoding="ascii")
            with open(file2, 'r', encoding="ascii") as f:
                old_content = f.read()
                assert old_content == "Test1"
            assert sys.stdout.getvalue() == f"[autojinja]    new    {file2.relpath(autojinja.path.Path(sys.argv[0]).dirpath)}\n"
            sys.stdout.truncate(0)
            sys.stdout.seek(0)
            autojinja.utils.generate_file(file2, "Test1", old_content, encoding="ascii")
            with open(file2, 'r', encoding="ascii") as f:
                old_content = f.read()
                assert old_content == "Test1"
            assert sys.stdout.getvalue() == f"[autojinja]  -------  {file2.relpath(autojinja.path.Path(sys.argv[0]).dirpath)}\n"
            sys.stdout.truncate(0)
            sys.stdout.seek(0)
            autojinja.utils.generate_file(file2, "Test2\nTest2", None, encoding="ascii", newline="\r\n")
            with open(file2, 'r', encoding="ascii", newline="\r\n") as f:
                old_content = f.read()
                assert old_content == "Test2\r\nTest2"
            assert sys.stdout.getvalue() == f"[autojinja]  changed  {file2.relpath(autojinja.path.Path(sys.argv[0]).dirpath)}\n"
        finally:
            sys.stdout = sys.__stdout__

    def test_generate_file_5(self):
        os.environ[autojinja.defaults.AUTOJINJA_SUMMARY] = "110"
        if file2.exists:
            os.remove(file2)
        try:
            sys.stdout = io.StringIO()
            autojinja.utils.generate_file(file2, "Test1", encoding="ascii")
            with open(file2, 'r', encoding="ascii") as f:
                old_content = f.read()
                assert old_content == "Test1"
            assert sys.stdout.getvalue() == f"[autojinja]    new    {file2}\n"
            sys.stdout.truncate(0)
            sys.stdout.seek(0)
            autojinja.utils.generate_file(file2, "Test1", old_content, encoding="ascii")
            with open(file2, 'r', encoding="ascii") as f:
                old_content = f.read()
                assert old_content == "Test1"
            assert sys.stdout.getvalue() == ""
            sys.stdout.truncate(0)
            sys.stdout.seek(0)
            autojinja.utils.generate_file(file2, "Test2\nTest2", None, encoding="ascii", newline="\r\n")
            with open(file2, 'r', encoding="ascii", newline="\r\n") as f:
                old_content = f.read()
                assert old_content == "Test2\r\nTest2"
            assert sys.stdout.getvalue() == f"[autojinja]  changed  {file2}\n"
        finally:
            sys.stdout = sys.__stdout__

    def test_parse_file(self):
        object = autojinja.utils.parse_file(file3, settings1, encoding="ascii")
        assert object.settings == settings1
        assert len(object.markers) == 4
        assert object.markers[0].header == "    // <<[ abc ]>>\n" \
                                           "    // <<[ end ]>>"
        assert object.markers[0].body == "    // <<[ abc ]>>\n" \
                                         "    hello\n" \
                                         "    // <<[ end ]>>"
        assert object.markers[1].header == "abc"
        assert object.markers[1].body == "    hello"
        assert object.markers[2].header == "end"
        assert object.markers[2].body == ""
        assert object.markers[3].header == "end"
        assert object.markers[3].body == ""
        assert len(object.edit_blocks) == 1
        assert object.edit_blocks["abc"].raw_body == "    hello"
        assert object.edit_blocks["abc"].body == "hello"
        assert len(object.edits) == 1
        assert object.edits["abc"] == "hello"

    def test_parse(self):
        with open(file3, 'r', encoding="ascii") as f:
            content = f.read()
        object = autojinja.utils.parse_string(content, None)
        assert object.settings != settings2
        assert len(object.markers) == 4
        assert object.markers[0].header == "    // <<[ abc ]>>\n" \
                                           "    // <<[ end ]>>"
        assert object.markers[0].body == "    // <<[ abc ]>>\n" \
                                         "    hello\n" \
                                         "    // <<[ end ]>>"
        assert object.markers[1].header == "abc"
        assert object.markers[1].body == "    hello"
        assert object.markers[2].header == "end"
        assert object.markers[2].body == ""
        assert object.markers[3].header == "end"
        assert object.markers[3].body == ""
        assert len(object.edit_blocks) == 1
        assert object.edit_blocks["abc"].raw_header == "abc"
        assert object.edit_blocks["abc"].header == "abc"
        assert object.edit_blocks["abc"].raw_body == "    hello"
        assert object.edit_blocks["abc"].body == "hello"
        assert len(object.edits) == 1
        assert object.edits["abc"] == "hello"

    def test_blocks_from_file(self):
        blocks = autojinja.utils.blocks_from_file(file3, settings1, encoding="ascii")
        assert len(blocks) == 2

    def test_blocks_from_string(self):
        with open(file3, 'r', encoding="ascii") as f:
            content = f.read()
        blocks = autojinja.utils.blocks_from_string(content, None)
        assert len(blocks) == 2

    def test_cog_blocks_from_file(self):
        cog_blocks = autojinja.utils.cog_blocks_from_file(file3, settings1, encoding="ascii")
        assert len(cog_blocks) == 1

    def test_cog_blocks_from_string(self):
        with open(file3, 'r', encoding="ascii") as f:
            content = f.read()
        cog_blocks = autojinja.utils.cog_blocks_from_string(content, None)
        assert len(cog_blocks) == 1

    def test_edit_blocks_from_file(self):
        edit_blocks = autojinja.utils.edit_blocks_from_file(file3, settings1, encoding="ascii")
        assert len(edit_blocks) == 1
        assert edit_blocks["abc"].raw_header == "abc"
        assert edit_blocks["abc"].header == "abc"
        assert edit_blocks["abc"].raw_body == "    hello"
        assert edit_blocks["abc"].body == "hello"

    def test_edit_blocks_from_string(self):
        with open(file3, 'r', encoding="ascii") as f:
            content = f.read()
        edit_blocks = autojinja.utils.edit_blocks_from_string(content, None)
        assert len(edit_blocks) == 1
        assert edit_blocks["abc"].raw_header == "abc"
        assert edit_blocks["abc"].header == "abc"
        assert edit_blocks["abc"].raw_body == "    hello"
        assert edit_blocks["abc"].body == "hello"

    def test_edit_blocks_get_code_1(self):
        input    = "  a\n" \
                   "  b\n" \
                   "  <<[ def ]>>\n" \
                   "  test\n" \
                   "  <<[ end ]>>\n" \
                   "  c\n" \
                   "  d"
        edit_blocks = autojinja.utils.edit_blocks_from_string(input)
        edit_block = edit_blocks["def"]
        expected = "  <<[ def ]>>\n" \
                   "  test\n" \
                   "  <<[ end ]>>"
        assert edit_block.get_code() == expected
        expected = "  <<[ def ]>>\n" \
                   "  test\n" \
                   "  <<[ end ]>>"
        assert edit_block.get_code((-1, 0)) == expected
        expected = "  b\n" \
                   "  <<[ def ]>>\n" \
                   "  test\n" \
                   "  <<[ end ]>>"
        assert edit_block.get_code((1, 0)) == expected
        expected = "  a\n" \
                   "  b\n" \
                   "  <<[ def ]>>\n" \
                   "  test\n" \
                   "  <<[ end ]>>"
        assert edit_block.get_code((2, 0)) == expected
        expected = "  a\n" \
                   "  b\n" \
                   "  <<[ def ]>>\n" \
                   "  test\n" \
                   "  <<[ end ]>>"
        assert edit_block.get_code((3, 0)) == expected
        expected = "  <<[ def ]>>\n" \
                   "  test\n" \
                   "  <<[ end ]>>"
        assert edit_block.get_code((0, -1)) == expected
        expected = "  <<[ def ]>>\n" \
                   "  test\n" \
                   "  <<[ end ]>>\n" \
                   "  c"
        assert edit_block.get_code((0, 1)) == expected
        expected = "  <<[ def ]>>\n" \
                   "  test\n" \
                   "  <<[ end ]>>\n" \
                   "  c\n" \
                   "  d"
        assert edit_block.get_code((0, 2)) == expected
        expected = "  <<[ def ]>>\n" \
                   "  test\n" \
                   "  <<[ end ]>>\n" \
                   "  c\n" \
                   "  d"
        assert edit_block.get_code((0, 3)) == expected
        expected = "  b\n" \
                   "  <<[ def ]>>\n" \
                   "  test\n" \
                   "  <<[ end ]>>\n" \
                   "  c"
        assert edit_block.get_code((1, 1)) == expected

    def test_edit_blocks_get_code_2(self):
        input    = "  a\n" \
                   "  b\n" \
                   "  <<[ def ]>> test <<[ end ]>>\n" \
                   "  c\n" \
                   "  d"
        edit_blocks = autojinja.utils.edit_blocks_from_string(input)
        edit_block = edit_blocks["def"]
        expected = "  <<[ def ]>> test <<[ end ]>>"
        assert edit_block.get_code() == expected
        expected = "  <<[ def ]>> test <<[ end ]>>"
        assert edit_block.get_code((-1, 0)) == expected
        expected = "  b\n" \
                   "  <<[ def ]>> test <<[ end ]>>"
        assert edit_block.get_code((1, 0)) == expected
        expected = "  a\n" \
                   "  b\n" \
                   "  <<[ def ]>> test <<[ end ]>>"
        assert edit_block.get_code((2, 0)) == expected
        expected = "  a\n" \
                   "  b\n" \
                   "  <<[ def ]>> test <<[ end ]>>"
        assert edit_block.get_code((3, 0)) == expected
        expected = "  <<[ def ]>> test <<[ end ]>>"
        assert edit_block.get_code((0, -1)) == expected
        expected = "  <<[ def ]>> test <<[ end ]>>\n" \
                   "  c"
        assert edit_block.get_code((0, 1)) == expected
        expected = "  <<[ def ]>> test <<[ end ]>>\n" \
                   "  c\n" \
                   "  d"
        assert edit_block.get_code((0, 2)) == expected
        expected = "  <<[ def ]>> test <<[ end ]>>\n" \
                   "  c\n" \
                   "  d"
        assert edit_block.get_code((0, 3)) == expected
        expected = "  b\n" \
                   "  <<[ def ]>> test <<[ end ]>>\n" \
                   "  c"
        assert edit_block.get_code((1, 1)) == expected

    def test_edits_from_file(self):
        edits = autojinja.utils.edits_from_file(file3, settings2, encoding="ascii")
        assert len(edits) == 1
        assert edits["abc"] == "hello"

    def test_edits_from_string(self):
        with open(file3, 'r', encoding="ascii") as f:
            content = f.read()
        edits = autojinja.utils.edits_from_string(content, settings1)
        assert len(edits) == 1
        assert edits["abc"] == "hello"

    def test_append_envvars(self):
        env = {"VAR1" : "1",
               "VAR2" : "2"}
        values = ["VAR1=42",
                  "VAR3 = ${VAR1}",
                  "VAR4 = Test string \n",
                  "   VAR5 =Test string= "]
        autojinja.utils.parse_envvars(env, values)
        assert len(env) == 5
        assert env["VAR1"] == "42"
        assert env["VAR2"] == "2"
        assert env["VAR3"] == "42"
        assert env["VAR4"] == "Test string"
        assert env["VAR5"] == "Test string="

    def test_parse_envfile(self):
        env = {"VAR1" : "1",
               "VAR2" : "2"}
        autojinja.utils.parse_envfile(env, file4)
        assert len(env) == 5
        assert env["VAR1"] == "42"
        assert env["VAR2"] == "2"
        assert env["VAR3"] == "42"
        assert env["VAR4"] == "Test string"
        assert env["VAR5"] == autojinja.path.Path(file4).abspath.dirpath

    def test_evaluate(self):
        env = {"VAR1" : "1",
               "VAR2" : "2",
               "VAR3" : "VAR2"}
        assert autojinja.utils.evaluate_env(env, "${VAR1}") == "1"
        assert autojinja.utils.evaluate_env(env, "${VAR1}/test${VAR2}.py") == "1/test2.py"
        assert autojinja.utils.evaluate_env(env, "${VAR40}.txt") == "${VAR40}.txt"

    def test_os_pathsep(self):
        if os.name != "nt": # Unix
            assert autojinja.utils.os_pathsep("a;b;c") == ";"
            assert autojinja.utils.os_pathsep("a:b;c") == ":"
            assert autojinja.utils.os_pathsep("a;b:c") == ":"
            assert autojinja.utils.os_pathsep("a:b:c") == ":"
        else: # Windows
            assert autojinja.utils.os_pathsep("a;b;c") == ";"
            assert autojinja.utils.os_pathsep("a:b;c") == ";"
            assert autojinja.utils.os_pathsep("a;b:c") == ";"
            assert autojinja.utils.os_pathsep("a:b:c") == ";"
