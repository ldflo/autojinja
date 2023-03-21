from . import assert_exception

import autojinja
import jinja2
import os
import sys

def invalid_marker(input: str, output: str, exception_type: type, message: str, *args: str, **kwargs: str):
    def function(*args: str, **kwargs: str):
        template = autojinja.CogTemplate.from_string(input)
        template.context(*args, **kwargs).render(output)
    assert_exception(function, exception_type, message, *args, **kwargs)

class Test_OpenMarkerNotFoundException:
    def test_1(self):
        input = "[[[end]]]"
        msg   = "Couldn't find corresponding open marker \"[[[ ]]]\":\n" \
                "[[[end]]]\\0\n" \
                "^^^ line 1, column 1"
        invalid_marker(input, None, autojinja.exceptions.OpenMarkerNotFoundException, msg)

    def test_2(self):
        input = "[[[end]]] [[[abc]]]"
        msg   = "Couldn't find corresponding open marker \"[[[ ]]]\":\n" \
                "[[[end]]] [[[abc]]]\\0\n" \
                "^^^ line 1, column 1"
        invalid_marker(input, None, autojinja.exceptions.OpenMarkerNotFoundException, msg)

    def test_3(self):
        input = "[[[abc]]] [[[end]]] [[[end]]]"
        msg   = "Couldn't find corresponding open marker \"[[[ ]]]\":\n" \
                "[[[abc]]] [[[end]]] [[[end]]]\\0\n" \
                "                    ^^^ line 1, column 21"
        invalid_marker(input, None, autojinja.exceptions.OpenMarkerNotFoundException, msg)

    def test_4(self):
        input = "[[[<<[end]>>]]]  [[[end]]]"
        msg = "\n  During generation of \"[[[ <<[end]>> ]]]\" at line 1, column 1\n" \
                "Couldn't find corresponding open marker \"<<[ ]>>\":\n" \
                "<<[end]>>\\0\n" \
                "^^^ line 1, column 1"
        invalid_marker(input, None, autojinja.exceptions.OpenMarkerNotFoundException, msg)

    def test_5(self):
        input = "[[[ <<[ a ]>> <<[ end ]>> ]]]\n" \
                "<<[ a ]>>\n" \
                "    [[[ <<[ end ]>> ]]]\n" \
                "    [[[ end ]]]\n" \
                "<<[ end ]>>\n" \
                "[[[end]]]\n"
        msg = "\n  During generation of \"[[[ <<[ a ]>> <<[ end ]>> ]]]\" at line 1, column 1\n" \
                "  During reinsertion of \"<<[ a ]>>\" at line 1, column 1\n" \
                "  During generation of \"[[[ <<[ end ]>> ]]]\" at line 1, column 5\n" \
                "Couldn't find corresponding open marker \"<<[ ]>>\":\n" \
                "<<[ end ]>>\\0\n" \
                "^^^ line 1, column 1"
        invalid_marker(input, None, autojinja.exceptions.OpenMarkerNotFoundException, msg)

    def test_6(self):
        input = "[[[\n" \
                "  <<[ a ]>>\n" \
                "  <<[ end ]>>\n" \
                "]]]\n" \
                "<<[ a ]>>\n" \
                "    [[[ <<[ end ]>> ]]]\n" \
                "    [[[ end ]]]\n" \
                "<<[ end ]>>\n" \
                "[[[end]]]\n"
        msg = "\n  During generation of \"[[[   <<[ a ]>>\\n  <<[ end ]>> ]]]\" at line 1, column 1\n" \
                "  During reinsertion of \"<<[ a ]>>\" at line 1, column 3\n" \
                "  During generation of \"[[[ <<[ end ]>> ]]]\" at line 1, column 5\n" \
                "Couldn't find corresponding open marker \"<<[ ]>>\":\n" \
                "<<[ end ]>>\\0\n" \
                "^^^ line 1, column 1"
        invalid_marker(input, None, autojinja.exceptions.OpenMarkerNotFoundException, msg)

class Test_CloseMarkerNotFoundException:
    def test_1(self):
        input = "[[[ abc "
        msg   = "Couldn't find corresponding close marker \"]]]\":\n" \
                "[[[ abc \\0\n" \
                "^^^ line 1, column 1"
        invalid_marker(input, None, autojinja.exceptions.CloseMarkerNotFoundException, msg)

    def test_2(self):
        input = "<<["
        msg   = "Couldn't find corresponding close marker \"]>>\":\n" \
                "<<[\\0\n" \
                "^^^ line 1, column 1"
        invalid_marker(input, None, autojinja.exceptions.CloseMarkerNotFoundException, msg)

    def test_3(self):
        input = "[[[ <<[ a ]>> <<[ end ]>> ]]]\n" \
                "<<[ a\n" \
                "    [[[ ]]]\n" \
                "    [[[ end ]]]\n" \
                "<<[ end ]>>\n" \
                "[[[end]]]\n"
        msg   = "Couldn't find corresponding close marker \"]>>\":\n" \
                "<<[ a\\n\n" \
                "^^^ line 2, column 1"
        invalid_marker(input, None, autojinja.exceptions.CloseMarkerNotFoundException, msg)

    def test_4(self):
        input = "[[[ <<[ a ]]]\n" \
                "<<[ a ]>>\n" \
                "    [[[ ]]]\n" \
                "    [[[ end ]]]\n" \
                "<<[ end ]>>\n" \
                "[[[end]]]\n"
        msg = "\n  During generation of \"[[[ <<[ a ]]]\" at line 1, column 1\n" \
                "Couldn't find corresponding close marker \"]>>\":\n" \
                "<<[ a\\0\n" \
                "^^^ line 1, column 1"
        invalid_marker(input, None, autojinja.exceptions.CloseMarkerNotFoundException, msg)

