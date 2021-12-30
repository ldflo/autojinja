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
root = autojinja.path[tmp.name]
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
            "   VAR5 =Test string= ")

class Test:
    def test_file_tagged(self):
        with open(file1, 'w') as f:
            f.write("import autojinja\n")
            f.write("\n")
        assert autojinja.utils.file_tagged(file1) == True
        with open(file1, 'w', encoding=None) as f:
            f.write("from autojinja import *\n")
            f.write("\n")
        assert autojinja.utils.file_tagged(file1, encoding=None) == True
        with open(file1, 'w', encoding="ascii") as f:
            f.write("autojinja\n")
            f.write("\n")
        assert autojinja.utils.file_tagged(file1, encoding="ascii") == True
        with open(file1, 'w', encoding="ascii") as f:
            f.write("import os.path\n")
            f.write("\n")
        assert autojinja.utils.file_tagged(file1, encoding="ascii") == False
        with open(file1, 'w', encoding="ascii") as f:
            f.write("\n")
            f.write("import autojinja\n")
        assert autojinja.utils.file_tagged(file1, encoding="ascii") == False

    def test_generate_file(self):
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
        assert len(object.edit_markers) == 1
        assert object.edit_markers["abc"].body == "    hello"
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
        assert len(object.edit_markers) == 1
        assert object.edit_markers["abc"].header == "abc"
        assert object.edit_markers["abc"].body == "    hello"
        assert len(object.edits) == 1
        assert object.edits["abc"] == "hello"

    def test_edit_markers_from_file(self):
        edit_markers = autojinja.utils.edit_markers_from_file(file3, settings1, encoding="ascii")
        assert len(edit_markers) == 1
        assert edit_markers["abc"].header == "abc"
        assert edit_markers["abc"].body == "    hello"

    def test_edit_markers_from_string(self):
        with open(file3, 'r', encoding="ascii") as f:
            content = f.read()
        edit_markers = autojinja.utils.edit_markers_from_string(content, None)
        assert len(edit_markers) == 1
        assert edit_markers["abc"].header == "abc"
        assert edit_markers["abc"].body == "    hello"

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
        assert env["VAR5"] == "Test string="

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
