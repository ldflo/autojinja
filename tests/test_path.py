import autojinja
import os
import tempfile

tmp = tempfile.TemporaryDirectory()
root = autojinja.Path[tmp.name]
dir1 = root.join("dir1/")
dir2 = root.join("dir1/dir2/")
file1 = root.join("file1.txt")
file2 = root.join("file2.txt.ext")
file3 = root.join("dir1\\file3.txt")
file4 = root.join("dir1/dir2\\file4.txt.ext")
os.mkdir(dir1)
os.mkdir(dir2)
open(file1, 'w')
open(file2, 'w')
open(file3, 'w')
open(file4, 'w')

class Test:
    def test_join(self):
        assert autojinja.path.join("", "file.txt")            == "file.txt"
        assert autojinja.path.join("/", "file.txt")           == "/file.txt"
        assert autojinja.path.join("C:/", "file.txt")         == "C:/file.txt"
        assert autojinja.path.join("/dir1", "file.txt")       == "/dir1/file.txt"
        assert autojinja.path.join("\\dir1/", "file.txt")     == "/dir1/file.txt"
        assert autojinja.path.join("/dir1\\dir2", "file.txt") == "/dir1/dir2/file.txt"

    def test_join_brackets(self):
        assert autojinja.path.join["file.txt"]                == "file.txt/"
        assert autojinja.path.join["", "file.txt"]            == "file.txt/"
        assert autojinja.path.join["/", "file.txt"]           == "/file.txt/"
        assert autojinja.path.join["C:/", "file.txt"]         == "C:/file.txt/"
        assert autojinja.path.join["/dir1", "file.txt"]       == "/dir1/file.txt/"
        assert autojinja.path.join["\\dir1/", "file.txt"]     == "/dir1/file.txt/"
        assert autojinja.path.join["/dir1\\dir2", "file.txt"] == "/dir1/dir2/file.txt/"

    def test_add(self):
        assert autojinja.path.add("", "file.txt")            == "file.txt"
        assert autojinja.path.add("/", "file.txt")           == "/file.txt"
        assert autojinja.path.add("C:/", "file.txt")         == "C:/file.txt"
        assert autojinja.path.add("\\dir1", "file.txt")      == "/dir1file.txt"
        assert autojinja.path.add("/dir1/", "file.txt")      == "/dir1/file.txt"
        assert autojinja.path.add("/dir1\\dir2", "file.txt") == "/dir1/dir2file.txt"

    def test_files(self):
        # dir
        values = autojinja.path.files(root, "**")
        assert len(values) == 4
        assert file1 in values
        assert file2 in values
        assert file3 in values
        assert file4 in values
        values = autojinja.path.files(dir1, "**")
        assert len(values) == 2
        assert file3 in values
        assert file4 in values
        values = autojinja.path.files(dir2, "**")
        assert len(values) == 1
        assert file4 in values
        values = autojinja.path.files(root, "*.ext")
        assert len(values) == 1
        assert file2 in values
        values = autojinja.path.files(root, "**/*.ext")
        assert len(values) == 2
        assert file2 in values
        assert file4 in values
        # file
        values = autojinja.path.files(file1, "**")
        assert len(values) == 4
        assert file1 in values
        assert file2 in values
        assert file3 in values
        assert file4 in values
        values = autojinja.path.files(file3, "**")
        assert len(values) == 2
        assert file3 in values
        assert file4 in values
        values = autojinja.path.files(file4, "**")
        assert len(values) == 1
        assert file4 in values
        values = autojinja.path.files(file2, "*.ext")
        assert len(values) == 1
        assert file2 in values
        values = autojinja.path.files(file2, "**/*.ext")
        assert len(values) == 2
        assert file2 in values
        assert file4 in values

    def test_dirs(self):
        # dir
        values = autojinja.path.dirs(root, "**")
        assert len(values) == 3
        assert root == values[0]
        assert dir1 in values
        assert dir2 in values
        values = autojinja.path.dirs(dir1, "**")
        assert len(values) == 2
        assert dir1 == values[0]
        assert dir2 in values
        values = autojinja.path.dirs(dir2, "**")
        assert len(values) == 1
        assert dir2 == values[0]
        # file
        values = autojinja.path.dirs(file2, "**")
        assert len(values) == 3
        assert root == values[0]
        assert dir1 in values
        assert dir2 in values
        values = autojinja.path.dirs(file3, "**")
        assert len(values) == 2
        assert dir1 == values[0]
        assert dir2 in values
        values = autojinja.path.dirs(file4, "**")
        assert len(values) == 1
        assert dir2 == values[0]

    def test_filepath(self):
        assert autojinja.path.filepath("")                     == ""
        assert autojinja.path.filepath("file.txt")             == "file.txt"
        assert autojinja.path.filepath("/file.txt")            == "/file.txt"
        assert autojinja.path.filepath("C:/")                  == "C:/"
        assert autojinja.path.filepath("\\")                   == "/"
        assert autojinja.path.filepath("/dir1\\")              == "/dir1/"
        assert autojinja.path.filepath("/dir1/file.txt")       == "/dir1/file.txt"
        assert autojinja.path.filepath("/dir1\\dir2/file.txt") == "/dir1/dir2/file.txt"

    def test_filename(self):
        assert autojinja.path.filename("")                     == ""
        assert autojinja.path.filename("file.txt")             == "file.txt"
        assert autojinja.path.filename("/file.txt")            == "file.txt"
        assert autojinja.path.filename("C:/")                  == ""
        assert autojinja.path.filename("\\")                   == ""
        assert autojinja.path.filename("/dir1\\")              == ""
        assert autojinja.path.filename("/dir1/file.txt")       == "file.txt"
        assert autojinja.path.filename("/dir1\\dir2/file.txt") == "file.txt"

    def test_set_filename(self):
        assert autojinja.path.set_filename("", "new.md")                     == "new.md"
        assert autojinja.path.set_filename("file.txt", "new.md")             == "new.md"
        assert autojinja.path.set_filename("/", "new.md")                    == "/new.md"
        assert autojinja.path.set_filename("C:/", "new.md")                  == "C:/new.md"
        assert autojinja.path.set_filename("\\", "new.md")                   == "/new.md"
        assert autojinja.path.set_filename("/dir1\\", "new.md")              == "/dir1/new.md"
        assert autojinja.path.set_filename("/dir1/file.txt", "new.md")       == "/dir1/new.md"
        assert autojinja.path.set_filename("/dir1\\dir2/file.txt", "new.md") == "/dir1/dir2/new.md"

    def test_dirpath(self):
        if os.name != "nt": # Unix
            assert autojinja.path.dirpath("")                     == ""
            assert autojinja.path.dirpath("file.txt")             == ""
            assert autojinja.path.dirpath("/file.txt")            == "/"
            assert autojinja.path.dirpath("C:")                   == ""
            assert autojinja.path.dirpath("C:/")                  == "C:/"
            assert autojinja.path.dirpath("/")                    == "/"
            assert autojinja.path.dirpath("\\")                   == "/"
            assert autojinja.path.dirpath("/dir1")                == "/"
            assert autojinja.path.dirpath("/dir1/")               == "/dir1/"
            assert autojinja.path.dirpath("/dir1\\ab")            == "/dir1/"
            assert autojinja.path.dirpath("/dir1/file.txt")       == "/dir1/"
            assert autojinja.path.dirpath("/dir1\\dir2/file.txt") == "/dir1/dir2/"
        else: # Windows
            assert autojinja.path.dirpath("")                     == ""
            assert autojinja.path.dirpath("file.txt")             == ""
            assert autojinja.path.dirpath("/file.txt")            == "/"
            assert autojinja.path.dirpath("C:")                   == "C:/"
            assert autojinja.path.dirpath("C:/")                  == "C:/"
            assert autojinja.path.dirpath("/")                    == "/"
            assert autojinja.path.dirpath("\\")                   == "/"
            assert autojinja.path.dirpath("/dir1")                == "/"
            assert autojinja.path.dirpath("/dir1/")               == "/dir1/"
            assert autojinja.path.dirpath("/dir1\\ab")            == "/dir1/"
            assert autojinja.path.dirpath("/dir1/file.txt")       == "/dir1/"
            assert autojinja.path.dirpath("/dir1\\dir2/file.txt") == "/dir1/dir2/"

    def test_dirname(self):
        if os.name != "nt": # Unix
            assert autojinja.path.dirname("")                     == ""
            assert autojinja.path.dirname("file.txt")             == ""
            assert autojinja.path.dirname("/file.txt")            == ""
            assert autojinja.path.dirname("C:")                   == ""
            assert autojinja.path.dirname("C:/")                  == "C:"
            assert autojinja.path.dirname("/")                    == ""
            assert autojinja.path.dirname("\\")                   == ""
            assert autojinja.path.dirname("/dir1")                == ""
            assert autojinja.path.dirname("/dir1/")               == "dir1"
            assert autojinja.path.dirname("/dir1\\")              == "dir1"
            assert autojinja.path.dirname("/dir1/file.txt")       == "dir1"
            assert autojinja.path.dirname("/dir1\\dir2/file.txt") == "dir2"
        else: # Windows
            assert autojinja.path.dirname("")                     == ""
            assert autojinja.path.dirname("file.txt")             == ""
            assert autojinja.path.dirname("/file.txt")            == ""
            assert autojinja.path.dirname("C:")                   == "C:"
            assert autojinja.path.dirname("C:/")                  == "C:"
            assert autojinja.path.dirname("/")                    == ""
            assert autojinja.path.dirname("\\")                   == ""
            assert autojinja.path.dirname("/dir1")                == ""
            assert autojinja.path.dirname("/dir1/")               == "dir1"
            assert autojinja.path.dirname("/dir1\\")              == "dir1"
            assert autojinja.path.dirname("/dir1/file.txt")       == "dir1"
            assert autojinja.path.dirname("/dir1\\dir2/file.txt") == "dir2"

    def test_parent_dirpath(self):
        if os.name != "nt": # Unix
            assert autojinja.path.parent_dirpath("")                     == ""
            assert autojinja.path.parent_dirpath("file.txt")             == ""
            assert autojinja.path.parent_dirpath("/file.txt")            == "/"
            assert autojinja.path.parent_dirpath("C:")                   == ""
            assert autojinja.path.parent_dirpath("C:/")                  == ""
            assert autojinja.path.parent_dirpath("/")                    == "/"
            assert autojinja.path.parent_dirpath("\\")                   == "/"
            assert autojinja.path.parent_dirpath("/dir1")                == "/"
            assert autojinja.path.parent_dirpath("/dir1/")               == "/"
            assert autojinja.path.parent_dirpath("/dir1\\")              == "/"
            assert autojinja.path.parent_dirpath("/dir1/file.txt")       == "/"
            assert autojinja.path.parent_dirpath("/dir1\\dir2/file.txt") == "/dir1/"
        else: # Windows
            assert autojinja.path.parent_dirpath("")                     == ""
            assert autojinja.path.parent_dirpath("file.txt")             == ""
            assert autojinja.path.parent_dirpath("/file.txt")            == "/"
            assert autojinja.path.parent_dirpath("C:")                   == "C:/"
            assert autojinja.path.parent_dirpath("C:/")                  == "C:/"
            assert autojinja.path.parent_dirpath("/")                    == "/"
            assert autojinja.path.parent_dirpath("\\")                   == "/"
            assert autojinja.path.parent_dirpath("/dir1")                == "/"
            assert autojinja.path.parent_dirpath("/dir1/")               == "/"
            assert autojinja.path.parent_dirpath("/dir1\\")              == "/"
            assert autojinja.path.parent_dirpath("/dir1/file.txt")       == "/"
            assert autojinja.path.parent_dirpath("/dir1\\dir2/file.txt") == "/dir1/"

    def test_parent_dirname(self):
        if os.name != "nt": # Unix
            assert autojinja.path.parent_dirname("")                     == ""
            assert autojinja.path.parent_dirname("file.txt")             == ""
            assert autojinja.path.parent_dirname("/file.txt")            == ""
            assert autojinja.path.parent_dirname("C:")                   == ""
            assert autojinja.path.parent_dirname("C:/")                  == ""
            assert autojinja.path.parent_dirname("/")                    == ""
            assert autojinja.path.parent_dirname("\\")                   == ""
            assert autojinja.path.parent_dirname("/dir1")                == ""
            assert autojinja.path.parent_dirname("/dir1/")               == ""
            assert autojinja.path.parent_dirname("/dir1\\")              == ""
            assert autojinja.path.parent_dirname("/dir1/file.txt")       == ""
            assert autojinja.path.parent_dirname("/dir1\\dir2/file.txt") == "dir1"
        else: # Windows
            assert autojinja.path.parent_dirname("")                     == ""
            assert autojinja.path.parent_dirname("file.txt")             == ""
            assert autojinja.path.parent_dirname("/file.txt")            == ""
            assert autojinja.path.parent_dirname("C:")                   == "C:"
            assert autojinja.path.parent_dirname("C:/")                  == "C:"
            assert autojinja.path.parent_dirname("/")                    == ""
            assert autojinja.path.parent_dirname("\\")                   == ""
            assert autojinja.path.parent_dirname("/dir1")                == ""
            assert autojinja.path.parent_dirname("/dir1/")               == ""
            assert autojinja.path.parent_dirname("/dir1\\")              == ""
            assert autojinja.path.parent_dirname("/dir1/file.txt")       == ""
            assert autojinja.path.parent_dirname("/dir1\\dir2/file.txt") == "dir1"

    def test_ext(self):
        assert autojinja.path.ext("")                     == ""
        assert autojinja.path.ext("file.ext.txt")         == ".txt"
        assert autojinja.path.ext("/file.ext.txt")        == ".txt"
        assert autojinja.path.ext("C:/")                  == ""
        assert autojinja.path.ext("\\")                   == ""
        assert autojinja.path.ext("/dir1")                == ""
        assert autojinja.path.ext("/dir1\\")              == ""
        assert autojinja.path.ext("/dir1/file")           == ""
        assert autojinja.path.ext("/dir1\\dir2/file.txt") == ".txt"

    def test_set_ext(self):
        assert autojinja.path.set_ext("", ".md")                     == ".md"
        assert autojinja.path.set_ext("file.ext.txt", ".md")         == "file.ext.md"
        assert autojinja.path.set_ext("/file.ext.txt", ".md")        == "/file.ext.md"
        assert autojinja.path.set_ext("C:/", ".md")                  == "C:/.md"
        assert autojinja.path.set_ext("\\", ".md")                   == "/.md"
        assert autojinja.path.set_ext("/dir1", ".md")                == "/dir1.md"
        assert autojinja.path.set_ext("/dir1\\", ".md")              == "/dir1/.md"
        assert autojinja.path.set_ext("/dir1/file", ".md")           == "/dir1/file.md"
        assert autojinja.path.set_ext("/dir1\\dir2/file.txt", ".md") == "/dir1/dir2/file.md"

    def test_no_ext(self):
        assert autojinja.path.no_ext("")                     == ""
        assert autojinja.path.no_ext("file.txt")             == "file"
        assert autojinja.path.no_ext("/file.txt")            == "/file"
        assert autojinja.path.no_ext("/file.ext.txt")        == "/file.ext"
        assert autojinja.path.no_ext("C:/")                  == "C:/"
        assert autojinja.path.no_ext("\\")                   == "/"
        assert autojinja.path.no_ext("/dir1")                == "/dir1"
        assert autojinja.path.no_ext("/dir1\\")              == "/dir1/"
        assert autojinja.path.no_ext("/dir1/file")           == "/dir1/file"
        assert autojinja.path.no_ext("/dir1\\dir2/file.txt") == "/dir1/dir2/file"

    def test_fullext(self):
        assert autojinja.path.fullext("")                     == ""
        assert autojinja.path.fullext("file.ext.txt")         == ".ext.txt"
        assert autojinja.path.fullext("/file.ext.txt")        == ".ext.txt"
        assert autojinja.path.fullext("C:/")                  == ""
        assert autojinja.path.fullext("\\")                   == ""
        assert autojinja.path.fullext("/dir1")                == ""
        assert autojinja.path.fullext("/dir1\\")              == ""
        assert autojinja.path.fullext("/dir1/file")           == ""
        assert autojinja.path.fullext("/dir1\\dir2/file.txt") == ".txt"

    def test_set_fullext(self):
        assert autojinja.path.set_fullext("", ".md")                     == ".md"
        assert autojinja.path.set_fullext("file.ext.txt", ".md")         == "file.md"
        assert autojinja.path.set_fullext("/file.ext.txt", ".md")        == "/file.md"
        assert autojinja.path.set_fullext("C:/", ".md")                  == "C:/.md"
        assert autojinja.path.set_fullext("\\", ".md")                   == "/.md"
        assert autojinja.path.set_fullext("/dir1", ".md")                == "/dir1.md"
        assert autojinja.path.set_fullext("/dir1\\", ".md")              == "/dir1/.md"
        assert autojinja.path.set_fullext("/dir1/file", ".md")           == "/dir1/file.md"
        assert autojinja.path.set_fullext("/dir1\\dir2/file.txt", ".md") == "/dir1/dir2/file.md"

    def test_no_fullext(self):
        assert autojinja.path.no_fullext("")                     == ""
        assert autojinja.path.no_fullext("file.txt")             == "file"
        assert autojinja.path.no_fullext("/file.txt")            == "/file"
        assert autojinja.path.no_fullext("/file.ext.txt")        == "/file"
        assert autojinja.path.no_fullext("C:/")                  == "C:/"
        assert autojinja.path.no_fullext("\\")                   == "/"
        assert autojinja.path.no_fullext("/dir1")                == "/dir1"
        assert autojinja.path.no_fullext("/dir1\\")              == "/dir1/"
        assert autojinja.path.no_fullext("/dir1/file")           == "/dir1/file"
        assert autojinja.path.no_fullext("/dir1\\dir2/file.txt") == "/dir1/dir2/file"

    def test_slash(self):
        assert autojinja.path.slash("")                     == "/"
        assert autojinja.path.slash("file.txt")             == "file.txt/"
        assert autojinja.path.slash("/file.txt")            == "/file.txt/"
        assert autojinja.path.slash("C:/")                  == "C:/"
        assert autojinja.path.slash("\\")                   == "/"
        assert autojinja.path.slash("/dir1")                == "/dir1/"
        assert autojinja.path.slash("/dir1\\")              == "/dir1/"
        assert autojinja.path.slash("/dir1/file.txt")       == "/dir1/file.txt/"
        assert autojinja.path.slash("/dir1\\dir2/file.txt") == "/dir1/dir2/file.txt/"

    def test_no_slash(self):
        assert autojinja.path.no_slash("")                     == ""
        assert autojinja.path.no_slash("file.txt")             == "file.txt"
        assert autojinja.path.no_slash("/file.txt")            == "/file.txt"
        assert autojinja.path.no_slash("C:/")                  == "C:"
        assert autojinja.path.no_slash("\\")                   == ""
        assert autojinja.path.no_slash("/dir1")                == "/dir1"
        assert autojinja.path.no_slash("/dir1\\")              == "/dir1"
        assert autojinja.path.no_slash("/dir1/file.txt")       == "/dir1/file.txt"
        assert autojinja.path.no_slash("/dir1\\dir2/file.txt") == "/dir1/dir2/file.txt"

    def test_no_antislash(self):
        assert autojinja.path.no_antislash("")                     == ""
        assert autojinja.path.no_antislash("file.txt")             == "file.txt"
        assert autojinja.path.no_antislash("/file.txt")            == "/file.txt"
        assert autojinja.path.no_antislash("C:/")                  == "C:/"
        assert autojinja.path.no_antislash("\\")                   == "/"
        assert autojinja.path.no_antislash("/dir1")                == "/dir1"
        assert autojinja.path.no_antislash("/dir1\\")              == "/dir1/"
        assert autojinja.path.no_antislash("/dir1/file.txt")       == "/dir1/file.txt"
        assert autojinja.path.no_antislash("/dir1\\dir2/file.txt") == "/dir1/dir2/file.txt"

    def test_abspath(self):
        assert len(autojinja.path.abspath(""))                     >= len("")
        assert len(autojinja.path.abspath("file.txt"))             >= len("file.txt")
        assert len(autojinja.path.abspath("/file.txt"))            >= len("/file.txt")
        assert len(autojinja.path.abspath("C:/"))                  >= len("C:/")
        assert len(autojinja.path.abspath("\\"))                   >= len("/")
        assert len(autojinja.path.abspath("/dir1"))                >= len("/dir1")
        assert len(autojinja.path.abspath("/dir1\\"))              >= len("/dir1/")
        assert len(autojinja.path.abspath("/dir1/file.txt"))       >= len("/dir1/file.txt")
        assert len(autojinja.path.abspath("/dir1\\dir2/file.txt")) >= len("/dir1/dir2/file.txt")

    def test_commonpath(self):
        assert autojinja.path.commonpath(["/dir1", "/dir1\\", "/dir1/file.txt", "/dir1\\dir2/file.txt"]) == "/dir1/"

    def test_commonprefix(self):
        assert autojinja.path.commonprefix(["/dir1", "/dir1\\", "/dir1/file.txt", "/dir1\\dir2/file.txt"]) == "/dir1"

    def test_exists(self):
        assert autojinja.path.exists(root) == True
        assert autojinja.path.exists(dir1) == True
        assert autojinja.path.exists(dir2) == True
        assert autojinja.path.exists(file1) == True
        assert autojinja.path.exists(file2) == True
        assert autojinja.path.exists(file3) == True
        assert autojinja.path.exists(file4) == True
        assert autojinja.path.exists(root.join("dummy")) == False
        assert autojinja.path.exists(dir1.join("dummy")) == False
        assert autojinja.path.exists(dir2.join("dummy")) == False
        assert autojinja.path.exists(file1.join("dummy")) == False
        assert autojinja.path.exists(file2.join("dummy")) == False
        assert autojinja.path.exists(file3.join("dummy")) == False
        assert autojinja.path.exists(file4.join("dummy")) == False

    def test_lexists(self):
        assert autojinja.path.lexists(root) == True
        assert autojinja.path.lexists(dir1) == True
        assert autojinja.path.lexists(dir2) == True
        assert autojinja.path.lexists(file1) == True
        assert autojinja.path.lexists(file2) == True
        assert autojinja.path.lexists(file3) == True
        assert autojinja.path.lexists(file4) == True
        assert autojinja.path.lexists(root.join("dummy")) == False
        assert autojinja.path.lexists(dir1.join("dummy")) == False
        assert autojinja.path.lexists(dir2.join("dummy")) == False
        assert autojinja.path.lexists(file1.join("dummy")) == False
        assert autojinja.path.lexists(file2.join("dummy")) == False
        assert autojinja.path.lexists(file3.join("dummy")) == False
        assert autojinja.path.lexists(file4.join("dummy")) == False

    def test_expanduser(self):
        assert autojinja.path.expanduser("")                     == ""
        assert autojinja.path.expanduser("file.txt")             == "file.txt"
        assert autojinja.path.expanduser("/file.txt")            == "/file.txt"
        assert autojinja.path.expanduser("C:/")                  == "C:/"
        assert autojinja.path.expanduser("\\")                   == "/"
        assert autojinja.path.expanduser("/dir1")                == "/dir1"
        assert autojinja.path.expanduser("/dir1\\")              == "/dir1/"
        assert autojinja.path.expanduser("/dir1/file.txt")       == "/dir1/file.txt"
        assert autojinja.path.expanduser("/dir1\\dir2/file.txt") == "/dir1/dir2/file.txt"

    def test_expandvars(self):
        assert autojinja.path.expandvars("")                     == ""
        assert autojinja.path.expandvars("file.txt")             == "file.txt"
        assert autojinja.path.expandvars("/file.txt")            == "/file.txt"
        assert autojinja.path.expandvars("C:/")                  == "C:/"
        assert autojinja.path.expandvars("\\")                   == "/"
        assert autojinja.path.expandvars("/dir1")                == "/dir1"
        assert autojinja.path.expandvars("/dir1\\")              == "/dir1/"
        assert autojinja.path.expandvars("/dir1/file.txt")       == "/dir1/file.txt"
        assert autojinja.path.expandvars("/dir1\\dir2/file.txt") == "/dir1/dir2/file.txt"

    def test_getatime(self):
        assert autojinja.path.getatime(root)  > 0
        assert autojinja.path.getatime(dir1)  > 0
        assert autojinja.path.getatime(dir2)  > 0
        assert autojinja.path.getatime(file1) > 0
        assert autojinja.path.getatime(file2) > 0
        assert autojinja.path.getatime(file3) > 0
        assert autojinja.path.getatime(file4) > 0

    def test_getmtime(self):
        assert autojinja.path.getmtime(root)  > 0
        assert autojinja.path.getmtime(dir1)  > 0
        assert autojinja.path.getmtime(dir2)  > 0
        assert autojinja.path.getmtime(file1) > 0
        assert autojinja.path.getmtime(file2) > 0
        assert autojinja.path.getmtime(file3) > 0
        assert autojinja.path.getmtime(file4) > 0

    def test_getctime(self):
        assert autojinja.path.getctime(root)  > 0
        assert autojinja.path.getctime(dir1)  > 0
        assert autojinja.path.getctime(dir2)  > 0
        assert autojinja.path.getctime(file1) > 0
        assert autojinja.path.getctime(file2) > 0
        assert autojinja.path.getctime(file3) > 0
        assert autojinja.path.getctime(file4) > 0

    def test_isabs(self):
        assert autojinja.path.isabs("")                     == False
        assert autojinja.path.isabs("file.txt")             == False
        assert autojinja.path.isabs("/file.txt")            == True
        assert autojinja.path.isabs("C:/")                  == True
        assert autojinja.path.isabs("\\")                   == True
        assert autojinja.path.isabs("/dir1")                == True
        assert autojinja.path.isabs("/dir1\\")              == True
        assert autojinja.path.isabs("/dir1/file.txt")       == True
        assert autojinja.path.isabs("/dir1\\dir2/file.txt") == True

    def test_isfile(self):
        assert autojinja.path.isfile(root)  == False
        assert autojinja.path.isfile(dir1)  == False
        assert autojinja.path.isfile(dir2)  == False
        assert autojinja.path.isfile(file1) == True
        assert autojinja.path.isfile(file2) == True
        assert autojinja.path.isfile(file3) == True
        assert autojinja.path.isfile(file4) == True
        assert autojinja.path.isfile(root.join("dummy")) == False
        assert autojinja.path.isfile(dir1.join("dummy")) == False
        assert autojinja.path.isfile(dir2.join("dummy")) == False
        assert autojinja.path.isfile(file1.join("dummy")) == False
        assert autojinja.path.isfile(file2.join("dummy")) == False
        assert autojinja.path.isfile(file3.join("dummy")) == False
        assert autojinja.path.isfile(file4.join("dummy")) == False

    def test_isdir(self):
        assert autojinja.path.isdir(root)  == True
        assert autojinja.path.isdir(dir1)  == True
        assert autojinja.path.isdir(dir2)  == True
        assert autojinja.path.isdir(file1) == False
        assert autojinja.path.isdir(file2) == False
        assert autojinja.path.isdir(file3) == False
        assert autojinja.path.isdir(file4) == False
        assert autojinja.path.isdir(root.join("dummy")) == False
        assert autojinja.path.isdir(dir1.join("dummy")) == False
        assert autojinja.path.isdir(dir2.join("dummy")) == False
        assert autojinja.path.isdir(file1.join("dummy")) == False
        assert autojinja.path.isdir(file2.join("dummy")) == False
        assert autojinja.path.isdir(file3.join("dummy")) == False
        assert autojinja.path.isdir(file4.join("dummy")) == False

    def test_islink(self):
        assert autojinja.path.islink(root)  == False
        assert autojinja.path.islink(dir1)  == False
        assert autojinja.path.islink(dir2)  == False
        assert autojinja.path.islink(file1) == False
        assert autojinja.path.islink(file2) == False
        assert autojinja.path.islink(file3) == False
        assert autojinja.path.islink(file4) == False

    def test_ismount(self):
        assert autojinja.path.ismount(root)  == False
        assert autojinja.path.ismount(dir1)  == False
        assert autojinja.path.ismount(dir2)  == False
        assert autojinja.path.ismount(file1) == False
        assert autojinja.path.ismount(file2) == False
        assert autojinja.path.ismount(file3) == False
        assert autojinja.path.ismount(file4) == False

    def test_normcase(self):
        assert autojinja.path.normcase("")                     == ""
        assert autojinja.path.normcase("file.txt")             == "file.txt"
        assert autojinja.path.normcase("/file.txt")            == "/file.txt"
        assert autojinja.path.normcase("C:/")                  == "c:/"
        assert autojinja.path.normcase("\\")                   == "/"
        assert autojinja.path.normcase("/dir1")                == "/dir1"
        assert autojinja.path.normcase("/dir1\\")              == "/dir1/"
        assert autojinja.path.normcase("/dir1/file.txt")       == "/dir1/file.txt"
        assert autojinja.path.normcase("/dir1\\dir2/file.txt") == "/dir1/dir2/file.txt"

    def test_normpath(self):
        assert autojinja.path.normpath("")                     == ""
        assert autojinja.path.normpath("file.txt")             == "file.txt"
        assert autojinja.path.normpath("/file.txt")            == "/file.txt"
        assert autojinja.path.normpath("C:/")                  == "C:/"
        assert autojinja.path.normpath("\\")                   == "/"
        assert autojinja.path.normpath("/dir1")                == "/dir1"
        assert autojinja.path.normpath("/dir1\\")              == "/dir1/"
        assert autojinja.path.normpath("/dir1/file.txt")       == "/dir1/file.txt"
        assert autojinja.path.normpath("/dir1\\dir2/file.txt") == "/dir1/dir2/file.txt"

    def test_realpath(self):
        assert len(autojinja.path.realpath(""))                     >= len("")
        assert len(autojinja.path.realpath("file.txt"))             >= len("file.txt")
        assert len(autojinja.path.realpath("/file.txt"))            >= len("/file.txt")
        assert len(autojinja.path.realpath("C:/"))                  >= len("C:/")
        assert len(autojinja.path.realpath("\\"))                   >= len("/")
        assert len(autojinja.path.realpath("/dir1"))                >= len("/dir1")
        assert len(autojinja.path.realpath("/dir1\\"))              >= len("/dir1/")
        assert len(autojinja.path.realpath("/dir1/file.txt"))       >= len("/dir1/file.txt")
        assert len(autojinja.path.realpath("/dir1\\dir2/file.txt")) >= len("/dir1/dir2/file.txt" )

    def test_samefile(self):
        assert autojinja.path.samefile(root, root) == True
        assert autojinja.path.samefile(root, file1) == False

    def test_samestat(self):
        assert autojinja.path.samestat(os.stat(root), os.stat(root)) == True
        assert autojinja.path.samestat(os.stat(root), os.stat(file1)) == False

    def test_splitpath(self):
        assert autojinja.path.splitpath("")                     == ("", "")
        assert autojinja.path.splitpath("file.txt")             == ("", "file.txt")
        assert autojinja.path.splitpath("/file.txt")            == ("/", "file.txt")
        assert autojinja.path.splitpath("C:/")                  == ("C:/", "")
        assert autojinja.path.splitpath("\\")                   == ("/", "")
        assert autojinja.path.splitpath("/dir1")                == ("/", "dir1")
        assert autojinja.path.splitpath("/dir1\\")              == ("/dir1", "")
        assert autojinja.path.splitpath("/dir1/file.txt")       == ("/dir1", "file.txt")
        assert autojinja.path.splitpath("/dir1\\dir2/file.txt") == ("/dir1/dir2", "file.txt")

    def test_splitdrive(self):
        assert autojinja.path.splitdrive("")                     == ("", "")
        assert autojinja.path.splitdrive("file.txt")             == ("", "file.txt")
        assert autojinja.path.splitdrive("/file.txt")            == ("", "/file.txt")
        assert autojinja.path.splitdrive("C:/")                  == ("C:", "/")
        assert autojinja.path.splitdrive("\\")                   == ("", "/")
        assert autojinja.path.splitdrive("/dir1")                == ("", "/dir1")
        assert autojinja.path.splitdrive("/dir1\\")              == ("", "/dir1/")
        assert autojinja.path.splitdrive("/dir1/file.txt")       == ("", "/dir1/file.txt")
        assert autojinja.path.splitdrive("/dir1\\dir2/file.txt") == ("", "/dir1/dir2/file.txt")

    def test_splitext(self):
        assert autojinja.path.splitext("")                     == ("", "")
        assert autojinja.path.splitext("file.txt")             == ("file", ".txt")
        assert autojinja.path.splitext("/file.txt")            == ("/file", ".txt")
        assert autojinja.path.splitext("C:/")                  == ("C:/", "")
        assert autojinja.path.splitext("\\")                   == ("/", "")
        assert autojinja.path.splitext("/dir1")                == ("/dir1", "")
        assert autojinja.path.splitext("/dir1\\")              == ("/dir1/", "")
        assert autojinja.path.splitext("/dir1/file.txt")       == ("/dir1/file", ".txt")
        assert autojinja.path.splitext("/dir1\\dir2/file.txt") == ("/dir1/dir2/file", ".txt")