class Test_EndMarkerNotFoundException:
    def test_1(self):
        input = "[[[]]] abc"
        msg   = "Couldn't find corresponding end marker \"[[[ end ]]]\":\n" \
                "[[[]]] abc\\0\n" \
                "   ^^^ line 1, column 4"
        invalid_marker(input, None, autojinja.exceptions.EndMarkerNotFoundException, msg)

    def test_2(self):
        input = "[[[]]] abc [[[  end  ]]]"
        msg   = "Couldn't find corresponding end marker \"[[[ end ]]]\":\n" \
                "[[[]]] abc [[[  end  ]]]\\0\n" \
                "                     ^^^ line 1, column 22"
        invalid_marker(input, None, autojinja.exceptions.EndMarkerNotFoundException, msg)

    def test_3(self):
        input = "[[[]]] abc [[[ any ]]]"
        msg   = "Couldn't find corresponding end marker \"[[[ end ]]]\":\n" \
                "[[[]]] abc [[[ any ]]]\\0\n" \
                "                   ^^^ line 1, column 20"
        invalid_marker(input, None, autojinja.exceptions.EndMarkerNotFoundException, msg)

    def test_4(self):
        input = "[[[]]] abc [[[dne]]] [[[end]]]"
        msg   = "Couldn't find corresponding end marker \"[[[ end ]]]\":\n" \
                "[[[]]] abc [[[dne]]] [[[end]]]\\0\n" \
                "   ^^^ line 1, column 4"
        invalid_marker(input, None, autojinja.exceptions.EndMarkerNotFoundException, msg)

    def test_5(self):
        input = "[[[]]] abc [[[dne]]] [[[zde]]] [[[end]]]"
        msg   = "Couldn't find corresponding end marker \"[[[ end ]]]\":\n" \
                "[[[]]] abc [[[dne]]] [[[zde]]] [[[end]]]\\0\n" \
                "                 ^^^ line 1, column 18"
        invalid_marker(input, None, autojinja.exceptions.EndMarkerNotFoundException, msg)

    def test_6(self):
        input = "[[[]]]\n" \
                "    [[[ a ]]]\n" \
                "[[[end]]]\n"
        msg   = "Couldn't find corresponding end marker \"[[[ end ]]]\":\n" \
                "[[[]]]\\n\n" \
                "   ^^^ line 1, column 4"
        invalid_marker(input, None, autojinja.exceptions.EndMarkerNotFoundException, msg)

    def test_7(self):
        input = "[[[]]]\n" \
                "    [[[ a ]]]\n" \
                "[[[end]]]\n"
        msg   = "Couldn't find corresponding end marker \"[[[ end ]]]\":\n" \
                "[[[]]]\\n\n" \
                "   ^^^ line 1, column 4"
        invalid_marker(input, None, autojinja.exceptions.EndMarkerNotFoundException, msg)

    def test_8(self):
        input = "[[[]]]\n" \
                "    [[[ a ]]]\n" \
                "    [[[zde]]]\n" \
                "[[[end]]]\n"
        msg   = "Couldn't find corresponding end marker \"[[[ end ]]]\":\n" \
                "    [[[ a ]]]\\n\n" \
                "          ^^^ line 2, column 11"
        invalid_marker(input, None, autojinja.exceptions.EndMarkerNotFoundException, msg)

    def test_9(self): # HEADER ILLFORMED
        input = "[[[\n" \
                "    [[[ a ]]]\n" \
                "    [[[zde]]]\n" \
                "]]]\n" \
                "    [[[ a ]]]\n" \
                "    [[[zde]]]\n" \
                "[[[end]]]\n"
        msg   = "Couldn't find corresponding end marker \"[[[ end ]]]\":\n" \
                "    [[[ a ]]]\\n\n" \
                "          ^^^ line 5, column 11"
        invalid_marker(input, None, autojinja.exceptions.EndMarkerNotFoundException, msg)

    def test_10(self): # HEADER ILLFORMED
        input = "[[[\n" \
                "    [[[ a ]]]\n" \
                "    [[[zde]]]\n" \
                "]]]\n" \
                "[[[end]]]\n"
        msg   = "Couldn't find corresponding end marker \"[[[ end ]]]\":\n" \
                "    [[[ a ]]]\\n\n" \
                "          ^^^ line 2, column 11"
        invalid_marker(input, None, autojinja.exceptions.EndMarkerNotFoundException, msg)

    def test_11(self):
        input = "<<[]>> abc"
        msg   = "Couldn't find corresponding end marker \"<<[ end ]>>\":\n" \
                "<<[]>> abc\\0\n" \
                "   ^^^ line 1, column 4"
        invalid_marker(input, None, autojinja.exceptions.EndMarkerNotFoundException, msg)

    def test_12(self):
        input = "<<[]>>\n" \
                "abc"
        msg   = "Couldn't find corresponding end marker \"<<[ end ]>>\":\n" \
                "<<[]>>\\n\n" \
                "   ^^^ line 1, column 4"
        invalid_marker(input, None, autojinja.exceptions.EndMarkerNotFoundException, msg)

    def test_13(self):
        input = "[[[ // <<[ a ]>> ]]]\n" \
                "[[[end]]]\n"
        msg = "\n  During generation of \"[[[ // <<[ a ]>> ]]]\" at line 1, column 1\n" \
                "Couldn't find corresponding end marker \"<<[ end ]>>\":\n" \
                "// <<[ a ]>>\\0\n" \
                "         ^^^ line 1, column 10"
        invalid_marker(input, None, autojinja.exceptions.EndMarkerNotFoundException, msg)

    def test_14(self):
        input = "[[[ <<[ a ]>> <<[ end ]>> ]]]\n" \
                "<<[ a ]>> [[[ <<[ b ]>> ]]] [[[ end ]]] <<[ end ]>>\n" \
                "[[[end]]]\n"
        msg = "\n  During generation of \"[[[ <<[ a ]>> <<[ end ]>> ]]]\" at line 1, column 1\n" \
                "  During reinsertion of \"<<[ a ]>>\" at line 1, column 1\n" \
                "  During generation of \"[[[ <<[ b ]>> ]]]\" at line 1, column 1\n" \
                "Couldn't find corresponding end marker \"<<[ end ]>>\":\n" \
                "<<[ b ]>>\\0\n" \
                "      ^^^ line 1, column 7"
        invalid_marker(input, None, autojinja.exceptions.EndMarkerNotFoundException, msg)

    def test_15(self):
        input = "[[[ <<[ a ]>> <<[ end ]>> ]]]\n" \
                "<<[ a ]>>\n" \
                "    [[[ <<[ b ]>> ]]]\n" \
                "    [[[ end ]]]\n" \
                "<<[ end ]>>\n" \
                "[[[end]]]\n"
        msg = "\n  During generation of \"[[[ <<[ a ]>> <<[ end ]>> ]]]\" at line 1, column 1\n" \
                "  During reinsertion of \"<<[ a ]>>\" at line 1, column 1\n" \
                "  During generation of \"[[[ <<[ b ]>> ]]]\" at line 1, column 5\n" \
                "Couldn't find corresponding end marker \"<<[ end ]>>\":\n" \
                "<<[ b ]>>\\0\n" \
                "      ^^^ line 1, column 7"
        invalid_marker(input, None, autojinja.exceptions.EndMarkerNotFoundException, msg)

class Test_RequireHeaderInlineException:
    def test_1(self):
        input = " <<[\n" \
                "]>>\n" \
                "<<[ end ]>>"
        msg   = "Marker can't have a multiline header:\n" \
                " <<[\\n\n" \
                " ^^^ line 1, column 2"
        invalid_marker(input, None, autojinja.exceptions.RequireHeaderInlineException, msg)

    def test_2(self):
        input = " <<[\n" \
                "a\n" \
                " ]>>\n" \
                "<<[ end ]>>"
        msg   = "Marker can't have a multiline header:\n" \
                " <<[\\n\n" \
                " ^^^ line 1, column 2"
        invalid_marker(input, None, autojinja.exceptions.RequireHeaderInlineException, msg)

    def test_3(self):
        input = "// <<[\n" \
                "//]>>\n" \
                "<<[ end ]>>"
        msg   = "Marker can't have a multiline header:\n" \
                "// <<[\\n\n" \
                "   ^^^ line 1, column 4"
        invalid_marker(input, None, autojinja.exceptions.RequireHeaderInlineException, msg)

    def test_4(self):
        input = "[[[\n" \
                "  <<[\n" \
                "  a\n" \
                "  ]>>\n" \
                "  <<[ end ]>>\n" \
                "]]]\n" \
                "<<[ a ]>>\n" \
                "<<[ end ]>>\n" \
                "[[[end]]]\n"
        msg = "\n  During generation of \"[[[   <<[\\n  a\\n  ]>>\\n  <<[ end ]>> ]]]\" at line 1, column 1\n" \
                "Marker can't have a multiline header:\n" \
                "  <<[\\n\n" \
                "  ^^^ line 1, column 3"
        invalid_marker(input, None, autojinja.exceptions.RequireHeaderInlineException, msg)

class RequireHeaderMultilineException:
    pass # Never reached

class Test_WrongHeaderIndentationException:
    def test_1(self):
        input = " [[[\n" \
                "]]]\n" \
                "[[[ end ]]]"
        msg   = "Wrong marker header indentation:\n" \
                "]]]\\n\n" \
                "^^^ line 2, column 1"
        invalid_marker(input, None, autojinja.exceptions.WrongHeaderIndentationException, msg)

    def test_2(self):
        input = " [[[\n" \
                "a\n" \
                " ]]]\n" \
                "[[[ end ]]]"
        msg   = "Wrong marker header indentation:\n" \
                "a\\n\n" \
                "^^^ line 2, column 1"
        invalid_marker(input, None, autojinja.exceptions.WrongHeaderIndentationException, msg)

    def test_3(self):
        input = "// [[[\n" \
                "//]]]\n" \
                "[[[ end ]]]"
        msg   = "Wrong marker header indentation:\n" \
                "//]]]\\n\n" \
                "  ^^^ line 2, column 3"
        invalid_marker(input, None, autojinja.exceptions.WrongHeaderIndentationException, msg)

    def test_4(self):
        input = "// [[[\n" \
                "//a\n" \
                "// ]]]\n" \
                "[[[ end ]]]"
        msg   = "Wrong marker header indentation:\n" \
                "//a\\n\n" \
                "  ^^^ line 2, column 3"
        invalid_marker(input, None, autojinja.exceptions.WrongHeaderIndentationException, msg)

    def test_5(self):
        input = "// [[[\n" \
                "//]]]\n" \
                "[[[ end ]]]"
        msg   = "Wrong marker header indentation:\n" \
                "//]]]\\n\n" \
                "  ^^^ line 2, column 3"
        invalid_marker(input, None, autojinja.exceptions.WrongHeaderIndentationException, msg)

    def test_6(self):
        input = "  [[[\n" \
                "//\n" \
                "  ]]]\n" \
                "[[[ end ]]]"
        msg   = "Wrong marker header indentation:\n" \
                "//\\n\n" \
                "^^^ line 2, column 1"
        invalid_marker(input, None, autojinja.exceptions.WrongHeaderIndentationException, msg)

    def test_7(self):
        input = " // [[[\n" \
                " //]]]\n" \
                "[[[ end ]]]"
        msg   = "Wrong marker header indentation:\n" \
                " //]]]\\n\n" \
                "   ^^^ line 2, column 4"
        invalid_marker(input, None, autojinja.exceptions.WrongHeaderIndentationException, msg)

    def test_8(self):
        input = " //  [[[\n" \
                " // a\n" \
                " //  ]]]\n" \
                "[[[ end ]]]"
        msg   = "Wrong marker header indentation:\n" \
                " // a\\n\n" \
                "    ^^^ line 2, column 5"
        invalid_marker(input, None, autojinja.exceptions.WrongHeaderIndentationException, msg)

    def test_9(self):
        input = " // [[[\n" \
                " //\t]]]\n" \
                "[[[ end ]]]"
        msg   = "Wrong marker header indentation:\n" \
                " //\t]]]\\n\n" \
                "   ^^^ line 2, column 4"
        invalid_marker(input, None, autojinja.exceptions.WrongHeaderIndentationException, msg)

    def test_10(self):
        input = " //\t [[[\n" \
                " //  a\n" \
                " //  ]]]\n" \
                "[[[ end ]]]"
        msg   = "Wrong marker header indentation:\n" \
                " //  a\\n\n" \
                "   ^^^ line 2, column 4"
        invalid_marker(input, None, autojinja.exceptions.WrongHeaderIndentationException, msg)

    def test_11(self):
        input = " // [[[\n" \
                " //\t]]]\n" \
                "[[[ end ]]]"
        msg   = "Wrong marker header indentation:\n" \
                " //\t]]]\\n\n" \
                "   ^^^ line 2, column 4"
        invalid_marker(input, None, autojinja.exceptions.WrongHeaderIndentationException, msg)

    def test_12(self):
        input = " // [[[\n" \
                " //\ta\n" \
                " // ]]]\n" \
                "[[[ end ]]]"
        msg   = "Wrong marker header indentation:\n" \
                " //\ta\\n\n" \
                "   ^^^ line 2, column 4"
        invalid_marker(input, None, autojinja.exceptions.WrongHeaderIndentationException, msg)

    def test_13(self):
        input = " // [[[\n" \
                "\t// ]]]\n" \
                "[[[ end ]]]"
        msg   = "Wrong marker header indentation:\n" \
                "\t// ]]]\\n\n" \
                "^^^ line 2, column 1"
        invalid_marker(input, None, autojinja.exceptions.WrongHeaderIndentationException, msg)

    def test_14(self):
        input = " // [[[\n" \
                " //\t]]]\n" \
                "[[[ end ]]]"
        msg   = "Wrong marker header indentation:\n" \
                " //\t]]]\\n\n" \
                "   ^^^ line 2, column 4"
        invalid_marker(input, None, autojinja.exceptions.WrongHeaderIndentationException, msg)

    def test_15(self):
        input = " // [[[\n" \
                " // a\n" \
                " \t  ]]]\n" \
                "[[[ end ]]]"
        msg   = "Wrong marker header indentation:\n" \
                " \t  ]]]\\n\n" \
                " ^^^ line 3, column 2"
        invalid_marker(input, None, autojinja.exceptions.WrongHeaderIndentationException, msg)

    def test_16(self):
        input = " // [[[\n" \
                " /\n" \
                "    ]]]\n" \
                "[[[ end ]]]"
        msg   = "Wrong marker header indentation:\n" \
                " /\\n\n" \
                "  ^^^ line 2, column 3"
        invalid_marker(input, None, autojinja.exceptions.WrongHeaderIndentationException, msg)

    def test_17(self):
        input = "[[[\n" \
                "    <<[ a ]>>\n" \
                "    <<[ end ]>>\n" \
                "]]]\n" \
                "<<[ a ]>>\n" \
                "    [[[\n" \
                "   abc\n" \
                "    ]]]\n" \
                "    [[[ end ]]]\n" \
                "<<[ end ]>>\n" \
                "[[[end]]]\n"
        msg   = "Wrong marker header indentation:\n" \
                "   abc\\n\n" \
                "   ^^^ line 7, column 4"
        invalid_marker(input, None, autojinja.exceptions.WrongHeaderIndentationException, msg)

