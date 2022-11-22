import autojinja

class CustomException(Exception):
    def __init__(self, result, expected):
        result = str(result).replace('\t', "\\t").replace('\n', "\\n\n")
        expected = str(expected).replace('\t', "\\t").replace('\n', "\\n\n")
        message = f"--- Expected ---\n{expected}\\0\n--- Got ---\n{result}\\0"
        super().__init__(message)

settingsCogComment = autojinja.ParserSettings(cog_open = "/**", cog_close = "**/", cog_as_comment = True)
settingsEditComment = autojinja.ParserSettings(edit_open = "/**", edit_close = "**/", edit_as_comment = True)

def valid_marker(input, expected,
                 header0 = None, body0 = None,
                 header1 = None, body1 = None,
                 header2 = None, body2 = None,
                 header3 = None, body3 = None,
                 remove_markers = False,
                 *args, **kwargs):
    template = autojinja.CogTemplate.from_string(input, *args, **kwargs)
    if header0 != None and template.markers[0].header != header0:
        raise CustomException(template.markers[0].header, header0)
    if body0 != None and template.markers[0].body != body0:
        raise CustomException(template.markers[0].body, body0)
    if header1 != None and template.markers[1].header != header1:
        raise CustomException(template.markers[1].header, header1)
    if body1 != None and template.markers[1].body != body1:
        raise CustomException(template.markers[1].body, body1)
    if header2 != None and template.markers[2].header != header2:
        raise CustomException(template.markers[2].header, header2)
    if body2 != None and template.markers[2].body != body2:
        raise CustomException(template.markers[2].body, body2)
    if header3 != None and template.markers[3].header != header3:
        raise CustomException(template.markers[3].header, header3)
    if body3 != None and template.markers[3].body != body3:
        raise CustomException(template.markers[3].body, body3)
    result = template.render(remove_markers = remove_markers)
    if expected != None and result != expected:
        raise CustomException(result, expected)

