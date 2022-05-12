import autojinja
import os
import tempfile

tmp = tempfile.TemporaryDirectory()
root = autojinja.path[tmp.name]
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

class TestPath:
    def test_join(self):
        assert autojinja.path("").join("file.txt")            == "file.txt"
        assert autojinja.path("/").join("file.txt")           == "/file.txt"
        assert autojinja.path("C:/").join("file.txt")         == "C:/file.txt"
        assert autojinja.path("/dir1").join("file.txt")       == "/dir1/file.txt"
        assert autojinja.path("\\dir1/").join("file.txt")     == "/dir1/file.txt"
        assert autojinja.path("/dir1\\dir2").join("file.txt") == "/dir1/dir2/file.txt"

    def test_join_brackets(self):
        assert autojinja.path("").join["file.txt"]                 == "file.txt/"
        assert autojinja.path("/").join["file.txt"]                == "/file.txt/"
        assert autojinja.path("C:/").join["file.txt"]              == "C:/file.txt/"
        assert autojinja.path("/dir1").join["file.txt", "a"]       == "/dir1/file.txt/a/"
        assert autojinja.path("\\dir1/").join["file.txt", "a"]     == "/dir1/file.txt/a/"
        assert autojinja.path("/dir1\\dir2").join["file.txt", "a"] == "/dir1/dir2/file.txt/a/"

    def test_add(self):
        assert autojinja.path("").add("file.txt")            == "file.txt"
        assert autojinja.path("/").add("file.txt")           == "/file.txt"
        assert autojinja.path("C:/").add("file.txt")         == "C:/file.txt"
        assert autojinja.path("\\dir1").add("file.txt")      == "/dir1file.txt"
        assert autojinja.path("/dir1/").add("file.txt")      == "/dir1/file.txt"
        assert autojinja.path("/dir1\\dir2").add("file.txt") == "/dir1/dir2file.txt"

        assert autojinja.path("") + "file.txt"            == "file.txt"
        assert autojinja.path("/") + "file.txt"           == "/file.txt"
        assert autojinja.path("C:/") + "file.txt"         == "C:/file.txt"
        assert autojinja.path("\\dir1") + "file.txt"      == "/dir1file.txt"
        assert autojinja.path("/dir1/") + "file.txt"      == "/dir1/file.txt"
        assert autojinja.path("/dir1\\dir2") + "file.txt" == "/dir1/dir2file.txt"

        assert  "" + autojinja.path("file.txt")            == "file.txt"
        assert  "/" + autojinja.path("file.txt")           == "/file.txt"
        assert  "C:/" + autojinja.path("file.txt")         == "C:/file.txt"
        assert  "\\dir1" + autojinja.path("file.txt")      == "/dir1file.txt"
        assert  "/dir1/" + autojinja.path("file.txt")      == "/dir1/file.txt"
        assert  "/dir1\\dir2" + autojinja.path("file.txt") == "/dir1/dir2file.txt"

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
        assert autojinja.path("").filepath                     == ""
        assert autojinja.path("file.txt").filepath             == "file.txt"
        assert autojinja.path("/file.txt").filepath            == "/file.txt"
        assert autojinja.path("C:/").filepath                  == "C:/"
        assert autojinja.path("\\").filepath                   == "/"
        assert autojinja.path("/dir1\\").filepath              == "/dir1/"
        assert autojinja.path("/dir1/file.txt").filepath       == "/dir1/file.txt"
        assert autojinja.path("/dir1\\dir2/file.txt").filepath == "/dir1/dir2/file.txt"

    def test_filename(self):
        assert autojinja.path("").filename                     == ""
        assert autojinja.path("file.txt").filename             == "file.txt"
        assert autojinja.path("/file.txt").filename            == "file.txt"
        assert autojinja.path("C:/").filename                  == ""
        assert autojinja.path("\\").filename                   == ""
        assert autojinja.path("/dir1\\").filename              == ""
        assert autojinja.path("/dir1/file.txt").filename       == "file.txt"
        assert autojinja.path("/dir1\\dir2/file.txt").filename == "file.txt"

    def test_set_filename(self):
        assert autojinja.path("").set_filename("new.md")                     == "new.md"
        assert autojinja.path("file.txt").set_filename("new.md")             == "new.md"
        assert autojinja.path("/").set_filename("new.md")                    == "/new.md"
        assert autojinja.path("C:/").set_filename("new.md")                  == "C:/new.md"
        assert autojinja.path("\\").set_filename("new.md")                   == "/new.md"
        assert autojinja.path("/dir1\\").set_filename("new.md")              == "/dir1/new.md"
        assert autojinja.path("/dir1/file.txt").set_filename("new.md")       == "/dir1/new.md"
        assert autojinja.path("/dir1\\dir2/file.txt").set_filename("new.md") == "/dir1/dir2/new.md"

    def test_dirpath(self):
        if os.name != "nt": # Unix
            assert autojinja.path("").dirpath                     == ""
            assert autojinja.path("file.txt").dirpath             == ""
            assert autojinja.path("/file.txt").dirpath            == "/"
            assert autojinja.path("C:").dirpath                   == ""
            assert autojinja.path("C:/").dirpath                  == "C:/"
            assert autojinja.path("/").dirpath                    == "/"
            assert autojinja.path("\\").dirpath                   == "/"
            assert autojinja.path("/dir1").dirpath                == "/"
            assert autojinja.path("/dir1/").dirpath               == "/dir1/"
            assert autojinja.path("/dir1\\ab").dirpath            == "/dir1/"
            assert autojinja.path("/dir1/file.txt").dirpath       == "/dir1/"
            assert autojinja.path("/dir1\\dir2/file.txt").dirpath == "/dir1/dir2/"
        else: # Windows
            assert autojinja.path("").dirpath                     == ""
            assert autojinja.path("file.txt").dirpath             == ""
            assert autojinja.path("/file.txt").dirpath            == "/"
            assert autojinja.path("C:").dirpath                   == "C:/"
            assert autojinja.path("C:/").dirpath                  == "C:/"
            assert autojinja.path("/").dirpath                    == "/"
            assert autojinja.path("\\").dirpath                   == "/"
            assert autojinja.path("/dir1").dirpath                == "/"
            assert autojinja.path("/dir1/").dirpath               == "/dir1/"
            assert autojinja.path("/dir1\\ab").dirpath            == "/dir1/"
            assert autojinja.path("/dir1/file.txt").dirpath       == "/dir1/"
            assert autojinja.path("/dir1\\dir2/file.txt").dirpath == "/dir1/dir2/"

    def test_dirname(self):
        if os.name != "nt": # Unix
            assert autojinja.path("").dirname                     == ""
            assert autojinja.path("file.txt").dirname             == ""
            assert autojinja.path("/file.txt").dirname            == ""
            assert autojinja.path("C:").dirname                   == ""
            assert autojinja.path("C:/").dirname                  == "C:"
            assert autojinja.path("/").dirname                    == ""
            assert autojinja.path("\\").dirname                   == ""
            assert autojinja.path("/dir1").dirname                == ""
            assert autojinja.path("/dir1/").dirname               == "dir1"
            assert autojinja.path("/dir1\\").dirname              == "dir1"
            assert autojinja.path("/dir1/file.txt").dirname       == "dir1"
            assert autojinja.path("/dir1\\dir2/file.txt").dirname == "dir2"
        else: # Windows
            assert autojinja.path("").dirname                     == ""
            assert autojinja.path("file.txt").dirname             == ""
            assert autojinja.path("/file.txt").dirname            == ""
            assert autojinja.path("C:").dirname                   == "C:"
            assert autojinja.path("C:/").dirname                  == "C:"
            assert autojinja.path("/").dirname                    == ""
            assert autojinja.path("\\").dirname                   == ""
            assert autojinja.path("/dir1").dirname                == ""
            assert autojinja.path("/dir1/").dirname               == "dir1"
            assert autojinja.path("/dir1\\").dirname              == "dir1"
            assert autojinja.path("/dir1/file.txt").dirname       == "dir1"
            assert autojinja.path("/dir1\\dir2/file.txt").dirname == "dir2"

    def test_parent_dirpath(self):
        if os.name != "nt": # Unix
            assert autojinja.path("").parent_dirpath                     == ""
            assert autojinja.path("file.txt").parent_dirpath             == ""
            assert autojinja.path("/file.txt").parent_dirpath            == "/"
            assert autojinja.path("C:").parent_dirpath                   == ""
            assert autojinja.path("C:/").parent_dirpath                  == ""
            assert autojinja.path("/").parent_dirpath                    == "/"
            assert autojinja.path("\\").parent_dirpath                   == "/"
            assert autojinja.path("/dir1").parent_dirpath                == "/"
            assert autojinja.path("/dir1/").parent_dirpath               == "/"
            assert autojinja.path("/dir1\\").parent_dirpath              == "/"
            assert autojinja.path("/dir1/file.txt").parent_dirpath       == "/"
            assert autojinja.path("/dir1\\dir2/file.txt").parent_dirpath == "/dir1/"
        else: # Windows
            assert autojinja.path("").parent_dirpath                     == ""
            assert autojinja.path("file.txt").parent_dirpath             == ""
            assert autojinja.path("/file.txt").parent_dirpath            == "/"
            assert autojinja.path("C:").parent_dirpath                   == "C:/"
            assert autojinja.path("C:/").parent_dirpath                  == "C:/"
            assert autojinja.path("/").parent_dirpath                    == "/"
            assert autojinja.path("\\").parent_dirpath                   == "/"
            assert autojinja.path("/dir1").parent_dirpath                == "/"
            assert autojinja.path("/dir1/").parent_dirpath               == "/"
            assert autojinja.path("/dir1\\").parent_dirpath              == "/"
            assert autojinja.path("/dir1/file.txt").parent_dirpath       == "/"
            assert autojinja.path("/dir1\\dir2/file.txt").parent_dirpath == "/dir1/"

    def test_parent_dirname(self):
        if os.name != "nt": # Unix
            assert autojinja.path("").parent_dirname                     == ""
            assert autojinja.path("file.txt").parent_dirname             == ""
            assert autojinja.path("/file.txt").parent_dirname            == ""
            assert autojinja.path("C:").parent_dirname                   == ""
            assert autojinja.path("C:/").parent_dirname                  == ""
            assert autojinja.path("/").parent_dirname                    == ""
            assert autojinja.path("\\").parent_dirname                   == ""
            assert autojinja.path("/dir1").parent_dirname                == ""
            assert autojinja.path("/dir1/").parent_dirname               == ""
            assert autojinja.path("/dir1\\").parent_dirname              == ""
            assert autojinja.path("/dir1/file.txt").parent_dirname       == ""
            assert autojinja.path("/dir1\\dir2/file.txt").parent_dirname == "dir1"
        else: # Windows
            assert autojinja.path("").parent_dirname                     == ""
            assert autojinja.path("file.txt").parent_dirname             == ""
            assert autojinja.path("/file.txt").parent_dirname            == ""
            assert autojinja.path("C:").parent_dirname                   == "C:"
            assert autojinja.path("C:/").parent_dirname                  == "C:"
            assert autojinja.path("/").parent_dirname                    == ""
            assert autojinja.path("\\").parent_dirname                   == ""
            assert autojinja.path("/dir1").parent_dirname                == ""
            assert autojinja.path("/dir1/").parent_dirname               == ""
            assert autojinja.path("/dir1\\").parent_dirname              == ""
            assert autojinja.path("/dir1/file.txt").parent_dirname       == ""
            assert autojinja.path("/dir1\\dir2/file.txt").parent_dirname == "dir1"

    def test_ext(self):
        assert autojinja.path("").ext                     == ""
        assert autojinja.path("file.ext.txt").ext         == ".txt"
        assert autojinja.path("/file.ext.txt").ext        == ".txt"
        assert autojinja.path("C:/").ext                  == ""
        assert autojinja.path("\\").ext                   == ""
        assert autojinja.path("/dir1").ext                == ""
        assert autojinja.path("/dir1\\").ext              == ""
        assert autojinja.path("/dir1/file.txt").ext       == ".txt"
        assert autojinja.path("/dir1\\dir2/file.txt").ext == ".txt"

    def test_set_ext(self):
        assert autojinja.path("").set_ext(".md")                     == ".md"
        assert autojinja.path("file.ext.txt").set_ext(".md")         == "file.ext.md"
        assert autojinja.path("/file.ext.txt").set_ext(".md")        == "/file.ext.md"
        assert autojinja.path("C:/").set_ext(".md")                  == "C:/.md"
        assert autojinja.path("\\").set_ext(".md")                   == "/.md"
        assert autojinja.path("/dir1").set_ext(".md")                == "/dir1.md"
        assert autojinja.path("/dir1\\").set_ext(".md")              == "/dir1/.md"
        assert autojinja.path("/dir1/file.txt").set_ext(".md")       == "/dir1/file.md"
        assert autojinja.path("/dir1\\dir2/file.txt").set_ext(".md") == "/dir1/dir2/file.md"

    def test_no_ext(self):
        assert autojinja.path("").no_ext                     == ""
        assert autojinja.path("file.txt").no_ext             == "file"
        assert autojinja.path("/file.txt").no_ext            == "/file"
        assert autojinja.path("/file.ext.txt").no_ext        == "/file.ext"
        assert autojinja.path("C:/").no_ext                  == "C:/"
        assert autojinja.path("\\").no_ext                   == "/"
        assert autojinja.path("/dir1").no_ext                == "/dir1"
        assert autojinja.path("/dir1\\").no_ext              == "/dir1/"
        assert autojinja.path("/dir1/file.txt").no_ext       == "/dir1/file"
        assert autojinja.path("/dir1\\dir2/file.txt").no_ext == "/dir1/dir2/file"

    def test_fullext(self):
        assert autojinja.path("").fullext                     == ""
        assert autojinja.path("file.ext.txt").fullext         == ".ext.txt"
        assert autojinja.path("/file.ext.txt").fullext        == ".ext.txt"
        assert autojinja.path("C:/").fullext                  == ""
        assert autojinja.path("\\").fullext                   == ""
        assert autojinja.path("/dir1").fullext                == ""
        assert autojinja.path("/dir1\\").fullext              == ""
        assert autojinja.path("/dir1/file").fullext           == ""
        assert autojinja.path("/dir1\\dir2/file.txt").fullext == ".txt"

    def test_set_fullext(self):
        assert autojinja.path("").set_fullext(".md")                     == ".md"
        assert autojinja.path("file.ext.txt").set_fullext(".md")         == "file.md"
        assert autojinja.path("/file.ext.txt").set_fullext(".md")        == "/file.md"
        assert autojinja.path("C:/").set_fullext(".md")                  == "C:/.md"
        assert autojinja.path("\\").set_fullext(".md")                   == "/.md"
        assert autojinja.path("/dir1").set_fullext(".md")                == "/dir1.md"
        assert autojinja.path("/dir1\\").set_fullext(".md")              == "/dir1/.md"
        assert autojinja.path("/dir1/file").set_fullext(".md")           == "/dir1/file.md"
        assert autojinja.path("/dir1\\dir2/file.txt").set_fullext(".md") == "/dir1/dir2/file.md"

    def test_no_fullext(self):
        assert autojinja.path("").no_fullext                     == ""
        assert autojinja.path("file.txt").no_fullext             == "file"
        assert autojinja.path("/file.txt").no_fullext            == "/file"
        assert autojinja.path("/file.ext.txt").no_fullext        == "/file"
        assert autojinja.path("C:/").no_fullext                  == "C:/"
        assert autojinja.path("\\").no_fullext                   == "/"
        assert autojinja.path("/dir1").no_fullext                == "/dir1"
        assert autojinja.path("/dir1\\").no_fullext              == "/dir1/"
        assert autojinja.path("/dir1/file").no_fullext           == "/dir1/file"
        assert autojinja.path("/dir1\\dir2/file.txt").no_fullext == "/dir1/dir2/file"

    def test_slash(self):
        assert autojinja.path("").slash                     == "/"
        assert autojinja.path("file.txt").slash             == "file.txt/"
        assert autojinja.path("/file.txt").slash            == "/file.txt/"
        assert autojinja.path("C:/").slash                  == "C:/"
        assert autojinja.path("\\").slash                   == "/"
        assert autojinja.path("/dir1").slash                == "/dir1/"
        assert autojinja.path("/dir1\\").slash              == "/dir1/"
        assert autojinja.path("/dir1/file.txt").slash       == "/dir1/file.txt/"
        assert autojinja.path("/dir1\\dir2/file.txt").slash == "/dir1/dir2/file.txt/"

    def test_no_slash(self):
        assert autojinja.path("").no_slash                     == ""
        assert autojinja.path("file.txt").no_slash             == "file.txt"
        assert autojinja.path("/file.txt").no_slash            == "/file.txt"
        assert autojinja.path("C:/").no_slash                  == "C:"
        assert autojinja.path("\\").no_slash                   == ""
        assert autojinja.path("/dir1").no_slash                == "/dir1"
        assert autojinja.path("/dir1\\").no_slash              == "/dir1"
        assert autojinja.path("/dir1/file.txt").no_slash       == "/dir1/file.txt"
        assert autojinja.path("/dir1\\dir2/file.txt").no_slash == "/dir1/dir2/file.txt"