class TestPath:
    def test_join(self):
        assert autojinja.path.Path("").join("file.txt")            == "file.txt"
        assert autojinja.path.Path("/").join("file.txt")           == "/file.txt"
        assert autojinja.path.Path("C:/").join("file.txt")         == "C:/file.txt"
        assert autojinja.path.Path("/dir1").join("file.txt")       == "/dir1/file.txt"
        assert autojinja.path.Path("\\dir1/").join("file.txt")     == "/dir1/file.txt"
        assert autojinja.path.Path("/dir1\\dir2").join("file.txt") == "/dir1/dir2/file.txt"

    def test_join_brackets(self):
        assert autojinja.path.Path("").join["file.txt"]                 == "file.txt/"
        assert autojinja.path.Path("/").join["file.txt"]                == "/file.txt/"
        assert autojinja.path.Path("C:/").join["file.txt"]              == "C:/file.txt/"
        assert autojinja.path.Path("/dir1").join["file.txt", "a"]       == "/dir1/file.txt/a/"
        assert autojinja.path.Path("\\dir1/").join["file.txt", "a"]     == "/dir1/file.txt/a/"
        assert autojinja.path.Path("/dir1\\dir2").join["file.txt", "a"] == "/dir1/dir2/file.txt/a/"

    def test_add(self):
        assert autojinja.path.Path("").add("file.txt")            == "file.txt"
        assert autojinja.path.Path("/").add("file.txt")           == "/file.txt"
        assert autojinja.path.Path("C:/").add("file.txt")         == "C:/file.txt"
        assert autojinja.path.Path("\\dir1").add("file.txt")      == "/dir1file.txt"
        assert autojinja.path.Path("/dir1/").add("file.txt")      == "/dir1/file.txt"
        assert autojinja.path.Path("/dir1\\dir2").add("file.txt") == "/dir1/dir2file.txt"

        assert autojinja.path.Path("") + "file.txt"            == "file.txt"
        assert autojinja.path.Path("/") + "file.txt"           == "/file.txt"
        assert autojinja.path.Path("C:/") + "file.txt"         == "C:/file.txt"
        assert autojinja.path.Path("\\dir1") + "file.txt"      == "/dir1file.txt"
        assert autojinja.path.Path("/dir1/") + "file.txt"      == "/dir1/file.txt"
        assert autojinja.path.Path("/dir1\\dir2") + "file.txt" == "/dir1/dir2file.txt"

        assert  "" + autojinja.path.Path("file.txt")            == "file.txt"
        assert  "/" + autojinja.path.Path("file.txt")           == "/file.txt"
        assert  "C:/" + autojinja.path.Path("file.txt")         == "C:/file.txt"
        assert  "\\dir1" + autojinja.path.Path("file.txt")      == "/dir1file.txt"
        assert  "/dir1/" + autojinja.path.Path("file.txt")      == "/dir1/file.txt"
        assert  "/dir1\\dir2" + autojinja.path.Path("file.txt") == "/dir1/dir2file.txt"

    def test_truediv(self):
        assert autojinja.path.Path("") / "file.txt"            == "file.txt"
        assert autojinja.path.Path("/") / "file.txt"           == "/file.txt"
        assert autojinja.path.Path("C:/") / "file.txt"         == "C:/file.txt"
        assert autojinja.path.Path("\\dir1") / "file.txt"      == "/dir1/file.txt"
        assert autojinja.path.Path("/dir1/") / "file.txt"      == "/dir1/file.txt"
        assert autojinja.path.Path("/dir1\\dir2") / "file.txt" == "/dir1/dir2/file.txt"

    def test_files(self):
        # dir
        values = root.files("**")
        assert len(values) == 4
        assert file1 in values
        assert file2 in values
        assert file3 in values
        assert file4 in values
        values = dir1.files("**")
        assert len(values) == 2
        assert file3 in values
        assert file4 in values
        values = dir2.files("**")
        assert len(values) == 1
        assert file4 in values
        values = root.files("*.ext")
        assert len(values) == 1
        assert file2 in values
        values = root.files("**/*.ext")
        assert len(values) == 2
        assert file2 in values
        assert file4 in values
        # file
        values = file1.files("**")
        assert len(values) == 4
        assert file1 in values
        assert file2 in values
        assert file3 in values
        assert file4 in values
        values = file3.files("**")
        assert len(values) == 2
        assert file3 in values
        assert file4 in values
        values = file4.files("**")
        assert len(values) == 1
        assert file4 in values
        values = file2.files("*.ext")
        assert len(values) == 1
        assert file2 in values
        values = file2.files("**/*.ext")
        assert len(values) == 2
        assert file2 in values
        assert file4 in values

    def test_dirs(self):
        # dir
        values = root.dirs("**")
        assert len(values) == 3
        assert root == values[0]
        assert dir1 in values
        assert dir2 in values
        values = dir1.dirs("**")
        assert len(values) == 2
        assert dir1 == values[0]
        assert dir2 in values
        values = dir2.dirs("**")
        assert len(values) == 1
        assert dir2 == values[0]
        # file
        values = file2.dirs("**")
        assert len(values) == 3
        assert root == values[0]
        assert dir1 in values
        assert dir2 in values
        values = file3.dirs("**")
        assert len(values) == 2
        assert dir1 == values[0]
        assert dir2 in values
        values = file4.dirs("**")
        assert len(values) == 1
        assert dir2 == values[0]

    def test_filepath(self):
        assert autojinja.path.Path("").filepath                     == ""
        assert autojinja.path.Path("file.txt").filepath             == "file.txt"
        assert autojinja.path.Path("/file.txt").filepath            == "/file.txt"
        assert autojinja.path.Path("C:/").filepath                  == "C:/"
        assert autojinja.path.Path("\\").filepath                   == "/"
        assert autojinja.path.Path("/dir1\\").filepath              == "/dir1/"
        assert autojinja.path.Path("/dir1/file.txt").filepath       == "/dir1/file.txt"
        assert autojinja.path.Path("/dir1\\dir2/file.txt").filepath == "/dir1/dir2/file.txt"

    def test_filename(self):
        assert autojinja.path.Path("").filename                     == ""
        assert autojinja.path.Path("file.txt").filename             == "file.txt"
        assert autojinja.path.Path("/file.txt").filename            == "file.txt"
        assert autojinja.path.Path("C:/").filename                  == ""
        assert autojinja.path.Path("\\").filename                   == ""
        assert autojinja.path.Path("/dir1\\").filename              == ""
        assert autojinja.path.Path("/dir1/file.txt").filename       == "file.txt"
        assert autojinja.path.Path("/dir1\\dir2/file.txt").filename == "file.txt"

    def test_set_filename(self):
        assert autojinja.path.Path("").set_filename("new.md")                     == "new.md"
        assert autojinja.path.Path("file.txt").set_filename("new.md")             == "new.md"
        assert autojinja.path.Path("/").set_filename("new.md")                    == "/new.md"
        assert autojinja.path.Path("C:/").set_filename("new.md")                  == "C:/new.md"
        assert autojinja.path.Path("\\").set_filename("new.md")                   == "/new.md"
        assert autojinja.path.Path("/dir1\\").set_filename("new.md")              == "/dir1/new.md"
        assert autojinja.path.Path("/dir1/file.txt").set_filename("new.md")       == "/dir1/new.md"
        assert autojinja.path.Path("/dir1\\dir2/file.txt").set_filename("new.md") == "/dir1/dir2/new.md"

    def test_dirpath(self):
        if os.name != "nt": # Unix
            assert autojinja.path.Path("").dirpath                     == ""
            assert autojinja.path.Path("file.txt").dirpath             == ""
            assert autojinja.path.Path("/file.txt").dirpath            == "/"
            assert autojinja.path.Path("C:").dirpath                   == ""
            assert autojinja.path.Path("C:/").dirpath                  == "C:/"
            assert autojinja.path.Path("/").dirpath                    == "/"
            assert autojinja.path.Path("\\").dirpath                   == "/"
            assert autojinja.path.Path("/dir1").dirpath                == "/"
            assert autojinja.path.Path("/dir1/").dirpath               == "/dir1/"
            assert autojinja.path.Path("/dir1\\ab").dirpath            == "/dir1/"
            assert autojinja.path.Path("/dir1/file.txt").dirpath       == "/dir1/"
            assert autojinja.path.Path("/dir1\\dir2/file.txt").dirpath == "/dir1/dir2/"
        else: # Windows
            assert autojinja.path.Path("").dirpath                     == ""
            assert autojinja.path.Path("file.txt").dirpath             == ""
            assert autojinja.path.Path("/file.txt").dirpath            == "/"
            assert autojinja.path.Path("C:").dirpath                   == "C:/"
            assert autojinja.path.Path("C:/").dirpath                  == "C:/"
            assert autojinja.path.Path("/").dirpath                    == "/"
            assert autojinja.path.Path("\\").dirpath                   == "/"
            assert autojinja.path.Path("/dir1").dirpath                == "/"
            assert autojinja.path.Path("/dir1/").dirpath               == "/dir1/"
            assert autojinja.path.Path("/dir1\\ab").dirpath            == "/dir1/"
            assert autojinja.path.Path("/dir1/file.txt").dirpath       == "/dir1/"
            assert autojinja.path.Path("/dir1\\dir2/file.txt").dirpath == "/dir1/dir2/"

    def test_dirname(self):
        if os.name != "nt": # Unix
            assert autojinja.path.Path("").dirname                     == ""
            assert autojinja.path.Path("file.txt").dirname             == ""
            assert autojinja.path.Path("/file.txt").dirname            == ""
            assert autojinja.path.Path("C:").dirname                   == ""
            assert autojinja.path.Path("C:/").dirname                  == "C:"
            assert autojinja.path.Path("/").dirname                    == ""
            assert autojinja.path.Path("\\").dirname                   == ""
            assert autojinja.path.Path("/dir1").dirname                == ""
            assert autojinja.path.Path("/dir1/").dirname               == "dir1"
            assert autojinja.path.Path("/dir1\\").dirname              == "dir1"
            assert autojinja.path.Path("/dir1/file.txt").dirname       == "dir1"
            assert autojinja.path.Path("/dir1\\dir2/file.txt").dirname == "dir2"
        else: # Windows
            assert autojinja.path.Path("").dirname                     == ""
            assert autojinja.path.Path("file.txt").dirname             == ""
            assert autojinja.path.Path("/file.txt").dirname            == ""
            assert autojinja.path.Path("C:").dirname                   == "C:"
            assert autojinja.path.Path("C:/").dirname                  == "C:"
            assert autojinja.path.Path("/").dirname                    == ""
            assert autojinja.path.Path("\\").dirname                   == ""
            assert autojinja.path.Path("/dir1").dirname                == ""
            assert autojinja.path.Path("/dir1/").dirname               == "dir1"
            assert autojinja.path.Path("/dir1\\").dirname              == "dir1"
            assert autojinja.path.Path("/dir1/file.txt").dirname       == "dir1"
            assert autojinja.path.Path("/dir1\\dir2/file.txt").dirname == "dir2"

    def test_parent_dirpath(self):
        if os.name != "nt": # Unix
            assert autojinja.path.Path("").parent_dirpath                     == ""
            assert autojinja.path.Path("file.txt").parent_dirpath             == ""
            assert autojinja.path.Path("/file.txt").parent_dirpath            == "/"
            assert autojinja.path.Path("C:").parent_dirpath                   == ""
            assert autojinja.path.Path("C:/").parent_dirpath                  == ""
            assert autojinja.path.Path("/").parent_dirpath                    == "/"
            assert autojinja.path.Path("\\").parent_dirpath                   == "/"
            assert autojinja.path.Path("/dir1").parent_dirpath                == "/"
            assert autojinja.path.Path("/dir1/").parent_dirpath               == "/"
            assert autojinja.path.Path("/dir1\\").parent_dirpath              == "/"
            assert autojinja.path.Path("/dir1/file.txt").parent_dirpath       == "/"
            assert autojinja.path.Path("/dir1\\dir2/file.txt").parent_dirpath == "/dir1/"
        else: # Windows
            assert autojinja.path.Path("").parent_dirpath                     == ""
            assert autojinja.path.Path("file.txt").parent_dirpath             == ""
            assert autojinja.path.Path("/file.txt").parent_dirpath            == "/"
            assert autojinja.path.Path("C:").parent_dirpath                   == "C:/"
            assert autojinja.path.Path("C:/").parent_dirpath                  == "C:/"
            assert autojinja.path.Path("/").parent_dirpath                    == "/"
            assert autojinja.path.Path("\\").parent_dirpath                   == "/"
            assert autojinja.path.Path("/dir1").parent_dirpath                == "/"
            assert autojinja.path.Path("/dir1/").parent_dirpath               == "/"
            assert autojinja.path.Path("/dir1\\").parent_dirpath              == "/"
            assert autojinja.path.Path("/dir1/file.txt").parent_dirpath       == "/"
            assert autojinja.path.Path("/dir1\\dir2/file.txt").parent_dirpath == "/dir1/"

    def test_parent_dirname(self):
        if os.name != "nt": # Unix
            assert autojinja.path.Path("").parent_dirname                     == ""
            assert autojinja.path.Path("file.txt").parent_dirname             == ""
            assert autojinja.path.Path("/file.txt").parent_dirname            == ""
            assert autojinja.path.Path("C:").parent_dirname                   == ""
            assert autojinja.path.Path("C:/").parent_dirname                  == ""
            assert autojinja.path.Path("/").parent_dirname                    == ""
            assert autojinja.path.Path("\\").parent_dirname                   == ""
            assert autojinja.path.Path("/dir1").parent_dirname                == ""
            assert autojinja.path.Path("/dir1/").parent_dirname               == ""
            assert autojinja.path.Path("/dir1\\").parent_dirname              == ""
            assert autojinja.path.Path("/dir1/file.txt").parent_dirname       == ""
            assert autojinja.path.Path("/dir1\\dir2/file.txt").parent_dirname == "dir1"
        else: # Windows
            assert autojinja.path.Path("").parent_dirname                     == ""
            assert autojinja.path.Path("file.txt").parent_dirname             == ""
            assert autojinja.path.Path("/file.txt").parent_dirname            == ""
            assert autojinja.path.Path("C:").parent_dirname                   == "C:"
            assert autojinja.path.Path("C:/").parent_dirname                  == "C:"
            assert autojinja.path.Path("/").parent_dirname                    == ""
            assert autojinja.path.Path("\\").parent_dirname                   == ""
            assert autojinja.path.Path("/dir1").parent_dirname                == ""
            assert autojinja.path.Path("/dir1/").parent_dirname               == ""
            assert autojinja.path.Path("/dir1\\").parent_dirname              == ""
            assert autojinja.path.Path("/dir1/file.txt").parent_dirname       == ""
            assert autojinja.path.Path("/dir1\\dir2/file.txt").parent_dirname == "dir1"

    def test_ext(self):
        assert autojinja.path.Path("").ext                     == ""
        assert autojinja.path.Path("file.ext.txt").ext         == ".txt"
        assert autojinja.path.Path("/file.ext.txt").ext        == ".txt"
        assert autojinja.path.Path("C:/").ext                  == ""
        assert autojinja.path.Path("\\").ext                   == ""
        assert autojinja.path.Path("/dir1").ext                == ""
        assert autojinja.path.Path("/dir1\\").ext              == ""
        assert autojinja.path.Path("/dir1/file.txt").ext       == ".txt"
        assert autojinja.path.Path("/dir1\\dir2/file.txt").ext == ".txt"

    def test_set_ext(self):
        assert autojinja.path.Path("").set_ext(".md")                     == ".md"
        assert autojinja.path.Path("file.ext.txt").set_ext(".md")         == "file.ext.md"
        assert autojinja.path.Path("/file.ext.txt").set_ext(".md")        == "/file.ext.md"
        assert autojinja.path.Path("C:/").set_ext(".md")                  == "C:/.md"
        assert autojinja.path.Path("\\").set_ext(".md")                   == "/.md"
        assert autojinja.path.Path("/dir1").set_ext(".md")                == "/dir1.md"
        assert autojinja.path.Path("/dir1\\").set_ext(".md")              == "/dir1/.md"
        assert autojinja.path.Path("/dir1/file.txt").set_ext(".md")       == "/dir1/file.md"
        assert autojinja.path.Path("/dir1\\dir2/file.txt").set_ext(".md") == "/dir1/dir2/file.md"

    def test_no_ext(self):
        assert autojinja.path.Path("").no_ext                     == ""
        assert autojinja.path.Path("file.txt").no_ext             == "file"
        assert autojinja.path.Path("/file.txt").no_ext            == "/file"
        assert autojinja.path.Path("/file.ext.txt").no_ext        == "/file.ext"
        assert autojinja.path.Path("C:/").no_ext                  == "C:/"
        assert autojinja.path.Path("\\").no_ext                   == "/"
        assert autojinja.path.Path("/dir1").no_ext                == "/dir1"
        assert autojinja.path.Path("/dir1\\").no_ext              == "/dir1/"
        assert autojinja.path.Path("/dir1/file.txt").no_ext       == "/dir1/file"
        assert autojinja.path.Path("/dir1\\dir2/file.txt").no_ext == "/dir1/dir2/file"

    def test_fullext(self):
        assert autojinja.path.Path("").fullext                     == ""
        assert autojinja.path.Path("file.ext.txt").fullext         == ".ext.txt"
        assert autojinja.path.Path("/file.ext.txt").fullext        == ".ext.txt"
        assert autojinja.path.Path("C:/").fullext                  == ""
        assert autojinja.path.Path("\\").fullext                   == ""
        assert autojinja.path.Path("/dir1").fullext                == ""
        assert autojinja.path.Path("/dir1\\").fullext              == ""
        assert autojinja.path.Path("/dir1/file").fullext           == ""
        assert autojinja.path.Path("/dir1\\dir2/file.txt").fullext == ".txt"

    def test_set_fullext(self):
        assert autojinja.path.Path("").set_fullext(".md")                     == ".md"
        assert autojinja.path.Path("file.ext.txt").set_fullext(".md")         == "file.md"
        assert autojinja.path.Path("/file.ext.txt").set_fullext(".md")        == "/file.md"
        assert autojinja.path.Path("C:/").set_fullext(".md")                  == "C:/.md"
        assert autojinja.path.Path("\\").set_fullext(".md")                   == "/.md"
        assert autojinja.path.Path("/dir1").set_fullext(".md")                == "/dir1.md"
        assert autojinja.path.Path("/dir1\\").set_fullext(".md")              == "/dir1/.md"
        assert autojinja.path.Path("/dir1/file").set_fullext(".md")           == "/dir1/file.md"
        assert autojinja.path.Path("/dir1\\dir2/file.txt").set_fullext(".md") == "/dir1/dir2/file.md"

    def test_no_fullext(self):
        assert autojinja.path.Path("").no_fullext                     == ""
        assert autojinja.path.Path("file.txt").no_fullext             == "file"
        assert autojinja.path.Path("/file.txt").no_fullext            == "/file"
        assert autojinja.path.Path("/file.ext.txt").no_fullext        == "/file"
        assert autojinja.path.Path("C:/").no_fullext                  == "C:/"
        assert autojinja.path.Path("\\").no_fullext                   == "/"
        assert autojinja.path.Path("/dir1").no_fullext                == "/dir1"
        assert autojinja.path.Path("/dir1\\").no_fullext              == "/dir1/"
        assert autojinja.path.Path("/dir1/file").no_fullext           == "/dir1/file"
        assert autojinja.path.Path("/dir1\\dir2/file.txt").no_fullext == "/dir1/dir2/file"

    def test_slash(self):
        assert autojinja.path.Path("").slash                     == "/"
        assert autojinja.path.Path("file.txt").slash             == "file.txt/"
        assert autojinja.path.Path("/file.txt").slash            == "/file.txt/"
        assert autojinja.path.Path("C:/").slash                  == "C:/"
        assert autojinja.path.Path("\\").slash                   == "/"
        assert autojinja.path.Path("/dir1").slash                == "/dir1/"
        assert autojinja.path.Path("/dir1\\").slash              == "/dir1/"
        assert autojinja.path.Path("/dir1/file.txt").slash       == "/dir1/file.txt/"
        assert autojinja.path.Path("/dir1\\dir2/file.txt").slash == "/dir1/dir2/file.txt/"

    def test_no_slash(self):
        assert autojinja.path.Path("").no_slash                     == ""
        assert autojinja.path.Path("file.txt").no_slash             == "file.txt"
        assert autojinja.path.Path("/file.txt").no_slash            == "/file.txt"
        assert autojinja.path.Path("C:/").no_slash                  == "C:"
        assert autojinja.path.Path("\\").no_slash                   == ""
        assert autojinja.path.Path("/dir1").no_slash                == "/dir1"
        assert autojinja.path.Path("/dir1\\").no_slash              == "/dir1"
        assert autojinja.path.Path("/dir1/file.txt").no_slash       == "/dir1/file.txt"
        assert autojinja.path.Path("/dir1\\dir2/file.txt").no_slash == "/dir1/dir2/file.txt"

    def test_abspath(self):
        assert len(autojinja.path.Path("").abspath)                     >= len("")
        assert len(autojinja.path.Path("file.txt").abspath)             >= len("file.txt")
        assert len(autojinja.path.Path("/file.txt").abspath)            >= len("/file.txt")
        assert len(autojinja.path.Path("C:/").abspath)                  >= len("C:/")
        assert len(autojinja.path.Path("\\").abspath)                   >= len("/")
        assert len(autojinja.path.Path("/dir1").abspath)                >= len("/dir1")
        assert len(autojinja.path.Path("/dir1\\").abspath)              >= len("/dir1/")
        assert len(autojinja.path.Path("/dir1/file.txt").abspath)       >= len("/dir1/file.txt")
        assert len(autojinja.path.Path("/dir1\\dir2/file.txt").abspath) >= len("/dir1/dir2/file.txt")

    def test_commonpath(self):
        assert autojinja.path.Path("/dir1").commonpath(["/dir1\\", "/dir1/file.txt", "/dir1\\dir2/file.txt"]) == "/dir1/"

    def test_commonprefix(self):
        assert autojinja.path.Path("/dir1").commonprefix(["/dir1\\", "/dir1/file.txt", "/dir1\\dir2/file.txt"]) == "/dir1"

    def test_exists(self):
        assert autojinja.path.Path(root).exists == True
        assert autojinja.path.Path(dir1).exists == True
        assert autojinja.path.Path(dir2).exists == True
        assert autojinja.path.Path(file1).exists == True
        assert autojinja.path.Path(file2).exists == True
        assert autojinja.path.Path(file3).exists == True
        assert autojinja.path.Path(file4).exists == True
        assert autojinja.path.Path(root.join("dummy")).exists == False
        assert autojinja.path.Path(dir1.join("dummy")).exists == False
        assert autojinja.path.Path(dir2.join("dummy")).exists == False
        assert autojinja.path.Path(file1.join("dummy")).exists == False
        assert autojinja.path.Path(file2.join("dummy")).exists == False
        assert autojinja.path.Path(file3.join("dummy")).exists == False
        assert autojinja.path.Path(file4.join("dummy")).exists == False

    def test_lexists(self):
        assert autojinja.path.Path(root).lexists == True
        assert autojinja.path.Path(dir1).lexists == True
        assert autojinja.path.Path(dir2).lexists == True
        assert autojinja.path.Path(file1).lexists == True
        assert autojinja.path.Path(file2).lexists == True
        assert autojinja.path.Path(file3).lexists == True
        assert autojinja.path.Path(file4).lexists == True
        assert autojinja.path.Path(root.join("dummy")).lexists == False
        assert autojinja.path.Path(dir1.join("dummy")).lexists == False
        assert autojinja.path.Path(dir2.join("dummy")).lexists == False
        assert autojinja.path.Path(file1.join("dummy")).lexists == False
        assert autojinja.path.Path(file2.join("dummy")).lexists == False
        assert autojinja.path.Path(file3.join("dummy")).lexists == False
        assert autojinja.path.Path(file4.join("dummy")).lexists == False

    def test_expanduser(self):
        assert autojinja.path.Path("").expanduser                     == ""
        assert autojinja.path.Path("file.txt").expanduser             == "file.txt"
        assert autojinja.path.Path("/file.txt").expanduser            == "/file.txt"
        assert autojinja.path.Path("C:/").expanduser                  == "C:/"
        assert autojinja.path.Path("\\").expanduser                   == "/"
        assert autojinja.path.Path("/dir1").expanduser                == "/dir1"
        assert autojinja.path.Path("/dir1\\").expanduser              == "/dir1/"
        assert autojinja.path.Path("/dir1/file.txt").expanduser       == "/dir1/file.txt"
        assert autojinja.path.Path("/dir1\\dir2/file.txt").expanduser == "/dir1/dir2/file.txt"

    def test_expandvars(self):
        assert autojinja.path.Path("").expandvars                     == ""
        assert autojinja.path.Path("file.txt").expandvars             == "file.txt"
        assert autojinja.path.Path("/file.txt").expandvars            == "/file.txt"
        assert autojinja.path.Path("C:/").expandvars                  == "C:/"
        assert autojinja.path.Path("\\").expandvars                   == "/"
        assert autojinja.path.Path("/dir1").expandvars                == "/dir1"
        assert autojinja.path.Path("/dir1\\").expandvars              == "/dir1/"
        assert autojinja.path.Path("/dir1/file.txt").expandvars       == "/dir1/file.txt"
        assert autojinja.path.Path("/dir1\\dir2/file.txt").expandvars == "/dir1/dir2/file.txt"

    def test_getatime(self):
        assert autojinja.path.Path(root).getatime  > 0
        assert autojinja.path.Path(dir1).getatime  > 0
        assert autojinja.path.Path(dir2).getatime  > 0
        assert autojinja.path.Path(file1).getatime > 0
        assert autojinja.path.Path(file2).getatime > 0
        assert autojinja.path.Path(file3).getatime > 0
        assert autojinja.path.Path(file4).getatime > 0

    def test_getmtime(self):
        assert autojinja.path.Path(root).getmtime  > 0
        assert autojinja.path.Path(dir1).getmtime  > 0
        assert autojinja.path.Path(dir2).getmtime  > 0
        assert autojinja.path.Path(file1).getmtime > 0
        assert autojinja.path.Path(file2).getmtime > 0
        assert autojinja.path.Path(file3).getmtime > 0
        assert autojinja.path.Path(file4).getmtime > 0

    def test_getctime(self):
        assert autojinja.path.Path(root).getctime  > 0
        assert autojinja.path.Path(dir1).getctime  > 0
        assert autojinja.path.Path(dir2).getctime  > 0
        assert autojinja.path.Path(file1).getctime > 0
        assert autojinja.path.Path(file2).getctime > 0
        assert autojinja.path.Path(file3).getctime > 0
        assert autojinja.path.Path(file4).getctime > 0

    def test_isabs(self):
        assert autojinja.path.Path("").isabs                     == False
        assert autojinja.path.Path("file.txt").isabs             == False
        assert autojinja.path.Path("/file.txt").isabs            == True
        assert autojinja.path.Path("C:/").isabs                  == True
        assert autojinja.path.Path("\\").isabs                   == True
        assert autojinja.path.Path("/dir1").isabs                == True
        assert autojinja.path.Path("/dir1\\").isabs              == True
        assert autojinja.path.Path("/dir1/file.txt").isabs       == True
        assert autojinja.path.Path("/dir1\\dir2/file.txt").isabs == True

    def test_isfile(self):
        assert autojinja.path.Path(root) .isfile == False
        assert autojinja.path.Path(dir1) .isfile == False
        assert autojinja.path.Path(dir2) .isfile == False
        assert autojinja.path.Path(file1).isfile == True
        assert autojinja.path.Path(file2).isfile == True
        assert autojinja.path.Path(file3).isfile == True
        assert autojinja.path.Path(file4).isfile == True
        assert autojinja.path.Path(root.join("dummy")).isfile == False
        assert autojinja.path.Path(dir1.join("dummy")).isfile == False
        assert autojinja.path.Path(dir2.join("dummy")).isfile == False
        assert autojinja.path.Path(file1.join("dummy")).isfile == False
        assert autojinja.path.Path(file2.join("dummy")).isfile == False
        assert autojinja.path.Path(file3.join("dummy")).isfile == False
        assert autojinja.path.Path(file4.join("dummy")).isfile == False

    def test_isdir(self):
        assert autojinja.path.Path(root) .isdir == True
        assert autojinja.path.Path(dir1) .isdir == True
        assert autojinja.path.Path(dir2) .isdir == True
        assert autojinja.path.Path(file1).isdir == False
        assert autojinja.path.Path(file2).isdir == False
        assert autojinja.path.Path(file3).isdir == False
        assert autojinja.path.Path(file4).isdir == False
        assert autojinja.path.Path(root.join("dummy")).isdir == False
        assert autojinja.path.Path(dir1.join("dummy")).isdir == False
        assert autojinja.path.Path(dir2.join("dummy")).isdir == False
        assert autojinja.path.Path(file1.join("dummy")).isdir == False
        assert autojinja.path.Path(file2.join("dummy")).isdir == False
        assert autojinja.path.Path(file3.join("dummy")).isdir == False
        assert autojinja.path.Path(file4.join("dummy")).isdir == False

    def test_islink(self):
        assert autojinja.path.Path(root).islink  == False
        assert autojinja.path.Path(dir1).islink  == False
        assert autojinja.path.Path(dir2).islink  == False
        assert autojinja.path.Path(file1).islink == False
        assert autojinja.path.Path(file2).islink == False
        assert autojinja.path.Path(file3).islink == False
        assert autojinja.path.Path(file4).islink == False

    def test_ismount(self):
        assert autojinja.path.Path(root).ismount  == False
        assert autojinja.path.Path(dir1).ismount  == False
        assert autojinja.path.Path(dir2).ismount  == False
        assert autojinja.path.Path(file1).ismount == False
        assert autojinja.path.Path(file2).ismount == False
        assert autojinja.path.Path(file3).ismount == False
        assert autojinja.path.Path(file4).ismount == False

    def test_normcase(self):
        assert autojinja.path.Path("").normcase                     == ""
        assert autojinja.path.Path("file.txt").normcase             == "file.txt"
        assert autojinja.path.Path("/file.txt").normcase            == "/file.txt"
        assert autojinja.path.Path("C:/").normcase                  == "c:/"
        assert autojinja.path.Path("\\").normcase                   == "/"
        assert autojinja.path.Path("/dir1").normcase                == "/dir1"
        assert autojinja.path.Path("/dir1\\").normcase              == "/dir1/"
        assert autojinja.path.Path("/dir1/file.txt").normcase       == "/dir1/file.txt"
        assert autojinja.path.Path("/dir1\\dir2/file.txt").normcase == "/dir1/dir2/file.txt"

    def test_normpath(self):
        assert autojinja.path.Path("").normpath                     == ""
        assert autojinja.path.Path("file.txt").normpath             == "file.txt"
        assert autojinja.path.Path("/file.txt").normpath            == "/file.txt"
        assert autojinja.path.Path("C:/").normpath                  == "C:/"
        assert autojinja.path.Path("\\").normpath                   == "/"
        assert autojinja.path.Path("/dir1").normpath                == "/dir1"
        assert autojinja.path.Path("/dir1\\").normpath              == "/dir1/"
        assert autojinja.path.Path("/dir1/file.txt").normpath       == "/dir1/file.txt"
        assert autojinja.path.Path("/dir1\\dir2/file.txt").normpath == "/dir1/dir2/file.txt"

    def test_realpath(self):
        assert len(autojinja.path.Path("").realpath)                     >= len("")
        assert len(autojinja.path.Path("file.txt").realpath)             >= len("file.txt")
        assert len(autojinja.path.Path("/file.txt").realpath)            >= len("/file.txt")
        assert len(autojinja.path.Path("C:/").realpath)                  >= len("C:/")
        assert len(autojinja.path.Path("\\").realpath)                   >= len("/")
        assert len(autojinja.path.Path("/dir1").realpath)                >= len("/dir1")
        assert len(autojinja.path.Path("/dir1\\").realpath)              >= len("/dir1/")
        assert len(autojinja.path.Path("/dir1/file.txt").realpath)       >= len("/dir1/file.txt")
        assert len(autojinja.path.Path("/dir1\\dir2/file.txt").realpath) >= len("/dir1/dir2/file.txt" )

    def test_samefile(self):
        assert autojinja.path.Path(root).samefile(root) == True
        assert autojinja.path.Path(root).samefile(file1) == False

    def test_samestat(self):
        assert autojinja.path.Path(root).samestat(os.stat(root)) == True
        assert autojinja.path.Path(root).samestat(os.stat(file1)) == False

    def test_splitpath(self):
        assert autojinja.path.Path("").splitpath                     == ("", "")
        assert autojinja.path.Path("file.txt").splitpath             == ("", "file.txt")
        assert autojinja.path.Path("/file.txt").splitpath            == ("/", "file.txt")
        assert autojinja.path.Path("C:/").splitpath                  == ("C:/", "")
        assert autojinja.path.Path("\\").splitpath                   == ("/", "")
        assert autojinja.path.Path("/dir1").splitpath                == ("/", "dir1")
        assert autojinja.path.Path("/dir1\\").splitpath              == ("/dir1", "")
        assert autojinja.path.Path("/dir1/file.txt").splitpath       == ("/dir1", "file.txt")
        assert autojinja.path.Path("/dir1\\dir2/file.txt").splitpath == ("/dir1/dir2", "file.txt")

    def test_splitdrive(self):
        assert autojinja.path.Path("").splitdrive                     == ("", "")
        assert autojinja.path.Path("file.txt").splitdrive             == ("", "file.txt")
        assert autojinja.path.Path("/file.txt").splitdrive            == ("", "/file.txt")
        assert autojinja.path.Path("C:/").splitdrive                  == ("C:", "/")
        assert autojinja.path.Path("\\").splitdrive                   == ("", "/")
        assert autojinja.path.Path("/dir1").splitdrive                == ("", "/dir1")
        assert autojinja.path.Path("/dir1\\").splitdrive              == ("", "/dir1/")
        assert autojinja.path.Path("/dir1/file.txt").splitdrive       == ("", "/dir1/file.txt")
        assert autojinja.path.Path("/dir1\\dir2/file.txt").splitdrive == ("", "/dir1/dir2/file.txt")

    def test_splitext(self):
        assert autojinja.path.Path("").splitext                     == ("", "")
        assert autojinja.path.Path("file.txt").splitext             == ("file", ".txt")
        assert autojinja.path.Path("/file.txt").splitext            == ("/file", ".txt")
        assert autojinja.path.Path("C:/").splitext                  == ("C:/", "")
        assert autojinja.path.Path("\\").splitext                   == ("/", "")
        assert autojinja.path.Path("/dir1").splitext                == ("/dir1", "")
        assert autojinja.path.Path("/dir1\\").splitext              == ("/dir1/", "")
        assert autojinja.path.Path("/dir1/file.txt").splitext       == ("/dir1/file", ".txt")
        assert autojinja.path.Path("/dir1\\dir2/file.txt").splitext == ("/dir1/dir2/file", ".txt")