class Test_CogMarkers:
    class Test_OneLineMarker:
        def test_1(self):
            input    = "[[[]]][[[end]]]"
            expected = "[[[]]]  [[[end]]]"
            header   = ""
            body     = ""
            valid_marker(input, expected, header, body)

        def test_2(self):
            input    = "[[[]]] abc [[[end]]]"
            expected = "[[[]]]  [[[end]]]"
            header   = ""
            body     = "abc"
            valid_marker(input, expected, header, body)

        def test_3(self):
            input    = " [[[ ]]]  abc [[[end ]]]"
            expected = " [[[ ]]]  [[[end ]]]"
            header   = ""
            body     = " abc"
            valid_marker(input, expected, header, body)

        def test_4(self):
            input    = "  [[[  ]]] abc [[[ end]]]"
            expected = "  [[[  ]]]  [[[ end]]]"
            header   = ""
            body     = "abc"
            valid_marker(input, expected, header, body)

        def test_5(self):
            input    = "[[[a]]] abc [[[ end ]]] "
            expected = "[[[a]]] a [[[ end ]]] "
            header   = "a"
            body     = "abc"
            valid_marker(input, expected, header, body)

        def test_6(self):
            input    = "[[[ a]]] [[[end]]]  "
            expected = "[[[ a]]] a [[[end]]]  "
            header   = "a"
            body     = ""
            valid_marker(input, expected, header, body)

        def test_7(self):
            input    = "[[[a ]]]  [[[end]]]"
            expected = "[[[a ]]] a [[[end]]]"
            header   = "a"
            body     = ""
            valid_marker(input, expected, header, body)

        def test_8(self):
            input    = "[[[ a ]]]   [[[end]]]"
            expected = "[[[ a ]]] a [[[end]]]"
            header   = "a"
            body     = " "
            valid_marker(input, expected, header, body)

        def test_9(self):
            input    = "[[[   ]]][[[ end]]]"
            expected = "[[[   ]]]   [[[ end]]]"
            header   = " "
            body     = ""
            valid_marker(input, expected, header, body)

        def test_10(self):
            input    = "[[[  \t  ]]][[[end ]]]"
            expected = "[[[  \t  ]]]  \t  [[[end ]]]"
            header   = " \t "
            body     = ""
            valid_marker(input, expected, header, body)

        def test_11(self):
            input    = "  [[[     ]]]\n" \
                       "[[[ end ]]]"
            expected = "  [[[     ]]]\n" \
                       "     \n" \
                       "[[[ end ]]]"
            header   = "   "
            body     = ""
            valid_marker(input, expected, header, body)

        def test_12(self):
            input    = " [[[a    ]]] \n" \
                       " dummy\n" \
                       " [[[end]]]"
            expected = " [[[a    ]]] \n" \
                       " a   \n" \
                       " [[[end]]]"
            header   = "a   "
            body     = " dummy"
            valid_marker(input, expected, header, body)

        def test_13(self):
            input    = "[[[    a]]]  \n" \
                       "  [[[abc]]][[[end]]]\n" \
                       "  [[[end]]] "
            expected = "[[[    a]]]  \n" \
                       "   a\n" \
                       "  [[[end]]] "
            header   = "   a"
            body     = "  [[[abc]]][[[end]]]"
            valid_marker(input, expected, header, body)

        def test_14(self):
            input    = "[[[]]]  \n" \
                       "  [[[end]]] "
            expected = "[[[]]]  \n" \
                       "  [[[end]]] "
            header   = ""
            body     = ""
            valid_marker(input, expected, header, body)

        def test_15(self):
            input    = " /* [[[ a ]]]*/ dummy /*[[[end]]] */"
            expected = " /* [[[ a ]]]*/ a /*[[[end]]] */"
            header   = "a"
            body     = "dummy"
            valid_marker(input, expected, header, body)

        def test_16(self):
            input    = " /* [[[ a ]]]*/dummy /*[[[end]]] */"
            expected = " /* [[[ a ]]]*/dummy a /*[[[end]]] */"
            header   = "a"
            body     = ""
            valid_marker(input, expected, header, body)

        def test_17(self):
            input    = " /* [[[ a ]]]*/ dummy/*[[[end]]] */"
            expected = " /* [[[ a ]]]*/ a dummy/*[[[end]]] */"
            header   = "a"
            body     = ""
            valid_marker(input, expected, header, body)

        def test_18(self):
            input    = " /* [[[ a ]]]*/dummy dummy/*[[[end]]] */"
            expected = " /* [[[ a ]]]*/dummy a dummy/*[[[end]]] */"
            header   = "a"
            body     = ""
            valid_marker(input, expected, header, body)

    class Test_SeveralLinesMarker:
        def test_1(self):
            input    = "[[[\n" \
                       "a\n" \
                       "]]]def\n" \
                       "[[[ end ]]]"
            expected = "[[[\n" \
                       "a\n" \
                       "]]]def\n" \
                       "a\n" \
                       "[[[ end ]]]"
            header   = "a"
            body     = ""
            valid_marker(input, expected, header, body)

        def test_2(self):
            input    = "    [[[\n" \
                       "    a\n" \
                       "    ]]] test\n" \
                       "    dummy\n" \
                       "[[[ end ]]]"
            expected = "    [[[\n" \
                       "    a\n" \
                       "    ]]] test\n" \
                       "    a\n" \
                       "[[[ end ]]]"
            header   = "a"
            body     = "    dummy"
            valid_marker(input, expected, header, body)

        def test_3(self):
            input    = "    [[[\n" \
                       "\n" \
                       "    ]]]\n" \
                       "[[[ end ]]]"
            expected = "    [[[\n" \
                       "\n" \
                       "    ]]]\n" \
                       "    \n" \
                       "[[[ end ]]]"
            header   = ""
            body     = ""
            valid_marker(input, expected, header, body)

        def test_4(self):
            input    = " // [[[\n" \
                       "    a\n" \
                       "    ]]]\n" \
                       "[[[ end ]]]"
            expected = " // [[[\n" \
                       "    a\n" \
                       "    ]]]\n" \
                       " a\n" \
                       "[[[ end ]]]"
            header   = "a"
            body     = ""
            valid_marker(input, expected, header, body)

        def test_5(self):
            input    = "\t\t[[[\n" \
                       "\t\t a\n" \
                       "\t\t]]]\n" \
                       "[[[ end ]]]"
            expected = "\t\t[[[\n" \
                       "\t\t a\n" \
                       "\t\t]]]\n" \
                       "\t\t a\n" \
                       "[[[ end ]]]"
            header   = " a"
            body     = ""
            valid_marker(input, expected, header, body)

        def test_6(self):
            input    = " //\t[[[\n" \
                       "   \ta\n" \
                       "   \t]]]\n" \
                       "     dummy\n" \
                       "     dummy\n" \
                       "[[[ end ]]]"
            expected = " //\t[[[\n" \
                       "   \ta\n" \
                       "   \t]]]\n" \
                       " a\n" \
                       "[[[ end ]]]"
            header   = "a"
            body     = "     dummy\n     dummy"
            valid_marker(input, expected, header, body)

        def test_7(self):
            input    = " //\t[[[\n" \
                       " //\t]]]\n" \
                       "[[[ end ]]]"
            expected = " //\t[[[\n" \
                       " //\t]]]\n" \
                       "[[[ end ]]]"
            header   = ""
            body     = ""
            valid_marker(input, expected, header, body)

        def test_8(self):
            input    = " //\t[[[ \n" \
                       " //\t]]]\n" \
                       "[[[ end ]]]"
            expected = " //\t[[[ \n" \
                       " //\t]]]\n" \
                       " \n" \
                       "[[[ end ]]]"
            header   = ""
            body     = ""
            valid_marker(input, expected, header, body)

        def test_9(self):
            input    = " //\t[[[  \n" \
                       " //\t]]]\n" \
                       "[[[ end ]]]"
            expected = " //\t[[[  \n" \
                       " //\t]]]\n" \
                       "  \n" \
                       "[[[ end ]]]"
            header   = " "
            body     = ""
            valid_marker(input, expected, header, body)

        def test_10(self):
            input    = " // [[[\n" \
                       " //  ]]]\n" \
                       "[[[ end ]]]"
            expected = " // [[[\n" \
                       " //  ]]]\n" \
                       " \n" \
                       "[[[ end ]]]"
            header   = ""
            body     = ""
            valid_marker(input, expected, header, body)

        def test_1(self):
            input    = " // [[[\n" \
                       " //   ]]]\n" \
                       " dummy\n" \
                       "[[[ end ]]]"
            expected = " // [[[\n" \
                       " //   ]]]\n" \
                       "  \n" \
                       "[[[ end ]]]"
            header   = " "
            body     = " dummy"
            valid_marker(input, expected, header, body)

        def test_12(self):
            input    = " // [[[ \n" \
                       " //  ]]]\n" \
                       "[[[ end ]]]"
            expected = " // [[[ \n" \
                       " //  ]]]\n" \
                       " \n" \
                       "[[[ end ]]]"
            header   = "\n"
            body     = ""
            valid_marker(input, expected, header, body)

        def test_13(self):
            input    = " // [[[ abc\n" \
                       " // def ]]]\n" \
                       "[[[ end ]]]"
            expected = " // [[[ abc\n" \
                       " // def ]]]\n" \
                       " abc\n" \
                       " def\n" \
                       "[[[ end ]]]"
            header   = "abc\ndef"
            body     = ""
            valid_marker(input, expected, header, body)

        def test_14(self):
            input    = "//[[[ abc\n" \
                       "//def ]]]\n" \
                       "[[[ end ]]]"
            expected = "//[[[ abc\n" \
                       "//def ]]]\n" \
                       "abc\n" \
                       "def\n" \
                       "[[[ end ]]]"
            header   = "abc\ndef"
            body     = ""
            valid_marker(input, expected, header, body)

        def test_15(self):
            input    = "[[[ abc\n" \
                       "\n" \
                       "def ]]]\n" \
                       "[[[ end ]]]"
            expected = "[[[ abc\n" \
                       "\n" \
                       "def ]]]\n" \
                       "abc\n" \
                       "\n" \
                       "def\n" \
                       "[[[ end ]]]"
            header   = "abc\n\ndef"
            body     = ""
            valid_marker(input, expected, header, body)

        def test_16(self):
            input    = "[[[\n" \
                       "a\n" \
                       "\n" \
                       "]]]\n" \
                       "[[[ end ]]]"
            expected = "[[[\n" \
                       "a\n" \
                       "\n" \
                       "]]]\n" \
                       "a\n" \
                       "[[[ end ]]]"
            header   = "a\n"
            body     = ""
            valid_marker(input, expected, header, body)

        def test_17(self):
            input    = "    [[[\n" \
                       "    a\n" \
                       "\n" \
                       "    ]]]\n" \
                       "    dummy\n" \
                       "[[[ end ]]]"
            expected = "    [[[\n" \
                       "    a\n" \
                       "\n" \
                       "    ]]]\n" \
                       "    a\n" \
                       "[[[ end ]]]"
            header   = "a\n"
            body     = "    dummy"
            valid_marker(input, expected, header, body)

        def test_18(self):
            input    = "    [[[\n" \
                       "    \n" \
                       "    a\n" \
                       "    ]]]\n" \
                       "[[[ end ]]]"
            expected = "    [[[\n" \
                       "    \n" \
                       "    a\n" \
                       "    ]]]\n" \
                       "    \n" \
                       "    a\n" \
                       "[[[ end ]]]"
            header   = "\na"
            body     = ""
            valid_marker(input, expected, header, body)

    class Test_CommentMarkers:
        def test_1(self):
            input    = "/**  \t  **//**end **/"
            expected = "/**  \t  **/  \t  /**end **/"
            header   = " \t "
            body     = ""
            valid_marker(input, expected, header, body, settings = settingsCogComment)

        def test_2(self):
            input    = "//\t/**  \t  **//**end **/"
            expected = "//\t/**  \t  **/  \t  /**end **/"
            header   = " \t "
            body     = ""
            valid_marker(input, expected, header, body, settings = settingsCogComment)

        def test_3(self):
            input    = "  /**     **/\n" \
                       "/** end **/"
            expected = "  /**     **/\n" \
                       "     \n" \
                       "/** end **/"
            header   = "   "
            body     = ""
            valid_marker(input, expected, header, body, settings = settingsCogComment)

        def test_4(self):
            input    = "/**\n" \
                       "\n" \
                       "**/\n" \
                       "/** end **/"
            expected = "/**\n" \
                       "\n" \
                       "**/\n" \
                       "\n" \
                       "/** end **/"
            header   = ""
            body     = ""
            valid_marker(input, expected, header, body, settings = settingsCogComment)

        def test_5(self):
            input    = "    /**\n" \
                       "    \n" \
                       "    **/\n" \
                       "/** end **/"
            expected = "    /**\n" \
                       "    \n" \
                       "    **/\n" \
                       "    \n" \
                       "/** end **/"
            header   = ""
            body     = ""
            valid_marker(input, expected, header, body, settings = settingsCogComment)

        def test_6(self):
            input    = "///**\n" \
                       "//\n" \
                       "//**/\n" \
                       "///** end **/"
            expected = "///**\n" \
                       "//\n" \
                       "//**/\n" \
                       "  \n" \
                       "///** end **/"
            header   = ""
            body     = ""
            valid_marker(input, expected, header, body, settings = settingsCogComment)

        def test_7(self):
            input    = " // /**\n" \
                       " // \n" \
                       " // **/\n" \
                       "/** end **/"
            expected = " // /**\n" \
                       " // \n" \
                       " // **/\n" \
                       "    \n" \
                       "/** end **/"
            header   = ""
            body     = ""
            valid_marker(input, expected, header, body, settings = settingsCogComment)

    class Test_RemoveMarkers:
        def test_1(self):
            input    = "//\n" \
                       "    [[[ a ]]] \n" \
                       "    \n" \
                       "    [[[ end ]]] \n"
            expected = "//\n" \
                       "    a\n"
            header   = "a"
            body     = "    "
            valid_marker(input, expected, header, body, remove_markers = True)

        def test_2(self):
            input    = "//\n" \
                       "    [[[ a ]]] \n" \
                       "    \n" \
                       "    [[[ end ]]] \n" \
                       "[[[ def ]]] [[[ end ]]] \n"
            expected = "//\n" \
                       "    a\n" \
                       "def \n"
            header   = "a"
            body     = "    "
            valid_marker(input, expected, header, body, remove_markers = True)

        def test_3(self):
            input    = "//\n" \
                       "    [[[ a ]]]\n" \
                       "    \n" \
                       "    [[[end]]] \n" \
                       "def\n"
            expected = "//\n" \
                       "    a\n" \
                       "def\n"
            header   = "a"
            body     = "    "
            valid_marker(input, expected, header, body, remove_markers = True)

        def test_4(self):
            input    = "//\n" \
                       "    [[[\n" \
                       "    \n" \
                       "    a\n" \
                       "    ]]]\n" \
                       "    [[[ end ]]] "
            expected = "//\n" \
                       "    \n" \
                       "    a\n"
            header   = "\na"
            body     = ""
            valid_marker(input, expected, header, body, remove_markers = True)

        def test_5(self):
            input    = " // [[[ a ]]] abc [[[ end ]]] \n"
            expected = " // a \n"
            header0  = "a"
            body0    = "abc"
            valid_marker(input, expected, header0, body0, remove_markers = True)

        def test_6(self):
            input    = " // [[[ a ]]] abc [[[ end ]]] dummy [[[ bde ]]] b [[[ end ]]] \n"
            expected = " // a dummy bde \n"
            header0  = "a"
            body0    = "abc"
            header2  = "bde"
            body2    = "b"
            valid_marker(input, expected, header0, body0, None, None, header2, body2, remove_markers = True)

        def test_7(self):
            input    = " // [[[ a ]]] abc [[[ end ]]]dummy [[[ bde ]]] b [[[ end ]]] \n"
            expected = " // adummy bde \n"
            header0  = "a"
            body0    = "abc"
            header2  = "bde"
            body2    = "b"
            valid_marker(input, expected, header0, body0, None, None, header2, body2, remove_markers = True)

        def test_8(self):
            input    = " // [[[ a ]]] abc [[[ end ]]] dummy[[[ bde ]]] b [[[ end ]]] \n"
            expected = " // a dummybde \n"
            header0  = "a"
            body0    = "abc"
            header2  = "bde"
            body2    = "b"
            valid_marker(input, expected, header0, body0, None, None, header2, body2, remove_markers = True)

        def test_9(self):
            input    = " /**[[[ a ]]]**/ abc /**[[[ end ]]]**/ dummy/**[[[ bde ]]]**/ b **/[[[ end ]]]**/ \n"
            expected = " /**a**/ dummy/**bde**/ \n"
            header0  = "a"
            body0    = "abc"
            header2  = "bde"
            body2    = "b"
            valid_marker(input, expected, header0, body0, None, None, header2, body2, remove_markers = True)

        def test_10(self):
            input    = "  [[[\n" \
                       "    <<[ abc ]>>\n" \
                       "    <<[ end ]>>\n" \
                       "  ]]]\n" \
                       "  [[[ end ]]]"
            expected = ""
            header0  = "  <<[ abc ]>>\n" \
                       "  <<[ end ]>>"
            body0    = ""
            valid_marker(input, expected, header0, body0, None, None, None, None, remove_markers = True)

