from . import assert_exception

import autojinja
import os
import tempfile

def invalid_autojinja(exception_type: type, message: str, *args: str, **kwargs: str):
    def function(*args: str, **kwargs: str):
        autojinja.main(*args, **kwargs)
    assert_exception(function, exception_type, message, *args, **kwargs)

tmp = tempfile.TemporaryDirectory()
root = autojinja.path.DirPath(tmp.name)
output = root.join("output.txt")

def clear_output():
    if output.exists:
        os.remove(output)
def read_output():
    with open(output, 'r') as f:
        return f.read()

# TestSearch
dir1 = root.join("dir1/")
dir2 = root.join("dir1/dir2/")
file1 = root.join("script.py")
file2 = root.join("__jinja__.py")
file3 = root.join("dir1/script.py")
file4 = root.join("dir1/__jinja__.py")
file5 = root.join("dir1/dir2/script.py")
file6 = root.join("dir1/dir2/__jinja__.py")
file7 = root.join("faulty_script.py")
file8 = root.join("binary_script.py")
os.mkdir(dir1)
os.mkdir(dir2)
with open(file1, 'w') as f:
    f.write(f"# autojinja\n" \
            f"with open('{output}', 'a') as f:\n" \
            f"    f.write('file1\\n')\n")
with open(file2, 'w') as f:
    f.write(f"# tag\n" \
            f"with open('{output}', 'a') as f:\n" \
            f"    f.write('file2\\n')\n")
with open(file3, 'w') as f:
    f.write(f"# autojinja\n" \
            f"with open('{output}', 'a') as f:\n" \
            f"    f.write('file3\\n')\n")
with open(file4, 'w') as f:
    f.write(f"# tag\n" \
            f"with open('{output}', 'a') as f:\n" \
            f"    f.write('file4\\n')\n")
with open(file5, 'w') as f:
    f.write(f"# autojinja\n" \
            f"with open('{output}', 'a') as f:\n" \
            f"    f.write('file5\\n')\n")
with open(file6, 'w') as f:
    f.write(f"# tag\n" \
            f"with open('{output}', 'a') as f:\n" \
            f"    f.write('file6\\n')\n")
with open(file7, 'w') as f:
    f.write("raise Exception('faulty')\n")
with open(file8, 'w') as f:
    f.write("raise Exception('faulty')\n")

# TestEnv
file8 = root.join("script_env.py")
file9 = root.join("file.env")
with open(file8, 'w') as f:
    f.write(f"import os\n" \
            f"with open('{output}', 'a') as f:\n" \
            f"    if 'VAR1' in os.environ:\n" \
            f"        f.write(os.environ['VAR1'] + '\\n')\n" \
            f"    if 'VAR2' in os.environ:\n" \
            f"        f.write(os.environ['VAR2'] + '\\n')\n")
with open(file9, 'w') as f:
    f.write("VAR1=1\n" \
            "VAR2=2\n")

# TestIncludes
file10 = root.join("script_includes.py")
with open(file10, 'w') as f:
    f.write(f"import os\n" \
            f"with open('{output}', 'a') as f:\n" \
            f"    if 'PYTHONPATH' in os.environ:\n" \
            f"        f.write(os.environ['PYTHONPATH'] + '\\n')\n")

# TestRemoveMarkers
file11 = root.join("script_remove_markers.py")
with open(file11, 'w') as f:
    f.write(f"import os\n" \
            f"with open('{output}', 'a') as f:\n" \
            f"    if '{autojinja.defaults.AUTOJINJA_REMOVE_MARKERS}' in os.environ:\n" \
            f"        f.write(os.environ['{autojinja.defaults.AUTOJINJA_REMOVE_MARKERS}'] + '\\n')\n")

# TestSilent
file12 = root.join("script_silent.py")
with open(file12, 'w') as f:
    f.write(f"import os\n" \
            f"with open('{output}', 'a') as f:\n" \
            f"    if '{autojinja.defaults.AUTOJINJA_SILENT}' in os.environ:\n" \
            f"        f.write(os.environ['{autojinja.defaults.AUTOJINJA_SILENT}'] + '\\n')\n")