class Test_RequireNewlineException:
    def test_1(self):
        input = "[[[ a ]]]\n" \
                "[[[ end ]]] [[[ a ]]] [[[ end ]]]"
        msg   = "Marker can't start on same line as previous end marker:\n" \
                "[[[ end ]]] [[[ a ]]] [[[ end ]]]\\0\n" \
                "            ^^^ line 2, column 13"
        invalid_marker(input, None, autojinja.exceptions.RequireNewlineException, msg)

    def test_2(self):
        input = "<<[ a ]>>\n" \
                "<<[ end ]>> <<[ a ]>> <<[ end ]>>"
        msg   = "Marker can't start on same line as previous end marker:\n" \
                "<<[ end ]>> <<[ a ]>> <<[ end ]>>\\0\n" \
                "            ^^^ line 2, column 13"
        invalid_marker(input, None, autojinja.exceptions.RequireNewlineException, msg)

    def test_3(self):
        input = "[[[  \n" \
                "    <<[ a ]>>\n" \
                "    <<[ end ]>> <<[ b ]>>\n" \
                "]]]\n" \
                "<<[ a ]>>\n" \
                "    [[[ <<[ b ]>> ]]]\n" \
                "    [[[ end ]]]\n" \
                "<<[ end ]>>\n" \
                "[[[end]]]\n"
        msg = "\n  During generation of \"[[[  \\n    <<[ a ]>>\\n    <<[ end ]>> <<[ b ]>> ]]]\" at line 1, column 1\n" \
                "Marker can't start on same line as previous end marker:\n" \
                "    <<[ end ]>> <<[ b ]>>\\0\n" \
                "                ^^^ line 3, column 17"
        invalid_marker(input, None, autojinja.exceptions.RequireNewlineException, msg)

    def test_4(self):
        input = "<<[ a ]>>\n" \
                "  [[[ ]]]\n" \
                "    <<[ b ]>>\n" \
                "    <<[ end ]>> <<[ a ]>>\n" \
                "  [[[ end ]]]\n" \
                "<<[ end ]>>"
        msg   = "Marker can't start on same line as previous end marker:\n" \
                "    <<[ end ]>> <<[ a ]>>\\n\n" \
                "                ^^^ line 4, column 17"
        invalid_marker(input, None, autojinja.exceptions.RequireNewlineException, msg)

class Test_RequireInlineException:
    def test_1(self):
        input = "[[[ a ]]] [[[ b ]]]\n" \
                "[[[ end ]]]"
        msg   = "Marker must start on same line as previous marker:\n" \
                "[[[ end ]]]\\0\n" \
                "^^^ line 2, column 1"
        invalid_marker(input, None, autojinja.exceptions.RequireInlineException, msg)

    def test_2(self):
        input = "[[[ a ]]] [[[ end ]]] [[[ abc ]]]\n" \
                "[[[ end ]]]"
        msg   = "Marker must start on same line as previous marker:\n" \
                "[[[ end ]]]\\0\n" \
                "^^^ line 2, column 1"
        invalid_marker(input, None, autojinja.exceptions.RequireInlineException, msg)

    def test_3(self):
        input = "<<[ a ]>> <<[ end ]>> <<[ abc ]>>\n" \
                "<<[ end ]>>"
        msg   = "Marker must start on same line as previous marker:\n" \
                "<<[ end ]>>\\0\n" \
                "^^^ line 2, column 1"
        invalid_marker(input, None, autojinja.exceptions.RequireInlineException, msg)

    def test_4(self):
        input = "// [[[ <<[ abc ]>><<[ end ]>> ]]] <<[ abc ]>> <<[ end ]>>\n" \
                "// [[[ end ]]]"
        msg   = "Marker must start on same line as previous marker:\n" \
                "// [[[ end ]]]\\0\n" \
                "   ^^^ line 2, column 4"
        invalid_marker(input, None, autojinja.exceptions.RequireInlineException, msg)

    def test_5(self):
        input = "// [[[ <<[ abc ]>><<[ end ]>> ]]] <<[ abc ]>> \n" \
                "<<[ end ]>>\n" \
                "// [[[ end ]]]"
        msg   = "Marker must start on same line as previous marker:\n" \
                "<<[ end ]>>\\n\n" \
                "^^^ line 2, column 1"
        invalid_marker(input, None, autojinja.exceptions.RequireInlineException, msg)

class Test_WrongInclusionException:
    def test_1(self):
        input = "[[[]]]\n" \
                "    <<[ a ]>>\n" \
                "[[[end]]]\n"
        msg   = "Marker has wrong inclusion regarding enclosing markers:\n" \
                "[[[end]]]\\n\n" \
                "^^^ line 3, column 1"
        invalid_marker(input, None, autojinja.exceptions.WrongInclusionException, msg)

    def test_2(self):
        input = "[[[]]]\n" \
                "    <<[ a ]>>\n" \
                "        [[[ ]]]\n" \
                "    <<[ end ]>>\n" \
                "        [[[ end ]]]\n" \
                "[[[end]]]\n"
        msg   = "Marker has wrong inclusion regarding enclosing markers:\n" \
                "    <<[ end ]>>\\n\n" \
                "    ^^^ line 4, column 5"
        invalid_marker(input, None, autojinja.exceptions.WrongInclusionException, msg)

    def test_3(self):
        input = "<<[ c ]>>\n" \
                "   [[[ ]]]\n" \
                "<<[ end ]>>"
        msg   = "Marker has wrong inclusion regarding enclosing markers:\n" \
                "<<[ end ]>>\\0\n" \
                "^^^ line 3, column 1"
        invalid_marker(input, None, autojinja.exceptions.WrongInclusionException, msg)

    def test_4(self):
        input = "<<[ c ]>>\n" \
                "   [[[ ]]]\n" \
                "       [[[ ]]]\n" \
                "       [[[ end ]]]\n" \
                "       <<[ a ]>>\n" \
                "   [[[ end ]]]\n" \
                "<<[ end ]>>"
        msg   = "Marker has wrong inclusion regarding enclosing markers:\n" \
                "   [[[ end ]]]\\n\n" \
                "   ^^^ line 6, column 4"
        invalid_marker(input, None, autojinja.exceptions.WrongInclusionException, msg)