class Test_EditMarkers:
    class Test_OneLineMarker:
        def test_1(self):
            input    = "<<[]>><<[end]>>"
            expected = "<<[]>>  <<[end]>>"
            header   = ""
            body     = ""
            valid_marker(input, expected, header, body)

        def test_2(self):
            input    = "<<[]>> abc <<[end]>>"
            expected = "<<[]>> abc <<[end]>>"
            header   = ""
            body     = "abc"
            valid_marker(input, expected, header, body)

        def test_3(self):
            input    = " <<[ ]>>  abc <<[end ]>>"
            expected = " <<[ ]>>  abc <<[end ]>>"
            header   = ""
            body     = " abc"
            valid_marker(input, expected, header, body)

        def test_4(self):
            input    = "  <<[  ]>> abc  <<[ end]>>"
            expected = "  <<[  ]>> abc  <<[ end]>>"
            header   = ""
            body     = "abc "
            valid_marker(input, expected, header, body)

        def test_5(self):
            input    = "<<[a]>> abc <<[ end ]>> "
            expected = "<<[a]>> abc <<[ end ]>> "
            header   = "a"
            body     = "abc"
            valid_marker(input, expected, header, body)

        def test_6(self):
            input    = "<<[ a]>> <<[end]>>  "
            expected = "<<[ a]>>  <<[end]>>  "
            header   = "a"
            body     = ""
            valid_marker(input, expected, header, body)

        def test_7(self):
            input    = "<<[a ]>>  <<[end]>>"
            expected = "<<[a ]>>  <<[end]>>"
            header   = "a"
            body     = ""
            valid_marker(input, expected, header, body)

        def test_8(self):
            input    = "<<[ a ]>>   <<[end]>>"
            expected = "<<[ a ]>>   <<[end]>>"
            header   = "a"
            body     = " "
            valid_marker(input, expected, header, body)

        def test_9(self):
            input    = "<<[   ]>><<[ end]>>"
            expected = "<<[   ]>>  <<[ end]>>"
            header   = " "
            body     = ""
            valid_marker(input, expected, header, body)

        def test_10(self):
            input    = "<<[  \t  ]>><<[end ]>>"
            expected = "<<[  \t  ]>>  <<[end ]>>"
            header   = " \t "
            body     = ""
            valid_marker(input, expected, header, body)

        def test_11(self):
            input    = "  <<[     ]>>\n" \
                       "<<[ end ]>>"
            expected = "  <<[     ]>>\n" \
                       "<<[ end ]>>"
            header   = "   "
            body     = ""
            valid_marker(input, expected, header, body)

        def test_12(self):
            input    = " <<[a    ]>> \n" \
                       " dummy\n" \
                       " <<[end]>>"
            expected = " <<[a    ]>> \n" \
                       " dummy\n" \
                       " <<[end]>>"
            header   = "a   "
            body     = " dummy"
            valid_marker(input, expected, header, body)

        def test_13(self):
            input    = "<<[    a]>>  \n" \
                       "  <<[end]>> "
            expected = "<<[    a]>>  \n" \
                       "  <<[end]>> "
            header   = "   a"
            body     = ""
            valid_marker(input, expected, header, body)

        def test_14(self):
            input    = "<<[]>>  \n" \
                       "  <<[end]>> "
            expected = "<<[]>>  \n" \
                       "  <<[end]>> "
            header   = ""
            body     = ""
            valid_marker(input, expected, header, body)

        def test_15(self):
            input    = " /* <<[ a ]>>*/ dummy /*<<[end]>> */"
            expected = " /* <<[ a ]>>*/ dummy /*<<[end]>> */"
            header   = "a"
            body     = "dummy"
            valid_marker(input, expected, header, body)

        def test_16(self):
            input    = " /* <<[ a ]>>*/dummy /*<<[end]>> */"
            expected = " /* <<[ a ]>>*/dummy  /*<<[end]>> */"
            header   = "a"
            body     = ""
            valid_marker(input, expected, header, body)

        def test_17(self):
            input    = " /* <<[ a ]>>*/ dummy/*<<[end]>> */"
            expected = " /* <<[ a ]>>*/  dummy/*<<[end]>> */"
            header   = "a"
            body     = ""
            valid_marker(input, expected, header, body)

        def test_18(self):
            input    = " /* <<[ a ]>>*/dummy dummy/*<<[end]>> */"
            expected = " /* <<[ a ]>>*/dummy  dummy/*<<[end]>> */"
            header   = "a"
            body     = ""
            valid_marker(input, expected, header, body)

    class Test_SeveralLinesMarker:
        pass # Not possible

    class Test_CommentMarkers:
        def test_1(self):
            input    = "/**  \t  **//**end **/"
            expected = "/**  \t  **/  /**end **/"
            header   = " \t "
            body     = ""
            valid_marker(input, expected, header, body, settings = settingsEditComment)

        def test_2(self):
            input    = "//\t/**  \t  **//**end **/"
            expected = "//\t/**  \t  **/  /**end **/"
            header   = " \t "
            body     = ""
            valid_marker(input, expected, header, body, settings = settingsEditComment)

        def test_3(self):
            input    = "  /**     **/\n" \
                       "/** end **/"
            expected = "  /**     **/\n" \
                       "/** end **/"
            header   = "   "
            body     = ""
            valid_marker(input, expected, header, body, settings = settingsEditComment)

    class Test_RemoveMarkers:
        def test_1(self):
            input    = "//\n" \
                       "    <<[ a ]>> \n" \
                       "    \n" \
                       "    <<[ end ]>> \n"
            expected = "//\n" \
                       "    \n"
            header   = "a"
            body     = "    "
            valid_marker(input, expected, header, body, remove_markers = True)

        def test_2(self):
            input    = "//\n" \
                       "    <<[ a ]>> \n" \
                       "    \n" \
                       "    <<[ end ]>> \n" \
                       "<<[ def ]>> test <<[ end ]>> \n"
            expected = "//\n" \
                       "    \n" \
                       "test \n"
            header   = "a"
            body     = "    "
            valid_marker(input, expected, header, body, remove_markers = True)

        def test_3(self):
            input    = "//\n" \
                       "    <<[ a ]>>\n" \
                       "    test\n" \
                       "    <<[end]>> \n" \
                       "def\n"
            expected = "//\n" \
                       "    test\n" \
                       "def\n"
            header   = "a"
            body     = "    test"
            valid_marker(input, expected, header, body, remove_markers = True)

        def test_4(self):
            input    = " // <<[ a ]>> abc <<[ end ]>> \n"
            expected = " // abc \n"
            header0  = "a"
            body0    = "abc"
            valid_marker(input, expected, header0, body0, remove_markers = True)

        def test_5(self):
            input    = " // <<[ a ]>> abc <<[ end ]>> dummy <<[ bde ]>> b <<[ end ]>> \n"
            expected = " // abc dummy b \n"
            header0  = "a"
            body0    = "abc"
            header2  = "bde"
            body2    = "b"
            valid_marker(input, expected, header0, body0, None, None, header2, body2, remove_markers = True)

        def test_6(self):
            input    = " // <<[ a ]>> abc <<[ end ]>>dummy <<[ bde ]>> b <<[ end ]>> \n"
            expected = " // abcdummy b \n"
            header0  = "a"
            body0    = "abc"
            header2  = "bde"
            body2    = "b"
            valid_marker(input, expected, header0, body0, None, None, header2, body2, remove_markers = True)

        def test_7(self):
            input    = " // <<[ a ]>> abc <<[ end ]>> dummy<<[ bde ]>> b <<[ end ]>> \n"
            expected = " // abc dummyb \n"
            header0  = "a"
            body0    = "abc"
            header2  = "bde"
            body2    = "b"
            valid_marker(input, expected, header0, body0, None, None, header2, body2, remove_markers = True)

        def test_8(self):
            input    = " /**<<[ a ]>>**/ abc /**<<[ end ]>>**/ dummy/**<<[ bde ]>>**/ b **/<<[ end ]>>**/ \n"
            expected = " /**abc**/ dummy/**b**/ \n"
            header0  = "a"
            body0    = "abc"
            header2  = "bde"
            body2    = "b"
            valid_marker(input, expected, header0, body0, None, None, header2, body2, remove_markers = True)