file13 = root.join("script_silent_faulty.py")
with open(file13, 'w') as f:
    f.write(f"import sys\n" \
            f"sys.stderr.write(\"error1\\n\")\n" \
            f"sys.stdout.write(\"print1\\n\")\n" \
            f"sys.stderr.write(\"error2\\n\")\n" \
            f"sys.stdout.write(\"print2\\n\")\n" \
            f"raise Exception(\"Error\")\n")

# TestDebug
file14 = root.join("script_debug.py")
with open(file14, 'w') as f:
    f.write(f"import os\n" \
            f"with open('{output}', 'a') as f:\n" \
            f"    if '{autojinja.defaults.AUTOJINJA_DEBUG}' in os.environ:\n" \
            f"        f.write(os.environ['{autojinja.defaults.AUTOJINJA_DEBUG}'] + '\\n')\n")

# TestSummary
file15 = root.join("script_summary.py")
with open(file15, 'w') as f:
    f.write(f"import os\n" \
            f"with open('{output}', 'a') as f:\n" \
            f"    if '{autojinja.defaults.AUTOJINJA_SUMMARY}' in os.environ:\n" \
            f"        f.write(os.environ['{autojinja.defaults.AUTOJINJA_SUMMARY}'] + '\\n')\n")

class TestVersion:
    def test_1(self):
        assert autojinja.__version__ == "1.10.0"

class TestSearch:
    def test_1(self):
        clear_output()
        autojinja.main(file1, file2, file3, file4, file5, file6)
        assert read_output() == "file1\nfile2\nfile3\nfile4\nfile5\nfile6\n"

    # Search filename
    def test_2(self):
        clear_output()
        autojinja.main("-f", root)
        assert read_output() == "file2\n"

    def test_3(self):
        clear_output()
        autojinja.main("-fr", root)
        assert read_output() == "file2\nfile4\nfile6\n"

    def test_4(self):
        clear_output()
        autojinja.main("--search-filename", "--filename", "script.py", root)
        assert read_output() == "file1\n"

    def test_5(self):
        clear_output()
        autojinja.main("--search-filename", "--recursive", "--filename", "script.py", root)
        assert read_output() == "file1\nfile3\nfile5\n"

    # Search tag
    def test_6(self):
        clear_output()
        autojinja.main("-t", root)
        assert read_output() == "file1\n"

    def test_7(self):
        clear_output()
        autojinja.main("-tr", root)
        assert read_output() == "file1\nfile3\nfile5\n"

    def test_8(self):
        clear_output()
        autojinja.main("--search-tag", "--tag", "tag", root)
        assert read_output() == "file2\n"

    def test_9(self):
        clear_output()
        autojinja.main("--search-tag", "-r", "--tag", "tag", root)
        assert read_output() == "file2\nfile4\nfile6\n"

    # Search all
    def test_10(self):
        clear_output()
        autojinja.main("-ftr", "--filename", "script.py", "--tag", "tag", root)
        assert read_output() == "file1\nfile2\nfile3\nfile4\nfile5\nfile6\n"

    def test_11(self):
        clear_output()
        autojinja.main("-a", "--filename", "script.py", "--tag", "tag", root)
        assert read_output() == "file1\nfile2\nfile3\nfile4\nfile5\nfile6\n"

    def test_12(self):
        clear_output()
        autojinja.main("--all", "--filename", "script.py", "--tag", "tag", root)
        assert read_output() == "file1\nfile2\nfile3\nfile4\nfile5\nfile6\n"

    # Exception
    def test_13(self):
        message = "Directory arguments require '--search-filename' or '--search-tag'"
        invalid_autojinja(Exception, message, ".")

    def test_14(self):
        file = autojinja.path.Path("script.py")
        message = f"File or directory at path \"{file.abspath}\" doesn't exist"
        invalid_autojinja(Exception, message, file)

    def test_15(self):
        dir = autojinja.path.DirPath("dir")
        message = f"File or directory at path \"{dir.abspath}\" doesn't exist"
        invalid_autojinja(Exception, message, dir)

    def test_16(self):
        message = f"File at path \"{output.abspath}\" is not a python script (.py extension)"
        invalid_autojinja(Exception, message, output)

    def test_17(self):
        message = f"Error 1 while executing script at path \"{file7.abspath}\""
        invalid_autojinja(Exception, message, file7)