class Test_DuplicateEditException:
    def test_1(self):
        input = "<<[ abc ]>>\n" \
                "<<[ end ]>>\n" \
                "<<[ abc ]>>\n" \
                "<<[ end ]>>"
        msg   = "Duplicate edit marker \"<<[ abc ]>>\", consider reusing/removing duplicates:\n" \
                "<<[ abc ]>>\\n\n" \
                "^^^ line 3, column 1"
        invalid_marker(input, None, autojinja.exceptions.DuplicateEditException, msg)

    def test_2(self):
        input = "<<[ abc ]>><<[ end ]>>\n" \
                "// [[[ <<[ abc ]>><<[ end ]>> ]]]\n" \
                "<<[ abc ]>><<[ end ]>>\n" \
                "// [[[ end ]]]"
        msg   = "Duplicate edit marker \"<<[ abc ]>>\", consider reusing/removing duplicates:\n" \
                "<<[ abc ]>><<[ end ]>>\\n\n" \
                "^^^ line 3, column 1"
        invalid_marker(input, None, autojinja.exceptions.DuplicateEditException, msg)

    def test_3(self):
        input = "<<[ abc ]>><<[ end ]>>\n" \
                "<<[ b ]>>\n" \
                "// [[[ <<[ abc ]>><<[ end ]>> ]]]\n" \
                "  <<[ abc ]>><<[ end ]>>\n" \
                "// [[[ end ]]]\n" \
                "<<[ end ]>>"
        msg   = "Duplicate edit marker \"<<[ abc ]>>\", consider reusing/removing duplicates:\n" \
                "  <<[ abc ]>><<[ end ]>>\\n\n" \
                "  ^^^ line 4, column 3"
        invalid_marker(input, None, autojinja.exceptions.DuplicateEditException, msg)

    def test_4(self):
        input = "<<[ b ]>>\n" \
                "// [[[ <<[ abc ]>><<[ end ]>> ]]]\n" \
                "  <<[ abc ]>><<[ end ]>>\n" \
                "// [[[ end ]]]\n" \
                "<<[ end ]>>\n" \
                "<<[ abc ]>><<[ end ]>>"
        msg   = "Duplicate edit marker \"<<[ abc ]>>\", consider reusing/removing duplicates:\n" \
                "<<[ abc ]>><<[ end ]>>\\0\n" \
                "^^^ line 6, column 1"
        invalid_marker(input, None, autojinja.exceptions.DuplicateEditException, msg)

    def test_5(self):
        input = "// [[[ <<[ abc ]>><<[ end ]>> ]]]\n" \
                "  <<[ abc ]>><<[ end ]>>\n" \
                "// [[[ end ]]]\n" \
                "// [[[ <<[ abc ]>><<[ end ]>> ]]]\n" \
                "  <<[ abc ]>><<[ end ]>>\n" \
                "// [[[ end ]]]"
        msg   = "Duplicate edit marker \"<<[ abc ]>>\", consider reusing/removing duplicates:\n" \
                "  <<[ abc ]>><<[ end ]>>\\n\n" \
                "  ^^^ line 5, column 3"
        invalid_marker(input, None, autojinja.exceptions.DuplicateEditException, msg)

class Test_DirectlyEnclosedEditException:
    def test_1(self):
        input = "<<[]>> abc <<[  end  ]>>"
        msg   = "Directly enclosed edit marker \"<<[  end  ]>>\", consider reusing/removing it:\n" \
                "<<[]>> abc <<[  end  ]>>\\0\n" \
                "           ^^^ line 1, column 12"
        invalid_marker(input, None, autojinja.exceptions.DirectlyEnclosedEditException, msg)

    def test_2(self):
        input = "<<[]>> abc <<[ any ]>>"
        msg   = "Directly enclosed edit marker \"<<[ any ]>>\", consider reusing/removing it:\n" \
                "<<[]>> abc <<[ any ]>>\\0\n" \
                "           ^^^ line 1, column 12"
        invalid_marker(input, None, autojinja.exceptions.DirectlyEnclosedEditException, msg)

    def test_3(self):
        input = "<<[]>> abc <<[dne]>> <<[end]>>"
        msg   = "Directly enclosed edit marker \"<<[ dne ]>>\", consider reusing/removing it:\n" \
                "<<[]>> abc <<[dne]>> <<[end]>>\\0\n" \
                "           ^^^ line 1, column 12"
        invalid_marker(input, None, autojinja.exceptions.DirectlyEnclosedEditException, msg)

    def test_4(self):
        input = "<<[]>> abc <<[dne]>> <<[zde]>> <<[end]>>"
        msg   = "Directly enclosed edit marker \"<<[ dne ]>>\", consider reusing/removing it:\n" \
                "<<[]>> abc <<[dne]>> <<[zde]>> <<[end]>>\\0\n" \
                "           ^^^ line 1, column 12"
        invalid_marker(input, None, autojinja.exceptions.DirectlyEnclosedEditException, msg)

    def test_5(self):
        input = "<<[]>> abc <<[  end  ]>>"
        msg   = "Directly enclosed edit marker \"<<[  end  ]>>\", consider reusing/removing it:\n" \
                "<<[]>> abc <<[  end  ]>>\\0\n" \
                "           ^^^ line 1, column 12"
        invalid_marker(input, None, autojinja.exceptions.DirectlyEnclosedEditException, msg)

    def test_6(self):
        input = "<<[]>> abc <<[ any ]>>"
        msg   = "Directly enclosed edit marker \"<<[ any ]>>\", consider reusing/removing it:\n" \
                "<<[]>> abc <<[ any ]>>\\0\n" \
                "           ^^^ line 1, column 12"
        invalid_marker(input, None, autojinja.exceptions.DirectlyEnclosedEditException, msg)

    def test_7(self):
        input = "<<[]>> abc <<[dne]>>"
        msg   = "Directly enclosed edit marker \"<<[ dne ]>>\", consider reusing/removing it:\n" \
                "<<[]>> abc <<[dne]>>\\0\n" \
                "           ^^^ line 1, column 12"
        invalid_marker(input, None, autojinja.exceptions.DirectlyEnclosedEditException, msg)

    def test_8(self):
        input = "<<[ a ]>> <<[ b ]>>\n" \
                "<<[ end ]>>"
        msg   = "Directly enclosed edit marker \"<<[ b ]>>\", consider reusing/removing it:\n" \
                "<<[ a ]>> <<[ b ]>>\\n\n" \
                "          ^^^ line 1, column 11"
        invalid_marker(input, None, autojinja.exceptions.DirectlyEnclosedEditException, msg)

    def test_9(self):
        input = "// [[[ ]]]\n" \
                "// <<[ a ]>>\n" \
                "   // <<[ b ]>><<[ end ]>>\n" \
                "// <<[ end ]>>\n" \
                "// [[[ end ]]]"
        msg   = "Directly enclosed edit marker \"<<[ b ]>>\", consider reusing/removing it:\n" \
                "   // <<[ b ]>><<[ end ]>>\\n\n" \
                "      ^^^ line 3, column 7"
        invalid_marker(input, None, autojinja.exceptions.DirectlyEnclosedEditException, msg)

    def test_10(self):
        input = "// [[[ ]]]\n" \
                "// <<[ a ]>>\n" \
                "//   <<[ b ]>> abc <<[ end ]>>\n" \
                "// <<[ end ]>>\n" \
                "// [[[ end ]]]"
        msg   = "Directly enclosed edit marker \"<<[ b ]>>\", consider reusing/removing it:\n" \
                "//   <<[ b ]>> abc <<[ end ]>>\\n\n" \
                "     ^^^ line 3, column 6"
        invalid_marker(input, None, autojinja.exceptions.DirectlyEnclosedEditException, msg)

    def test_11(self):
        input = "// <<[ a ]>>\n" \
                "//   <<[ b ]>><<[ end ]>>\n" \
                "// <<[ end ]>>\n"
        msg   = "Directly enclosed edit marker \"<<[ b ]>>\", consider reusing/removing it:\n" \
                "//   <<[ b ]>><<[ end ]>>\\n\n" \
                "     ^^^ line 2, column 6"
        invalid_marker(input, None, autojinja.exceptions.DirectlyEnclosedEditException, msg)

    def test_12(self):
        input = "// [[[  ]]]\n" \
                "// [[[  ]]]\n" \
                "// [[[  ]]]\n" \
                "// [[[ end ]]]\n" \
                "// [[[ end ]]]\n" \
                "  <<[ abc ]>> <<[d]>> <<[ end ]>>\n" \
                "// [[[ end ]]]"
        msg   = "Directly enclosed edit marker \"<<[ d ]>>\", consider reusing/removing it:\n" \
                "  <<[ abc ]>> <<[d]>> <<[ end ]>>\\n\n" \
                "              ^^^ line 6, column 15"
        invalid_marker(input, None, autojinja.exceptions.DirectlyEnclosedEditException, msg)