class Test_BothMarkers:
    class Test_Both:
        def test_1(self):
            input = "// [[[ <<[ a ]>> ab <<[ end ]>> ]]]\n" \
                    "//   [[[ ]]][[[ end ]]]\n" \
                    "//   <<[ a ]>> <<[ end ]>>\n" \
                    "//   [[[ ]]][[[ end ]]]\n" \
                    "// [[[ end ]]]"
            valid_marker(input, None)

        def test_2(self):
            input    = "// [[[ <<[ a ]>> dummy <<[ end ]>> ]]]\n" \
                       "<<[ a ]>> test <<[ end ]>>\n" \
                       "// [[[ end ]]]"
            expected = "// [[[ <<[ a ]>> dummy <<[ end ]>> ]]]\n" \
                       "<<[ a ]>> test <<[ end ]>>\n" \
                       "// [[[ end ]]]"
            header0  = "<<[ a ]>> dummy <<[ end ]>>"
            body0    = "<<[ a ]>> test <<[ end ]>>"
            valid_marker(input, expected, header0, body0)

        def test_3(self):
            input    = "// [[[\n" \
                       "// def\n" \
                       "// // <<[ abc ]>>\n" \
                       "// // <<[ end ]>>\n" \
                       "// \n" \
                       "// ]]]\n" \
                       "// <<[ abc ]>>\n" \
                       "123\n" \
                       "// <<[ end ]>>\n" \
                       "// [[[ end ]]]"
            expected = "// [[[\n" \
                       "// def\n" \
                       "// // <<[ abc ]>>\n" \
                       "// // <<[ end ]>>\n" \
                       "// \n" \
                       "// ]]]\n" \
                       "def\n" \
                       "// <<[ abc ]>>\n" \
                       "123\n" \
                       "// <<[ end ]>>\n" \
                       "// [[[ end ]]]"
            header0  = "def\n" \
                       "// <<[ abc ]>>\n" \
                       "// <<[ end ]>>\n"
            body0    = "// <<[ abc ]>>\n" \
                       "123\n" \
                       "// <<[ end ]>>"
            header1  = "abc"
            body1    = "123"
            valid_marker(input, expected, header0, body0, header1, body1)

        def test_4(self):
            input    = "// [[[\n" \
                       "// def\n" \
                       "// // <<[ abc ]>>\n" \
                       "// // <<[ end ]>>\n" \
                       "// // <<[ hgi ]>>\n" \
                       "// // <<[ end ]>>\n" \
                       "// ]]]\n" \
                       "// <<[ abc ]>>\n" \
                       "123\n" \
                       "// <<[ end ]>>\n" \
                       "// [[[ end ]]]"
            expected = "// [[[\n" \
                       "// def\n" \
                       "// // <<[ abc ]>>\n" \
                       "// // <<[ end ]>>\n" \
                       "// // <<[ hgi ]>>\n" \
                       "// // <<[ end ]>>\n" \
                       "// ]]]\n" \
                       "def\n" \
                       "// <<[ abc ]>>\n" \
                       "123\n" \
                       "// <<[ end ]>>\n" \
                       "// <<[ hgi ]>>\n" \
                       "// <<[ end ]>>\n" \
                       "// [[[ end ]]]"
            header0  = "def\n" \
                       "// <<[ abc ]>>\n" \
                       "// <<[ end ]>>\n" \
                       "// <<[ hgi ]>>\n" \
                       "// <<[ end ]>>"
            body0    = "// <<[ abc ]>>\n" \
                       "123\n" \
                       "// <<[ end ]>>"
            header1  = "abc"
            body1    = "123"
            valid_marker(input, expected, header0, body0, header1, body1)

        def test_5(self):
            input    = "// [[[ <<[ abc ]>><<[ end ]>> ]]]\n" \
                       "// [[[ end ]]]"
            expected = "// [[[ <<[ abc ]>><<[ end ]>> ]]]\n" \
                       "<<[ abc ]>>  <<[ end ]>>\n" \
                       "// [[[ end ]]]"
            header   = "<<[ abc ]>><<[ end ]>>"
            body     = ""
            valid_marker(input, expected, header, body)

        def test_6(self):
            input    = "// [[[ <<[ abc ]>><<[ end ]>> ]]][[[ end ]]]"
            expected = "// [[[ <<[ abc ]>><<[ end ]>> ]]] <<[ abc ]>>  <<[ end ]>> [[[ end ]]]"
            header   = "<<[ abc ]>><<[ end ]>>"
            body     = ""
            valid_marker(input, expected, header, body)

        def test_7(self):
            input    = "// [[[ <<[ abc ]>><<[ end ]>> ]]] <<[ abc ]>> afz <<[ end ]>> [[[ end ]]]"
            expected = "// [[[ <<[ abc ]>><<[ end ]>> ]]] <<[ abc ]>> afz <<[ end ]>> [[[ end ]]]"
            header0  = "<<[ abc ]>><<[ end ]>>"
            body0    = "<<[ abc ]>> afz <<[ end ]>>"
            header1  = "abc"
            body1    = "afz"
            valid_marker(input, expected, header0, body0, header1, body1)

        def test_8(self):
            input    = "// [[[\n" \
                       "//     // <<[ abc ]>>\n" \
                       "//     // <<[ end ]>>\n" \
                       "// ]]]\n" \
                       "    // <<[ abc ]>>\n" \
                       "    hello\n" \
                       "    // <<[ end ]>>\n" \
                       "// [[[ end ]]]"
            expected = "// [[[\n" \
                       "//     // <<[ abc ]>>\n" \
                       "//     // <<[ end ]>>\n" \
                       "// ]]]\n" \
                       "    // <<[ abc ]>>\n" \
                       "    hello\n" \
                       "    // <<[ end ]>>\n" \
                       "// [[[ end ]]]"
            header0  = "    // <<[ abc ]>>\n" \
                       "    // <<[ end ]>>"
            body0    = "    // <<[ abc ]>>\n" \
                       "    hello\n" \
                       "    // <<[ end ]>>"
            header1  = "abc"
            body1    = "    hello"
            valid_marker(input, expected, header0, body0, header1, body1)

        def test_9(self):
            input    = "  // [[[\n" \
                       "  //     // <<[ abc ]>>\n" \
                       "  //     // <<[ end ]>>\n" \
                       "  // ]]]\n" \
                       "      // <<[ abc ]>>\n" \
                       "          // [[[ <<[ def ]>><<[ end ]>> ]]] <<[ def ]>> test <<[ end ]>> [[[ end ]]]\n" \
                       "      // <<[ end ]>>\n" \
                       "  // [[[ end ]]]"
            expected = "  // [[[\n" \
                       "  //     // <<[ abc ]>>\n" \
                       "  //     // <<[ end ]>>\n" \
                       "  // ]]]\n" \
                       "      // <<[ abc ]>>\n" \
                       "          // [[[ <<[ def ]>><<[ end ]>> ]]] <<[ def ]>> test <<[ end ]>> [[[ end ]]]\n" \
                       "      // <<[ end ]>>\n" \
                       "  // [[[ end ]]]"
            header0  = "    // <<[ abc ]>>\n" \
                       "    // <<[ end ]>>"
            body0    = "      // <<[ abc ]>>\n" \
                       "          // [[[ <<[ def ]>><<[ end ]>> ]]] <<[ def ]>> test <<[ end ]>> [[[ end ]]]\n" \
                       "      // <<[ end ]>>"
            header1  = "abc"
            body1    = "          // [[[ <<[ def ]>><<[ end ]>> ]]] <<[ def ]>> test <<[ end ]>> [[[ end ]]]"
            header2  = "<<[ def ]>><<[ end ]>>"
            body2    = "<<[ def ]>> test <<[ end ]>>"
            header3  = "def"
            body3    = "test"
            valid_marker(input, expected, header0, body0, header1, body1, header2, body2, header3, body3)

        def test_10(self):
            input    = "// [[[]]]\n" \
                       "    // <<[ abc ]>>\n" \
                       "      test\n" \
                       "    // <<[ end ]>>\n" \
                       "// [[[ end ]]]\n" \
                       "  // [[[\n" \
                       "  //         // <<[ abc ]>>\n" \
                       "  //         // <<[ end ]>>\n" \
                       "  // ]]]\n" \
                       "  // [[[ end ]]]\n"
            expected = "// [[[]]]\n" \
                       "// [[[ end ]]]\n" \
                       "  // [[[\n" \
                       "  //         // <<[ abc ]>>\n" \
                       "  //         // <<[ end ]>>\n" \
                       "  // ]]]\n" \
                       "          // <<[ abc ]>>\n" \
                       "            test\n" \
                       "          // <<[ end ]>>\n" \
                       "  // [[[ end ]]]\n"
            header0  = ""
            body0    = "    // <<[ abc ]>>\n" \
                       "      test\n" \
                       "    // <<[ end ]>>"
            header1  = "abc"
            body1    =  "      test"
            valid_marker(input, expected, header0, body0, header1, body1)

    class Test_RemoveMarkers:
        def test_1(self):
            input    = "// [[[ <<[ a ]>> dummy <<[ end ]>> ]]]\n" \
                       "<<[ a ]>> test <<[ end ]>>\n" \
                       "// [[[ end ]]]"
            expected = "test\n"
            header0  = "<<[ a ]>> dummy <<[ end ]>>"
            body0    = "<<[ a ]>> test <<[ end ]>>"
            valid_marker(input, expected, header0, body0, remove_markers = True)

        def test_2(self):
            input    = "// [[[\n" \
                       "// def\n" \
                       "// // <<[ abc ]>>\n" \
                       "// // <<[ end ]>>\n" \
                       "// ]]]\n" \
                       "// <<[ abc ]>>\n" \
                       "123\n" \
                       "// <<[ end ]>>\n" \
                       "// [[[ end ]]]"
            expected = "def\n" \
                       "123\n"
            header0  = "def\n" \
                       "// <<[ abc ]>>\n" \
                       "// <<[ end ]>>"
            body0    = "// <<[ abc ]>>\n" \
                       "123\n" \
                       "// <<[ end ]>>"
            header1  = "abc"
            body1    = "123"
            valid_marker(input, expected, header0, body0, header1, body1, remove_markers = True)

        def test_3(self):
            input    = "// [[[\n" \
                       "// def\n" \
                       "// // <<[ abc ]>>\n" \
                       "// // <<[ end ]>>\n" \
                       "// // <<[ hgi ]>>\n" \
                       "// // <<[ end ]>>\n" \
                       "// ]]]\n" \
                       "// <<[ abc ]>>\n" \
                       "123\n" \
                       "// <<[ end ]>>\n" \
                       "// [[[ end ]]]"
            expected = "def\n" \
                       "123\n"
            header0  = "def\n" \
                       "// <<[ abc ]>>\n" \
                       "// <<[ end ]>>\n" \
                       "// <<[ hgi ]>>\n" \
                       "// <<[ end ]>>"
            body0    = "// <<[ abc ]>>\n" \
                       "123\n" \
                       "// <<[ end ]>>"
            header1  = "abc"
            body1    = "123"
            valid_marker(input, expected, header0, body0, header1, body1, remove_markers = True)

        def test_4(self):
            input    = "// [[[ <<[ abc ]>><<[ end ]>> ]]]\n" \
                       "// [[[ end ]]]"
            expected = ""
            header   = "<<[ abc ]>><<[ end ]>>"
            body     = ""
            valid_marker(input, expected, header, body, remove_markers = True)

        def test_5(self):
            input    = "// [[[ <<[ abc ]>><<[ end ]>> ]]][[[ end ]]]"
            expected = "// "
            header   = "<<[ abc ]>><<[ end ]>>"
            body     = ""
            valid_marker(input, expected, header, body, remove_markers = True)

        def test_6(self):
            input    = "// [[[ <<[ abc ]>><<[ end ]>> ]]] <<[ abc ]>> afz <<[ end ]>> [[[ end ]]]"
            expected = "// afz"
            header0  = "<<[ abc ]>><<[ end ]>>"
            body0    = "<<[ abc ]>> afz <<[ end ]>>"
            header1  = "abc"
            body1    = "afz"
            valid_marker(input, expected, header0, body0, header1, body1, remove_markers = True)

        def test_7(self):
            input    = "// [[[\n" \
                       "//     // <<[ abc ]>>\n" \
                       "//     // <<[ end ]>>\n" \
                       "// ]]]\n" \
                       "    // <<[ abc ]>>\n" \
                       "    hello\n" \
                       "    // <<[ end ]>>\n" \
                       "// [[[ end ]]]"
            expected = "    hello\n"
            header0  = "    // <<[ abc ]>>\n" \
                       "    // <<[ end ]>>"
            body0    = "    // <<[ abc ]>>\n" \
                       "    hello\n" \
                       "    // <<[ end ]>>"
            header1  = "abc"
            body1    = "    hello"
            valid_marker(input, expected, header0, body0, header1, body1, remove_markers = True)

        def test_8(self):
            input    = "  // [[[\n" \
                       "  //     // <<[ abc ]>>\n" \
                       "  //     // <<[ end ]>>\n" \
                       "  // ]]]\n" \
                       "      // <<[ abc ]>>\n" \
                       "          // [[[ <<[ def ]>><<[ end ]>> ]]] <<[ def ]>> test <<[ end ]>> [[[ end ]]]\n" \
                       "      // <<[ end ]>>\n" \
                       "  // [[[ end ]]]"
            expected = "          // test\n"
            header0  = "    // <<[ abc ]>>\n" \
                       "    // <<[ end ]>>"
            body0    = "      // <<[ abc ]>>\n" \
                       "          // [[[ <<[ def ]>><<[ end ]>> ]]] <<[ def ]>> test <<[ end ]>> [[[ end ]]]\n" \
                       "      // <<[ end ]>>"
            header1  = "abc"
            body1    = "          // [[[ <<[ def ]>><<[ end ]>> ]]] <<[ def ]>> test <<[ end ]>> [[[ end ]]]"
            header2  = "<<[ def ]>><<[ end ]>>"
            body2    = "<<[ def ]>> test <<[ end ]>>"
            header3  = "def"
            body3    = "test"
            valid_marker(input, expected, header0, body0, header1, body1, header2, body2, header3, body3, remove_markers = True)

        def test_9(self):
            input    = "// [[[]]]\n" \
                       "    // <<[ abc ]>>\n" \
                       "      test\n" \
                       "    // <<[ end ]>>\n" \
                       "// [[[ end ]]]\n" \
                       "  // [[[\n" \
                       "  //         // <<[ abc ]>>\n" \
                       "  //         // <<[ end ]>>\n" \
                       "  // ]]]\n" \
                       "  // [[[ end ]]]\n"
            expected = "            test\n"
            header0  = ""
            body0    = "    // <<[ abc ]>>\n" \
                       "      test\n" \
                       "    // <<[ end ]>>"
            header1  = "abc"
            body1    = "      test"
            valid_marker(input, expected, header0, body0, header1, body1, remove_markers = True)

        def test_10(self): ### TRICKY RSTRIP
            input    = "// [[[\n" \
                       "// def\n" \
                       "// // <<[ abc ]>>\n" \
                       "// // <<[ end ]>>\n" \
                       "// \n" \
                       "// \n" \
                       "// \n" \
                       "// ]]]\n" \
                       "// <<[ abc ]>>\n" \
                       "123\n" \
                       "// <<[ end ]>>\n" \
                       "// [[[ end ]]]"
            expected = "def\n" \
                       "123\n" \
                       "\n" \
                       "\n"
            header0  = "def\n" \
                       "// <<[ abc ]>>\n" \
                       "// <<[ end ]>>\n" \
                       "\n" \
                       "\n"
            body0    = "// <<[ abc ]>>\n" \
                       "123\n" \
                       "// <<[ end ]>>"
            header1  = "abc"
            body1    = "123"
            valid_marker(input, expected, header0, body0, header1, body1, remove_markers = True)