class TestEnv:
    def test_1(self):
        clear_output()
        autojinja.main("--env", "VAR1=1", file8)
        assert read_output() == "1\n"

    def test_2(self):
        clear_output()
        os.environ["VAR2"] = "0"
        autojinja.main("--env=VAR1=1", file8)
        assert read_output() == "1\n0\n"
        del os.environ["VAR2"]

    def test_3(self):
        clear_output()
        os.environ["VAR2"] = "0"
        autojinja.main("-e", "VAR1=1", file8)
        assert read_output() == "1\n0\n"
        del os.environ["VAR2"]

    def test_4(self):
        clear_output()
        autojinja.main("-e", "VAR1=1", "-e", "VAR2=2", file8)
        assert read_output() == "1\n2\n"

    def test_5(self):
        clear_output()
        os.environ["VAR2"] = "0"
        autojinja.main("-e", file9, file8)
        assert read_output() == "1\n2\n"
        del os.environ["VAR2"]

class TestIncludes:
    def test_1(self):
        clear_output()
        autojinja.main("--includes", dir1, file10)
        assert read_output() == f"{dir1}\n"

    def test_2(self):
        clear_output()
        autojinja.main(f"--includes={dir1}", file10)
        assert read_output() == f"{dir1}\n"

    def test_3(self):
        clear_output()
        autojinja.main("-i", dir1, file10)
        assert read_output() == f"{dir1}\n"

    def test_4(self):
        clear_output()
        autojinja.main(f"-i={dir1}", file10)
        assert read_output() == f"{dir1}\n"

    def test_5(self):
        clear_output()
        os.environ["PYTHONPATH"] = "test"
        autojinja.main("-i", dir1, "-i", dir2, file10)
        assert read_output() == f"test;{dir1};{dir2}\n"
        del os.environ["PYTHONPATH"]

    def test_6(self):
        clear_output()
        os.environ["PYTHONPATH"] = "test"
        autojinja.main("-i", f"{dir1};{dir2}", file10)
        assert read_output() == f"test;{dir1};{dir2}\n"
        del os.environ["PYTHONPATH"]

class TestRemoveMarkers:
    def test_1(self):
        clear_output()
        autojinja.main(file11)
        assert read_output() == f"0\n"

    def test_2(self):
        clear_output()
        autojinja.main("--remove-markers", "0", file11)
        assert read_output() == f"0\n"

    def test_3(self):
        clear_output()
        autojinja.main("--remove-markers", "1", file11)
        assert read_output() == f"1\n"

    def test_4(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_REMOVE_MARKERS] = "0"
        autojinja.main(file11)
        assert read_output() == f"0\n"
        del os.environ[autojinja.defaults.AUTOJINJA_REMOVE_MARKERS]

    def test_5(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_REMOVE_MARKERS] = "0"
        autojinja.main("--remove-markers", "0", file11)
        assert read_output() == f"0\n"
        del os.environ[autojinja.defaults.AUTOJINJA_REMOVE_MARKERS]

    def test_6(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_REMOVE_MARKERS] = "0"
        autojinja.main("--remove-markers", "1", file11)
        assert read_output() == f"1\n"
        del os.environ[autojinja.defaults.AUTOJINJA_REMOVE_MARKERS]

    def test_7(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_REMOVE_MARKERS] = "1"
        autojinja.main(file11)
        assert read_output() == f"1\n"
        del os.environ[autojinja.defaults.AUTOJINJA_REMOVE_MARKERS]

    def test_8(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_REMOVE_MARKERS] = "1"
        autojinja.main("--remove-markers", "0", file11)
        assert read_output() == f"0\n"
        del os.environ[autojinja.defaults.AUTOJINJA_REMOVE_MARKERS]

    def test_9(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_REMOVE_MARKERS] = "1"
        autojinja.main("--remove-markers", "1", file11)
        assert read_output() == f"1\n"
        del os.environ[autojinja.defaults.AUTOJINJA_REMOVE_MARKERS]

    def test_10(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_REMOVE_MARKERS] = "0"
        autojinja.main("--env", f"{autojinja.defaults.AUTOJINJA_REMOVE_MARKERS}=1", file11)
        assert read_output() == f"1\n"
        del os.environ[autojinja.defaults.AUTOJINJA_REMOVE_MARKERS]

    def test_11(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_REMOVE_MARKERS] = "0"
        autojinja.main("--remove-markers", "1", "--env", f"{autojinja.defaults.AUTOJINJA_REMOVE_MARKERS}=0", file11)
        assert read_output() == f"1\n"
        del os.environ[autojinja.defaults.AUTOJINJA_REMOVE_MARKERS]

    def test_12(self):
        os.environ[autojinja.defaults.AUTOJINJA_REMOVE_MARKERS] = "abc"
        message = f"Expected 0 or 1 for environment variable '{autojinja.defaults.AUTOJINJA_REMOVE_MARKERS}'"
        invalid_autojinja(Exception, message, file11)
        del os.environ[autojinja.defaults.AUTOJINJA_REMOVE_MARKERS]

    def test_13(self):
        os.environ[autojinja.defaults.AUTOJINJA_REMOVE_MARKERS] = "abc"
        message = f"Expected 0 or 1 for environment variable '{autojinja.defaults.AUTOJINJA_REMOVE_MARKERS}'"
        assert_exception(lambda: autojinja.ParserSettings(), Exception, message)
        del os.environ[autojinja.defaults.AUTOJINJA_REMOVE_MARKERS]