class Test_RequireBodyInlineException:
    def test_1(self):
        input = "<<[ abc ]>><<[ end ]>>\n" \
                "// [[[ <<[ def ]>><<[ end ]>> ]]]\n" \
                "   <<[ def ]>>\n" \
                "   // [[[ <<[ ghi ]>><<[ end ]>> ]]]\n" \
                "   // [[[ end ]]]\n" \
                "   <<[ end ]>>\n" \
                "// [[[ end ]]]"
        msg = "\n  During generation of \"[[[ <<[ def ]>><<[ end ]>> ]]]\" at line 2, column 4\n" \
                "Generated body must contain only one line to be inlined:\n" \
                "<<[ def ]>><<[ end ]>>\\0\n" \
                "^^^ line 1, column 1"
        invalid_marker(input, None, autojinja.exceptions.RequireBodyInlineException, msg)

    def test_2(self):
        input = "// [[[ <<[ def ]>><<[ end ]>> ]]]\n" \
                "// [[[ end ]]]\n" \
                "// [[[ ]]]\n" \
                "   <<[ def ]>>\n" \
                "   // [[[ <<[ ghi ]>><<[ end ]>> ]]]\n" \
                "   // [[[ end ]]]\n" \
                "   <<[ end ]>>\n" \
                "// [[[ end ]]]"
        msg = "\n  During generation of \"[[[ <<[ def ]>><<[ end ]>> ]]]\" at line 1, column 4\n" \
                "Generated body must contain only one line to be inlined:\n" \
                "<<[ def ]>><<[ end ]>>\\0\n" \
                "^^^ line 1, column 1"
        invalid_marker(input, None, autojinja.exceptions.RequireBodyInlineException, msg)

class Test_NonGeneratedEditException:
    def test_1(self):
        input = "[[[\n" \
                "  <<[ edit2 ]>>\n" \
                "  <<[ end ]>>\n" \
                "]]]\n" \
                "  <<[ edit1 ]>>\n" \
                "  a\n" \
                "  <<[ end ]>>\n" \
                "[[[ end ]]]\n"
        msg   = "Non-generated edit marker \"<<[ edit1 ]>>\", consider reusing/removing it:\n" \
                "  <<[ edit1 ]>>\\n\n" \
                "  ^^^ line 5, column 3"
        invalid_marker(input, None, autojinja.exceptions.NonGeneratedEditException, msg)

    def test_1_allow_code_loss(self):
        input = "[[[\n" \
                "  <<[ edit2 ]>>\n" \
                "  <<[ end ]>>\n" \
                "]]]\n" \
                "  <<[ edit1 ]>>\n" \
                "  a\n" \
                "  <<[ end ]>>\n" \
                "[[[ end ]]]\n"
        template = autojinja.CogTemplate.from_string(input)
        for edit_block in template.edit_blocks.values():
            edit_block.allow_code_loss = True
        template.context().render()

    def test_2(self):
        input = "[[[\n" \
                "  <<[ edit1 ]>>\n" \
                "  <<[ end ]>>\n" \
                "]]]\n" \
                "  <<[ edit1 ]>>\n" \
                "    [[[ ]]]\n" \
                "      <<[ edit2 ]>>\n" \
                "      <<[ end ]>>\n" \
                "    [[[ end ]]]\n" \
                "  <<[ end ]>>\n" \
                "[[[ end ]]]\n"
        msg   = "Non-generated edit marker \"<<[ edit2 ]>>\", consider reusing/removing it:\n" \
                "      <<[ edit2 ]>>\\n\n" \
                "      ^^^ line 7, column 7"
        invalid_marker(input, None, autojinja.exceptions.NonGeneratedEditException, msg)

    def test_2_allow_code_loss(self):
        input = "[[[\n" \
                "  <<[ edit1 ]>>\n" \
                "  <<[ end ]>>\n" \
                "]]]\n" \
                "  <<[ edit1 ]>>\n" \
                "    [[[ ]]]\n" \
                "      <<[ edit2 ]>>\n" \
                "      <<[ end ]>>\n" \
                "    [[[ end ]]]\n" \
                "  <<[ end ]>>\n" \
                "[[[ end ]]]\n"
        template = autojinja.CogTemplate.from_string(input)
        for edit_block in template.edit_blocks.values():
            edit_block.allow_code_loss = True
        template.context().render()

    def test_3(self):
        input = "[[[\n" \
                "  <<[ edit2 ]>>\n" \
                "  <<[ end ]>>\n" \
                "]]]\n" \
                "  <<[ edit1 ]>>\n" \
                "    [[[ ]]]\n" \
                "      <<[ edit2 ]>>\n" \
                "      abc\n" \
                "      <<[ end ]>>\n" \
                "    [[[ end ]]]\n" \
                "  <<[ end ]>>\n" \
                "[[[ end ]]]\n"
        msg   = "Non-generated edit marker \"<<[ edit1 ]>>\", consider reusing/removing it:\n" \
                "  <<[ edit1 ]>>\\n\n" \
                "  ^^^ line 5, column 3"
        invalid_marker(input, None, autojinja.exceptions.NonGeneratedEditException, msg)

    def test_3_allow_code_loss(self):
        input = "[[[\n" \
                "  <<[ edit2 ]>>\n" \
                "  <<[ end ]>>\n" \
                "]]]\n" \
                "  <<[ edit1 ]>>\n" \
                "    [[[ ]]]\n" \
                "      <<[ edit2 ]>>\n" \
                "      abc\n" \
                "      <<[ end ]>>\n" \
                "    [[[ end ]]]\n" \
                "  <<[ end ]>>\n" \
                "[[[ end ]]]\n"
        template = autojinja.CogTemplate.from_string(input)
        for edit_block in template.edit_blocks.values():
            edit_block.allow_code_loss = True
        template.context().render()

    def test_4(self):
        input = "// [[[ ]]]\n" \
                "<<[ abc ]>><<[ end ]>>\n" \
                "// [[[ end ]]]"
        msg   = "Non-generated edit marker \"<<[ abc ]>>\", consider reusing/removing it:\n" \
                "<<[ abc ]>><<[ end ]>>\\n\n" \
                "^^^ line 2, column 1"
        invalid_marker(input, None, autojinja.exceptions.NonGeneratedEditException, msg)

    def test_4_allow_code_loss(self):
        input = "// [[[ ]]]\n" \
                "<<[ abc ]>><<[ end ]>>\n" \
                "// [[[ end ]]]"
        template = autojinja.CogTemplate.from_string(input)
        for edit_block in template.edit_blocks.values():
            edit_block.allow_code_loss = True
        template.context().render()

    def test_5(self):
        input = "[[[\n" \
                "  <<[ a ]>>\n" \
                "  <<[ end ]>>\n" \
                "]]]\n" \
                "  <<[ a ]>>\n" \
                "    [[[  ]]]\n" \
                "      <<[ b ]>>\n" \
                "      <<[ end ]>>\n" \
                "    [[[ end ]]]\n" \
                "  <<[ end ]>>\n" \
                "[[[ end ]]]"
        msg   = "Non-generated edit marker \"<<[ b ]>>\", consider reusing/removing it:\n" \
                "      <<[ b ]>>\\n\n" \
                "      ^^^ line 7, column 7"
        invalid_marker(input, None, autojinja.exceptions.NonGeneratedEditException, msg)

    def test_5_allow_code_loss(self):
        input = "[[[\n" \
                "  <<[ a ]>>\n" \
                "  <<[ end ]>>\n" \
                "]]]\n" \
                "  <<[ a ]>>\n" \
                "    [[[  ]]]\n" \
                "      <<[ b ]>>\n" \
                "      <<[ end ]>>\n" \
                "    [[[ end ]]]\n" \
                "  <<[ end ]>>\n" \
                "[[[ end ]]]"
        template = autojinja.CogTemplate.from_string(input)
        for edit_block in template.edit_blocks.values():
            edit_block.allow_code_loss = True
        template.context().render()

    def test_6(self):
        input  = "[[[\n" \
                 "  <<[ b ]>>\n" \
                 "  <<[ end ]>>\n" \
                 "]]]\n" \
                 "[[[ end ]]]"
        output = "[[[  ]]]\n" \
                 "  <<[ a ]>>\n" \
                 "    [[[  ]]]\n" \
                 "      <<[ b ]>>\n" \
                 "      <<[ end ]>>\n" \
                 "    [[[ end ]]]\n" \
                 "  <<[ end ]>>\n" \
                 "[[[ end ]]]"
        msg    = "Non-generated edit marker \"<<[ a ]>>\", consider reusing/removing it:\n" \
                 "  <<[ a ]>>\\n\n" \
                 "  ^^^ line 2, column 3"
        invalid_marker(input, output, autojinja.exceptions.NonGeneratedEditException, msg)

    def test_6_disallow_code_loss(self):
        input  = "[[[\n" \
                 "  <<[ b ]>>\n" \
                 "  <<[ end ]>>\n" \
                 "]]]\n" \
                 "[[[ end ]]]"
        output = "[[[  ]]]\n" \
                 "  <<[ a ]>>\n" \
                 "    [[[  ]]]\n" \
                 "      <<[ b ]>>\n" \
                 "      <<[ end ]>>\n" \
                 "    [[[ end ]]]\n" \
                 "  <<[ end ]>>\n" \
                 "[[[ end ]]]"
        template = autojinja.CogTemplate.from_string(input)
        for edit_block in template.edit_blocks.values():
            edit_block.allow_code_loss = True
        try:
            template.context().render(output)
            assert False # Shouldn't be reached
        except:
            pass

    def test_7(self):
        input  = "[[[  ]]]\n" \
                 "[[[ end ]]]"
        output = "[[[  ]]]\n" \
                 "  <<[ a ]>> <<[ end ]>>\n" \
                 "[[[ end ]]]"
        msg    = "Non-generated edit marker \"<<[ a ]>>\", consider reusing/removing it:\n" \
                 "  <<[ a ]>> <<[ end ]>>\\n\n" \
                 "  ^^^ line 2, column 3"
        invalid_marker(input, output, autojinja.exceptions.NonGeneratedEditException, msg)

    def test_7_disallow_code_loss(self):
        input  = "[[[  ]]]\n" \
                 "[[[ end ]]]"
        output = "[[[  ]]]\n" \
                 "  <<[ a ]>> <<[ end ]>>\n" \
                 "[[[ end ]]]"
        template = autojinja.CogTemplate.from_string(input)
        for edit_block in template.edit_blocks.values():
            edit_block.allow_code_loss = True
        try:
            template.context().render(output)
            assert False # Shouldn't be reached
        except:
            pass

    def test_8(self):
        input  = "[[[  ]]]\n" \
                 "[[[ end ]]]"
        output = "[[[  ]]]\n" \
                 "[[[ end ]]]\n" \
                 "  <<[ a ]>> <<[ end ]>>"
        msg    = "Non-generated edit marker \"<<[ a ]>>\", consider reusing/removing it:\n" \
                 "  <<[ a ]>> <<[ end ]>>\\0\n" \
                 "  ^^^ line 3, column 3"
        invalid_marker(input, output, autojinja.exceptions.NonGeneratedEditException, msg)

    def test_8_disallow_code_loss(self):
        input  = "[[[  ]]]\n" \
                 "[[[ end ]]]"
        output = "[[[  ]]]\n" \
                 "[[[ end ]]]\n" \
                 "  <<[ a ]>> <<[ end ]>>"
        template = autojinja.CogTemplate.from_string(input)
        for edit_block in template.edit_blocks.values():
            edit_block.allow_code_loss = True
        try:
            template.context().render(output)
            assert False # Shouldn't be reached
        except:
            pass