class TestModule:
    def test_call(self):
        assert autojinja.Path("")                     == ""
        assert autojinja.Path("file.txt")             == "file.txt"
        assert autojinja.Path("/file.txt")            == "/file.txt"
        assert autojinja.Path("C:/")                  == "C:/"
        assert autojinja.Path("\\")                   == "/"
        assert autojinja.Path("/dir1")                == "/dir1"
        assert autojinja.Path("/dir1\\")              == "/dir1/"
        assert autojinja.Path("/dir1/file.txt")       == "/dir1/file.txt"
        assert autojinja.Path("/dir1\\dir2/file.txt") == "/dir1/dir2/file.txt"

    def test_getitem(self):
        assert autojinja.Path[""]                     == "/"
        assert autojinja.Path["file.txt"]             == "file.txt/"
        assert autojinja.Path["/file.txt"]            == "/file.txt/"
        assert autojinja.Path["C:/"]                  == "C:/"
        assert autojinja.Path["\\"]                   == "/"
        assert autojinja.Path["/dir1"]                == "/dir1/"
        assert autojinja.Path["/dir1\\"]              == "/dir1/"
        assert autojinja.Path["/dir1/file.txt"]       == "/dir1/file.txt/"
        assert autojinja.Path["/dir1\\dir2/file.txt"] == "/dir1/dir2/file.txt/"