class TestSilent:
    def test_1(self):
        clear_output()
        autojinja.main(file12)
        assert read_output() == f"0\n"

    def test_2(self):
        clear_output()
        autojinja.main("--silent", file12)
        assert read_output() == f"1\n"

    def test_3(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_SILENT] = "0"
        autojinja.main(file12)
        assert read_output() == f"0\n"
        del os.environ[autojinja.defaults.AUTOJINJA_SILENT]

    def test_4(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_SILENT] = "1"
        autojinja.main(file12)
        assert read_output() == f"1\n"
        del os.environ[autojinja.defaults.AUTOJINJA_SILENT]

    def test_5(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_SILENT] = "0"
        autojinja.main("--silent", file12)
        assert read_output() == f"1\n"
        del os.environ[autojinja.defaults.AUTOJINJA_SILENT]

    def test_6(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_SILENT] = "1"
        autojinja.main("--silent", file12)
        assert read_output() == f"1\n"
        del os.environ[autojinja.defaults.AUTOJINJA_SILENT]

    def test_7(self):
        os.environ[autojinja.defaults.AUTOJINJA_SILENT] = "abc"
        message = f"Expected 0 or 1 for environment variable '{autojinja.defaults.AUTOJINJA_SILENT}'"
        invalid_autojinja(Exception, message, file12)
        del os.environ[autojinja.defaults.AUTOJINJA_SILENT]

    def test_8(self):
        os.environ[autojinja.defaults.AUTOJINJA_SILENT] = "1"
        message_start = f"error1\nprint1\nerror2\nprint2\n"
        message_end = f"Error 1 while executing script at path \"{file13}\""
        try:
            autojinja.main(file13)
        except Exception as e:
            exception = e
        else:
            exception = None
        assert str(exception).startswith(message_start) == True
        assert str(exception).endswith(message_end) == True
        del os.environ[autojinja.defaults.AUTOJINJA_SILENT]

class TestDebug:
    def test_1(self):
        clear_output()
        autojinja.main(file14)
        assert read_output() == f"0\n"

    def test_2(self):
        clear_output()
        autojinja.main("--debug", file14)
        assert read_output() == f"1\n"

    def test_3(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_DEBUG] = "0"
        autojinja.main(file14)
        assert read_output() == f"0\n"
        del os.environ[autojinja.defaults.AUTOJINJA_DEBUG]

    def test_4(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_DEBUG] = "0"
        autojinja.main("--debug", file14)
        assert read_output() == f"1\n"
        del os.environ[autojinja.defaults.AUTOJINJA_DEBUG]

    def test_5(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_DEBUG] = "1"
        autojinja.main(file14)
        assert read_output() == f"1\n"
        del os.environ[autojinja.defaults.AUTOJINJA_DEBUG]

    def test_6(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_DEBUG] = "1"
        autojinja.main("--debug", file14)
        assert read_output() == f"1\n"
        del os.environ[autojinja.defaults.AUTOJINJA_DEBUG]

    def test_7(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_DEBUG] = "0"
        autojinja.main("--env", f"{autojinja.defaults.AUTOJINJA_DEBUG}=1", file14)
        assert read_output() == f"1\n"
        del os.environ[autojinja.defaults.AUTOJINJA_DEBUG]

    def test_8(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_DEBUG] = "0"
        autojinja.main("--debug", "--env", f"{autojinja.defaults.AUTOJINJA_DEBUG}=0", file14)
        assert read_output() == f"1\n"
        del os.environ[autojinja.defaults.AUTOJINJA_DEBUG]

    def test_9(self):
        os.environ[autojinja.defaults.AUTOJINJA_DEBUG] = "abc"
        message = f"Expected 0 or 1 for environment variable '{autojinja.defaults.AUTOJINJA_DEBUG}'"
        invalid_autojinja(Exception, message, file14)
        del os.environ[autojinja.defaults.AUTOJINJA_DEBUG]