class Test_AlreadyGeneratedEditException:
    def test_1(self):
        input = "<<[ abc ]>><<[ end ]>>\n" \
                "// [[[ <<[ abc ]>><<[ end ]>> ]]]\n" \
                "// [[[ end ]]]"
        msg = "\n  During generation of \"[[[ <<[ abc ]>><<[ end ]>> ]]]\" at line 2, column 4\n" \
                "Already generated edit marker \"<<[ abc ]>>\", consider fixing generation:\n" \
                "<<[ abc ]>><<[ end ]>>\\0\n" \
                "^^^ line 1, column 1"
        invalid_marker(input, None, autojinja.exceptions.AlreadyGeneratedEditException, msg)

    def test_2(self):
        input = "<<[ abc ]>><<[ end ]>>\n" \
                "<<[ b ]>>\n" \
                "// [[[ <<[ abc ]>><<[ end ]>> ]]]\n" \
                "// [[[ end ]]]\n" \
                "<<[ end ]>>"
        msg = "\n  During reinsertion of \"<<[ b ]>>\" at line 2, column 1\n" \
                "  During generation of \"[[[ <<[ abc ]>><<[ end ]>> ]]]\" at line 1, column 4\n" \
                "Already generated edit marker \"<<[ abc ]>>\", consider fixing generation:\n" \
                "<<[ abc ]>><<[ end ]>>\\0\n" \
                "^^^ line 1, column 1"
        invalid_marker(input, None, autojinja.exceptions.AlreadyGeneratedEditException, msg)

    def test_3(self):
        input  = "[[[\n" \
                 "  <<[ a ]>>\n" \
                 "  <<[ end ]>>\n" \
                 "  <<[ b ]>>\n" \
                 "  <<[ end ]>>\n" \
                 "]]]\n" \
                 "  <<[ a ]>>\n" \
                 "  <<[ end ]>>\n" \
                 "[[[ end ]]]"
        output = "[[[ ]]]\n" \
                 "  <<[ a ]>>\n" \
                 "    [[[ <<[ a ]>><<[ end ]>> ]]]\n" \
                 "    <<[ b ]>><<[ end ]>>\n" \
                 "    [[[ end ]]]\n" \
                 "  <<[ end ]>>\n" \
                 "[[[ end ]]]"
        msg  = "\n  During generation of \"[[[   <<[ a ]>>\\n  <<[ end ]>>\\n  <<[ b ]>>\\n  <<[ end ]>... ]]]\" at line 1, column 1\n" \
                 "  During reinsertion of \"<<[ a ]>>\" at line 1, column 3\n" \
                 "  During generation of \"[[[ <<[ a ]>><<[ end ]>> ]]]\" at line 1, column 3\n" \
                 "Already generated edit marker \"<<[ a ]>>\", consider fixing generation:\n" \
                 "<<[ a ]>><<[ end ]>>\\0\n" \
                 "^^^ line 1, column 1"
        invalid_marker(input, output, autojinja.exceptions.AlreadyGeneratedEditException, msg)

    def test_4(self):
        input  = "[[[\n" \
                 "  <<[ a ]>>\n" \
                 "  <<[ end ]>>\n" \
                 "]]]\n" \
                 "  <<[ a ]>>\n" \
                 "  <<[ end ]>>\n" \
                 "[[[ end ]]]"
        output = "<<[ a ]>>\n" \
                 "  [[[ <<[ a ]>><<[ end ]>> ]]]\n" \
                 "  [[[ end ]]]\n" \
                 "<<[ end ]>>"
        msg  = "\n  During generation of \"[[[   <<[ a ]>>\\n  <<[ end ]>> ]]]\" at line 1, column 1\n" \
                 "  During reinsertion of \"<<[ a ]>>\" at line 1, column 3\n" \
                 "  During generation of \"[[[ <<[ a ]>><<[ end ]>> ]]]\" at line 1, column 3\n" \
                 "Already generated edit marker \"<<[ a ]>>\", consider fixing generation:\n" \
                 "<<[ a ]>><<[ end ]>>\\0\n" \
                 "^^^ line 1, column 1"
        invalid_marker(input, output, autojinja.exceptions.AlreadyGeneratedEditException, msg)