class TestModule:
    def test_call(self):
        assert autojinja.path("")                     == ""
        assert autojinja.path("file.txt")             == "file.txt"
        assert autojinja.path("/file.txt")            == "/file.txt"
        assert autojinja.path("C:/")                  == "C:/"
        assert autojinja.path("\\")                   == "/"
        assert autojinja.path("/dir1")                == "/dir1"
        assert autojinja.path("/dir1\\")              == "/dir1/"
        assert autojinja.path("/dir1/file.txt")       == "/dir1/file.txt"
        assert autojinja.path("/dir1\\dir2/file.txt") == "/dir1/dir2/file.txt"

    def test_getitem(self):
        assert autojinja.path[""]                     == "/"
        assert autojinja.path["file.txt"]             == "file.txt/"
        assert autojinja.path["/file.txt"]            == "/file.txt/"
        assert autojinja.path["C:/"]                  == "C:/"
        assert autojinja.path["\\"]                   == "/"
        assert autojinja.path["/dir1"]                == "/dir1/"
        assert autojinja.path["/dir1\\"]              == "/dir1/"
        assert autojinja.path["/dir1/file.txt"]       == "/dir1/file.txt/"
        assert autojinja.path["/dir1\\dir2/file.txt"] == "/dir1/dir2/file.txt/"

    def test_getattribute(self):
        # dir
        assert dir1.isdir  == True
        assert dir2.isdir  == True
        assert file1.isdir == False
        assert file2.isdir == False
        assert file3.isdir == False
        assert file4.isdir == False
        # file
        assert dir1.isfile  == False
        assert dir2.isfile  == False
        assert file1.isfile == True
        assert file2.isfile == True
        assert file3.isfile == True
        assert file4.isfile == True