class TestSummary:
    def test_1(self):
        clear_output()
        autojinja.main(file15)
        assert read_output() == f"1\n"

    def test_2(self):
        clear_output()
        autojinja.main("--summary", "0", file15)
        assert read_output() == f"0\n"

    def test_3(self):
        clear_output()
        autojinja.main("--summary", "1", file15)
        assert read_output() == f"1\n"

    def test_4(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_SUMMARY] = "0"
        autojinja.main(file15)
        assert read_output() == f"0\n"
        del os.environ[autojinja.defaults.AUTOJINJA_SUMMARY]

    def test_5(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_SUMMARY] = "0"
        autojinja.main("--summary", "0", file15)
        assert read_output() == f"0\n"
        del os.environ[autojinja.defaults.AUTOJINJA_SUMMARY]

    def test_6(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_SUMMARY] = "1"
        autojinja.main("--summary", "1", file15)
        assert read_output() == f"1\n"
        del os.environ[autojinja.defaults.AUTOJINJA_SUMMARY]

    def test_7(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_SUMMARY] = "1"
        autojinja.main("--summary", "0", file15)
        assert read_output() == f"0\n"
        del os.environ[autojinja.defaults.AUTOJINJA_SUMMARY]

    def test_8(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_SUMMARY] = "0"
        autojinja.main("--summary", "1", file15)
        assert read_output() == f"1\n"
        del os.environ[autojinja.defaults.AUTOJINJA_SUMMARY]

    def test_9(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_SUMMARY] = "0"
        autojinja.main("--env", f"{autojinja.defaults.AUTOJINJA_SUMMARY}=1", file15)
        assert read_output() == f"1\n"
        del os.environ[autojinja.defaults.AUTOJINJA_SUMMARY]

    def test_10(self):
        clear_output()
        os.environ[autojinja.defaults.AUTOJINJA_SUMMARY] = "0"
        autojinja.main("--summary", "1", "--env", f"{autojinja.defaults.AUTOJINJA_SUMMARY}=0", file15)
        assert read_output() == f"1\n"
        del os.environ[autojinja.defaults.AUTOJINJA_SUMMARY]

    def test_12(self):
        clear_output()
        autojinja.main("--summary", "111", file15)
        assert read_output() == f"111\n"

    def test_13(self):
        os.environ[autojinja.defaults.AUTOJINJA_SUMMARY] = "abc"
        message = f"Expected 0, 1 or flags for environment variable '{autojinja.defaults.AUTOJINJA_SUMMARY}'"
        invalid_autojinja(Exception, message, file15)
        del os.environ[autojinja.defaults.AUTOJINJA_SUMMARY]

    def test_14(self):
        os.environ[autojinja.defaults.AUTOJINJA_SUMMARY] = "222"
        message = f"Expected 0, 1 or flags for environment variable '{autojinja.defaults.AUTOJINJA_SUMMARY}'"
        invalid_autojinja(Exception, message, file15)
        del os.environ[autojinja.defaults.AUTOJINJA_SUMMARY]

    def test_15(self):
        os.environ[autojinja.defaults.AUTOJINJA_SUMMARY] = "222"
        message = f"Expected 0, 1 or flags for environment variable '{autojinja.defaults.AUTOJINJA_SUMMARY}'"
        assert_exception(lambda: autojinja.utils.generate_file(output, ""), Exception, message)
        del os.environ[autojinja.defaults.AUTOJINJA_SUMMARY]