class Test_Jinja2Exceptions:
    class Test_TemplateSyntaxError:
        def test_1(self):
            input = "[[[ {{ ]]]\n" \
                    "[[[ end ]]]"
            msg = "\n  File \"<unknown>\", line 1, in template\n" \
                    "unexpected 'end of template'"
            invalid_marker(input, None, jinja2.exceptions.TemplateSyntaxError, msg)

        def test_2(self):
            input = "[[[\n" \
                    "  <<[ a ]>>\n" \
                    "  <<[ end ]>>\n" \
                    "]]]\n" \
                    "  <<[ a ]>>\n" \
                    "    [[[ {{ ]]]\n" \
                    "    [[[ end ]]]\n" \
                    "  <<[ end ]>>\n" \
                    "[[[ end ]]]"
            msg = "\n  During generation of \"[[[   <<[ a ]>>\\n  <<[ end ]>> ]]]\" at line 1, column 1\n" \
                    "  During reinsertion of \"<<[ a ]>>\" at line 1, column 3\n" \
                    "  File \"<unknown>\", line 1, in template\n" \
                    "unexpected 'end of template'"
            invalid_marker(input, None, jinja2.exceptions.TemplateSyntaxError, msg)

    class Test_UndefinedError:
        def test_1(self):
            input = "[[[ {{ var }} ]]]\n" \
                    "[[[ end ]]]"
            msg = "\n  File \"{{ var }}\", line 1, in top-level template code\n" \
                    "'var' is undefined"
            invalid_marker(input, None, jinja2.exceptions.UndefinedError, msg)

        def test_2(self):
            input = "[[[\n" \
                    "  <<[ a ]>>\n" \
                    "  <<[ end ]>>\n" \
                    "]]]\n" \
                    "  <<[ a ]>>\n" \
                    "    [[[ {{ var }} ]]]\n" \
                    "    [[[ end ]]]\n" \
                    "  <<[ end ]>>\n" \
                    "[[[ end ]]]"
            msg = "\n  During generation of \"[[[   <<[ a ]>>\\n  <<[ end ]>> ]]]\" at line 1, column 1\n" \
                    "  During reinsertion of \"<<[ a ]>>\" at line 1, column 3\n" \
                    "  File \"{{ var }}\", line 1, in top-level template code\n" \
                    "'var' is undefined"
            invalid_marker(input, None, jinja2.exceptions.UndefinedError, msg)

    class Test_TemplateAssertionError:
        def test_1(self):
            input = "[[[ {{ []|var_filter }} ]]]\n" \
                    "[[[ end ]]]"
            msg = "\n  File \"<unknown>\", line 1, in template\n" \
                    "No filter named 'var_filter'."
            invalid_marker(input, None, jinja2.exceptions.TemplateAssertionError, msg)

        def test_2(self):
            input = "[[[\n" \
                    "  <<[ a ]>>\n" \
                    "  <<[ end ]>>\n" \
                    "]]]\n" \
                    "  <<[ a ]>>\n" \
                    "    [[[ {{ []|var_filter }} ]]]\n" \
                    "    [[[ end ]]]\n" \
                    "  <<[ end ]>>\n" \
                    "[[[ end ]]]"
            msg = "\n  During generation of \"[[[   <<[ a ]>>\\n  <<[ end ]>> ]]]\" at line 1, column 1\n" \
                    "  During reinsertion of \"<<[ a ]>>\" at line 1, column 3\n" \
                    "  File \"<unknown>\", line 1, in template\n" \
                    "No filter named 'var_filter'."
            invalid_marker(input, None, jinja2.exceptions.TemplateAssertionError, msg)

    class Test_FunctionError:
        def test_1(self):
            def function():
                raise TypeError()
            input = "[[[ {{ function() }} ]]]\n" \
                    "[[[ end ]]]"
            invalid_marker(input, None, TypeError, None, function = function)

        def test_2(self):
            def function():
                raise TypeError()
            input = "[[[\n" \
                    "  <<[ a ]>>\n" \
                    "  <<[ end ]>>\n" \
                    "]]]\n" \
                    "  <<[ a ]>>\n" \
                    "    [[[ {{ function() }} ]]]\n" \
                    "    [[[ end ]]]\n" \
                    "  <<[ end ]>>\n" \
                    "[[[ end ]]]"
            invalid_marker(input, None, TypeError, None, function = function)

    class Test_TemplateNotFound:
        def test_1(self):
            env = autojinja.RawTemplate.create_environment(loader=jinja2.FileSystemLoader("dir"))
            autojinja.RawTemplate.environment = env
            try:
                input = "[[[ {% extends 'file.txt' %} ]]]\n" \
                        "[[[ end ]]]"
                invalid_marker(input, None, jinja2.exceptions.TemplateNotFound, None)
            finally:
                autojinja.RawTemplate.environment = None

        def test_2(self):
            env = autojinja.RawTemplate.create_environment(loader=jinja2.FileSystemLoader("dir"))
            autojinja.RawTemplate.environment = env
            try:
                input = "[[[\n" \
                        "  <<[ a ]>>\n" \
                        "  <<[ end ]>>\n" \
                        "]]]\n" \
                        "  <<[ a ]>>\n" \
                        "    [[[ {% extends 'file.txt' %} ]]]\n" \
                        "    [[[ end ]]]\n" \
                        "  <<[ end ]>>\n" \
                        "[[[ end ]]]"
                invalid_marker(input, None, jinja2.exceptions.TemplateNotFound, None)
            finally:
                autojinja.RawTemplate.environment = None

    class Test_FilterError:
        def test_1(self):
            env = autojinja.RawTemplate.create_environment()
            env.filters["var_filter"] = lambda:None
            autojinja.RawTemplate.environment = env
            try:
                input = "[[[ {{ ['arg1']|var_filter }} ]]]\n" \
                        "[[[ end ]]]"
                if sys.version_info[1] >= 10:
                    msg = "\n  File \"{{ ['arg1']|var_filter }}\", line 1, in top-level template code\n" \
                          "Test_Jinja2Exceptions.Test_FilterError.test_1.<locals>.<lambda>() takes 0 positional arguments but 1 was given"
                else:
                    msg = "\n  File \"{{ ['arg1']|var_filter }}\", line 1, in top-level template code\n" \
                          "<lambda>() takes 0 positional arguments but 1 was given"
                invalid_marker(input, None, TypeError, msg)
            finally:
                autojinja.RawTemplate.environment = None

        def test_2(self):
            env = autojinja.RawTemplate.create_environment()
            env.filters["var_filter"] = lambda:None
            autojinja.RawTemplate.environment = env
            try:
                input = "[[[\n" \
                        "  <<[ a ]>>\n" \
                        "  <<[ end ]>>\n" \
                        "]]]\n" \
                        "  <<[ a ]>>\n" \
                        "    [[[ {{ ['arg1']|var_filter }} ]]]\n" \
                        "    [[[ end ]]]\n" \
                        "  <<[ end ]>>\n" \
                        "[[[ end ]]]"
                if sys.version_info[1] >= 10:
                    msg = "\n  During generation of \"[[[   <<[ a ]>>\\n  <<[ end ]>> ]]]\" at line 1, column 1\n" \
                            "  During reinsertion of \"<<[ a ]>>\" at line 1, column 3\n" \
                            "  File \"{{ ['arg1']|var_filter }}\", line 1, in top-level template code\n" \
                            "Test_Jinja2Exceptions.Test_FilterError.test_2.<locals>.<lambda>() takes 0 positional arguments but 1 was given"
                else:
                    msg = "\n  During generation of \"[[[   <<[ a ]>>\\n  <<[ end ]>> ]]]\" at line 1, column 1\n" \
                            "  During reinsertion of \"<<[ a ]>>\" at line 1, column 3\n" \
                            "  File \"{{ ['arg1']|var_filter }}\", line 1, in top-level template code\n" \
                            "<lambda>() takes 0 positional arguments but 1 was given"
                invalid_marker(input, None, TypeError, msg)
            finally:
                autojinja.RawTemplate.environment = None

class Test:
    def test_index_to_coordinates(self):
        input = "abcdef\n" \
                "ghijklmnopqrst\n" \
                "uvwwyz"
        for i in range(0, 7):
            assert autojinja.exceptions.index_to_coordinates(input, i) == (1, 1 + i)
        for i in range(7, 22):
            assert autojinja.exceptions.index_to_coordinates(input, i) == (2, 1 + i-7)
        for i in range(22, 28):
            assert autojinja.exceptions.index_to_coordinates(input, i) == (3, 1 + i-22)
        assert autojinja.exceptions.index_to_coordinates(input, 28) == (3, 6)
        assert autojinja.exceptions.index_to_coordinates(input, 29) == (3, 6)
        assert autojinja.exceptions.index_to_coordinates(input, 30) == (3, 6)
        assert autojinja.exceptions.index_to_coordinates(input, -1) == (3, 6)
        assert autojinja.exceptions.index_to_coordinates(input, -2) == (3, 5)
        assert autojinja.exceptions.index_to_coordinates(input, -3) == (3, 4)
        assert autojinja.exceptions.index_to_coordinates(input, -28) == (1, 1)
        assert autojinja.exceptions.index_to_coordinates(input, -29) == (3, 6)
        assert autojinja.exceptions.index_to_coordinates(input, -30) == (3, 5)

    def test_line_at_index(self):
        input = "abcdef\n" \
                "ghijklmnopqrst\n" \
                "uvwwyz"
        for i in range(0, 7):
            assert autojinja.exceptions.line_at_index(input, i) == "abcdef\\n"
        for i in range(7, 22):
            assert autojinja.exceptions.line_at_index(input, i) == "ghijklmnopqrst\\n"
        for i in range(22, 28):
            assert autojinja.exceptions.line_at_index(input, i) == "uvwwyz\\0"
        assert autojinja.exceptions.line_at_index(input, 28) == "uvwwyz\\0"
        assert autojinja.exceptions.line_at_index(input, 29) == "uvwwyz\\0"
        assert autojinja.exceptions.line_at_index(input, 30) == "uvwwyz\\0"
        assert autojinja.exceptions.line_at_index(input, -1) == "uvwwyz\\0"
        assert autojinja.exceptions.line_at_index(input, -2) == "uvwwyz\\0"
        assert autojinja.exceptions.line_at_index(input, -3) == "uvwwyz\\0"
        assert autojinja.exceptions.line_at_index(input, -28) == "abcdef\\n"
        assert autojinja.exceptions.line_at_index(input, -29) == "uvwwyz\\0"
        assert autojinja.exceptions.line_at_index(input, -30) == "uvwwyz\\0"

    def test_format_text(self):
        input = "abcdef\n" \
                "ghijklmnopqrst\n" \
                "uvwwyz"
        assert autojinja.exceptions.format_text(input) == "abcdef\\nghijklmnopqrst\\nuvwwyz"
        assert autojinja.exceptions.format_text(input, 10) == "abcdef\\nghi..."
        assert autojinja.exceptions.format_text(input, 10, "_") == "abcdef\\nghi_"
        assert autojinja.exceptions.format_text(input, 20) == "abcdef\\nghijklmnopqrs..."
        assert autojinja.exceptions.format_text(input, 20, "__") == "abcdef\\nghijklmnopqrs__"

    def test_split_traceback(self):
        input = "autojinja.exceptions.Exception: line"
        assert autojinja.exceptions.split_traceback(input) == (None, "autojinja.exceptions.Exception: line")
        assert autojinja.exceptions.split_traceback(input, True) == (None, "line")
        input = "autojinja.exceptions.Exception: line\n"
        assert autojinja.exceptions.split_traceback(input) == ("autojinja.exceptions.Exception: line", "")
        assert autojinja.exceptions.split_traceback(input, True) == ("autojinja.exceptions.Exception: line", None)
        input = "  File <>\n" \
                "    abcdef\n" \
                "  File <>\n" \
                "    ghijkl\n" \
                "autojinja.exceptions.Exception: line1\n" \
                "line2"
        assert autojinja.exceptions.split_traceback(input) == ("  File <>\n    abcdef\n  File <>\n    ghijkl", "autojinja.exceptions.Exception: line1\nline2")
        assert autojinja.exceptions.split_traceback(input, True) == ("  File <>\n    abcdef\n  File <>\n    ghijkl", "line1\nline2")
        input = "  File <>\n" \
                "    abcdef\n" \
                "autojinja.exceptions.Exception:  \n" \
                "line2"
        assert autojinja.exceptions.split_traceback(input) == ("  File <>\n    abcdef", "autojinja.exceptions.Exception:  \nline2")
        assert autojinja.exceptions.split_traceback(input, True) == ("  File <>\n    abcdef", " \nline2")
        input = "  File <>\n" \
                "    abcdef\n" \
                "autojinja.exceptions.Exception: \n" \
                "line2"
        assert autojinja.exceptions.split_traceback(input) == ("  File <>\n    abcdef", "autojinja.exceptions.Exception: \nline2")
        assert autojinja.exceptions.split_traceback(input, True) == ("  File <>\n    abcdef", "line2")

        input = "  File <>\n" \
                "    abcdef\n" \
                "autojinja.exceptions.Exception:\n" \
                "line2"
        assert autojinja.exceptions.split_traceback(input) == ("  File <>\n    abcdef", "autojinja.exceptions.Exception:\nline2")
        assert autojinja.exceptions.split_traceback(input, True) == ("  File <>\n    abcdef", None) # Searches for ' '
        input = "  File <>\n" \
                "    abcdef\n" \
                " \n" \
                "line2"
        assert autojinja.exceptions.split_traceback(input) == ("  File <>\n    abcdef", " \nline2")
        assert autojinja.exceptions.split_traceback(input, True) == ("  File <>\n    abcdef", "line2")
        input = "  File <>\n" \
                "    abcdef\n" \
                "\n" \
                "line2"
        assert autojinja.exceptions.split_traceback(input) == ("  File <>\n    abcdef", "\nline2")
        assert autojinja.exceptions.split_traceback(input, True) == ("  File <>\n    abcdef", None) # Searches for ' '

    def test_prepend_jinja2_traceback(self):
        exception = Exception("Message")
        tb = "autojinja.exceptions.Exception: line"
        assert str(autojinja.exceptions.prepend_jinja2_traceback(exception, tb)) == "\nline"
        tb = "line"
        assert str(autojinja.exceptions.prepend_jinja2_traceback(exception, tb)) == "\n"
        ### jinja2
        tb = f"  File <> in \"jinja2{os.sep}environment.py\", line 1\n" \
              "    abcdef\n" \
              "  File <>\n" \
              "    ghijkl\n" \
              "autojinja.exceptions.Exception: line"
        assert str(autojinja.exceptions.prepend_jinja2_traceback(exception, tb)) == "\n  File <>\n    ghijkl\nline"
        tb = f"  File <> in \"jinja2{os.sep}environment.py\", line 1\n" \
              "    abcdef\n" \
              "  File <>\n" \
              "autojinja.exceptions.Exception: line"
        assert str(autojinja.exceptions.prepend_jinja2_traceback(exception, tb)) == "\n  File <>\nline"
        tb = f"  File <> in \"jinja2{os.sep}environment.py\", line 1\n" \
              "  File <>\n" \
              "    ghijkl\n" \
              "autojinja.exceptions.Exception: line"
        assert str(autojinja.exceptions.prepend_jinja2_traceback(exception, tb)) == "\n  File <>\n    ghijkl\nline"
        tb =  "  File <>\n" \
              "    abcdef\n" \
             f"  File <> in \"jinja2{os.sep}environment.py\", line 1\n" \
              "    abcdef\n" \
              "  File <>\n" \
              "    ghijkl\n" \
              "autojinja.exceptions.Exception: line"
        assert str(autojinja.exceptions.prepend_jinja2_traceback(exception, tb)) == "\n  File <>\n    ghijkl\nline"
        tb = f"  File <> in \"jinja2{os.sep}environment.py\", line 1\n" \
              "    abcdef\n" \
              "autojinja.exceptions.Exception: line"
        assert str(autojinja.exceptions.prepend_jinja2_traceback(exception, tb)) == "\nline"
        tb = f"  File <> in \"jinja2{os.sep}environment.py\", line 1\n" \
              "    abcdef\n" \
              "  File <>\n" \
              "    abcdef\n" \
             f"  File <> in \"jinja2{os.sep}environment.py\", line 1\n" \
              "    ghijkl\n" \
              "autojinja.exceptions.Exception: line"
        assert str(autojinja.exceptions.prepend_jinja2_traceback(exception, tb)) == "\nline"
        tb =  "  File <>\n" \
              "    abcdef\n" \
             f"  File <> in \"jinja2{os.sep}environment.py\", line 1\n" \
              "    ghijkl\n" \
              "  File <>\n" \
              "    ghijkl\n" \
             f"  File <> in \"jinja2{os.sep}environment.py\", line 1\n" \
              "    abcdef\n" \
              "autojinja.exceptions.Exception: line"
        assert str(autojinja.exceptions.prepend_jinja2_traceback(exception, tb)) == "\nline"
        tb =  "  File <>\n" \
              "    abcdef\n" \
             f"  File <> in \"jinja2{os.sep}environment.py\", line 1\n" \
              "  File <>\n" \
              "    ghijkl\n" \
             f"  File <> in \"jinja2{os.sep}environment.py\", line 1\n" \
              "    abcdef\n" \
              "autojinja.exceptions.Exception: line"
        assert str(autojinja.exceptions.prepend_jinja2_traceback(exception, tb)) == "\nline"
        tb =  "  File <>\n" \
              "    abcdef\n" \
             f"  File <> in \"jinja2{os.sep}environment.py\", line 1\n" \
              "    ghijkl\n" \
              "  File <>\n" \
              "    ghijkl\n" \
             f"  File <> in \"jinja2{os.sep}environment.py\", line 1\n" \
              "autojinja.exceptions.Exception: line"
        assert str(autojinja.exceptions.prepend_jinja2_traceback(exception, tb)) == "\nline"
        tb =  "  File <>\n" \
              "    abcdef\n" \
             f"  File <> in \"jinja2{os.sep}environment.py\", line 1\n" \
              "    ghijkl\n" \
              "  File <>\n" \
              "    ghijkl\n" \
             f"  File <> in \"jinja2{os.sep}environment.py\", line 1\n" \
              "autojinja.exceptions.Exception: line"
        assert str(autojinja.exceptions.prepend_jinja2_traceback(exception, tb)) == "\nline"
        ### autojinja
        tb = f"  File <> in \"jinja2{os.sep}environment.py\", line 1\n" \
              "    abcdef\n" \
              "  File <>\n" \
              "    ghijkl\n" \
             f"  File <> in \"autojinja{os.sep}templates.py\", line 1\n" \
              "    abc\n" \
              "    ^^^\n" \
              "autojinja.exceptions.Exception: line"
        assert str(autojinja.exceptions.prepend_jinja2_traceback(exception, tb)) == "\n  File <>\n    ghijkl\nline"
        tb = f"  File <> in \"jinja2{os.sep}environment.py\", line 1\n" \
              "    abcdef\n" \
              "    ^^^^^^\n" \
              "  File <>\n" \
             f"  File <> in \"autojinja{os.sep}templates.py\", line 1\n" \
              "    abc\n" \
              "autojinja.exceptions.Exception: line"
        assert str(autojinja.exceptions.prepend_jinja2_traceback(exception, tb)) == "\n  File <>\nline"
        tb = f"  File <> in \"jinja2{os.sep}environment.py\", line 1\n" \
              "    abcdef\n" \
              "    ^^^^^^\n" \
              "  File <>\n" \
              "    ghijkl\n" \
              "    ^^^^^^\n" \
             f"  File <> in \"autojinja{os.sep}templates.py\", line 1\n" \
              "autojinja.exceptions.Exception: line"
        assert str(autojinja.exceptions.prepend_jinja2_traceback(exception, tb)) == "\n  File <>\n    ghijkl\n    ^^^^^^\nline"
        tb = f"  File <> in \"jinja2{os.sep}environment.py\", line 1\n" \
              "    abcdef\n" \
              "  File <>\n" \
             f"  File <> in \"autojinja{os.sep}templates.py\", line 1\n" \
              "    abcdef\n" \
              "    ^^^^^^\n" \
              "autojinja.exceptions.Exception: line"
        assert str(autojinja.exceptions.prepend_jinja2_traceback(exception, tb)) == "\n  File <>\nline"
        tb = f"  File <> in \"jinja2{os.sep}environment.py\", line 1\n" \
              "    abcdef\n" \
              "  File <>\n" \
              "    ghijkl\n" \
             f"  File <> in \"autojinja{os.sep}templates.py\", line 1\n" \
              "    abcdef\n" \
              "  File <>\n" \
              "    ghijkl\n" \
              "autojinja.exceptions.Exception: line"
        assert str(autojinja.exceptions.prepend_jinja2_traceback(exception, tb)) == "\n  File <>\n    ghijkl\nline"
