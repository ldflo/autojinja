from .defaults import *
from .exceptions import *

import io
import os

class ParserSettings:
    def __init__(self,
                 cog_open = AUTOJINJA_DEFAULT_COG_OPEN,
                 cog_close = AUTOJINJA_DEFAULT_COG_CLOSE,
                 cog_end = AUTOJINJA_DEFAULT_COG_END,
                 cog_as_comment = False,
                 edit_open = AUTOJINJA_DEFAULT_EDIT_OPEN,
                 edit_close = AUTOJINJA_DEFAULT_EDIT_CLOSE,
                 edit_end = AUTOJINJA_DEFAULT_EDIT_END,
                 edit_as_comment = False,
                 remove_markers = None,
                 encoding = None,
                 newline = None):
        self.cog_open = cog_open
        self.cog_close = cog_close
        self.cog_end = cog_end
        self.cog_as_comment = cog_as_comment
        self.edit_open = edit_open
        self.edit_close = edit_close
        self.edit_end = edit_end
        self.edit_as_comment = edit_as_comment
        self.remove_markers = remove_markers
        self.encoding = encoding
        self.newline = newline

    @property
    def remove_markers(self):
        return self._removeMarkers
    @remove_markers.setter
    def remove_markers(self, remove_markers):
        if remove_markers != None:
            self._removeMarkers = remove_markers
        elif AUTOJINJA_REMOVE_MARKERS not in os.environ:
            self._removeMarkers = False
        else:
            value = os.environ[AUTOJINJA_REMOVE_MARKERS]
            if not value.isdigit() or int(value) < 0 or int(value) > 1:
                raise Exception(f"Expected 0 or 1 for environment variable '{AUTOJINJA_REMOVE_MARKERS}'")
            self._removeMarkers = True if int(value) else False

class Parser:
    def __init__(self, string, settings):
        self.string = string
        self.settings = settings
        self.markers = None # List[Marker]
        self.blocks = None # List[Block]
        self.cog_blocks = None # List[CogBlock]
        self.edit_blocks = None # List[EditBlock]

    @property
    def edits(self):
        return { key: edit_block.body for key, edit_block in self.edit_blocks.items() }

    def parse(self):
        idx = 0
        cog_markers = []
        edit_markers = []
        ### Find all [[[ ]]] pairs
        while True:
            marker = Marker(self.string, False, self.settings.cog_open, self.settings.cog_close, self.settings.cog_end, self.settings.cog_as_comment, None, True)
            marker, idx = self.find_marker(marker, idx, len(self.string))
            if not marker:
                break
            cog_markers.append(marker)
        ### Find all <<[ ]>> pairs not in [[[ ]]]
        sections = [[0,-1]]
        for cog_marker in cog_markers:
            sections[-1][1] = cog_marker.header_open
            sections.append([cog_marker.header_close, -1])
        sections[-1][1] = len(self.string)
        for section in sections:
            idx = section[0]
            while True:
                marker = Marker(self.string, True, self.settings.edit_open, self.settings.edit_close, self.settings.edit_end, self.settings.edit_as_comment, True, False)
                marker, idx = self.find_marker(marker, idx, section[1])
                if not marker:
                    break
                edit_markers.append(marker)
        ### Properly resolve [[[ ]]] and <<[ ]>>
        self.markers = cog_markers + edit_markers
        self.markers.sort(key=lambda x: x.header_open)
        self.check_markers()
        ### Collect blocks
        self.blocks = []
        self.cog_blocks = []
        self.edit_blocks = {}
        for marker in self.markers:
            if not marker.is_end:
                if marker.is_edit:
                    block = EditBlock(marker)
                    if block.name in self.edit_blocks:
                        raise DuplicateEditException.from_marker(marker)
                    self.edit_blocks[block.name] = block
                else:
                    block = CogBlock(marker)
                    self.cog_blocks.append(block)
                self.blocks.append(block)

    def find_marker(self, marker, idx, end):
        ### Find open
        found, idx = self.find_token(marker.open, idx, end)
        if not found:
            return None, idx
        ### Set open location
        marker.header_open = idx
        ### Find close
        idx = idx + len(marker.open)
        found, idx = self.find_token(marker.close, idx, end)
        if not found:
            raise CloseMarkerNotFoundException.from_marker(marker)
        ### Set close location
        idx = idx + len(marker.close)
        marker.header_close = idx
        ### Extract header
        marker.extract_indent()
        marker.extract_header()
        return marker, idx

    def find_token(self, token, idx, end):
        i = self.string.find(token, idx, end)
        if i < 0:
            return False, idx
        return True, i

    def check_markers(self):
        stack = []
        prev_inline = []
        mkrstate = 0 # 0: none, 1: cog, 2: edit, 3: cog end, 4: edit end
        state = 0 # 0: no requirement, 1: waiting for requirement, 2: require other line, 3: require same line
        prev_marker = None
        for marker in self.markers:
            ### Check cog & edit markers enclosure
            newstate = 1 + marker.is_edit + 2 * marker.is_end
            if mkrstate == 1 and newstate == 4:
                raise WrongInclusionException.from_marker(marker)
            if mkrstate == 2 and newstate == 3:
                raise WrongInclusionException.from_marker(marker)
            mkrstate = newstate
            ### Check direct enclosure
            if not marker.is_end and not marker.direct_enclosure and stack and stack[-1].is_edit == marker.is_edit:
                raise DirectlyEnclosedEditException.from_marker(marker)
            ### Check requirements with previous marker
            if prev_marker:
                same_line = marker.same_line(prev_marker.header_close, marker.header_open)
                if state == 0:
                    pass
                elif state == 1:
                    state = 3 if same_line else 0
                elif state == 2:
                    if same_line:
                        raise RequireNewlineException.from_marker(marker)
                    state = 0
                elif state == 3:
                    if not same_line:
                        raise RequireInlineException.from_marker(marker)
                    state = 0
            ### Ensure marker subtree is correctly inlined
            if prev_inline:
                if prev_inline[-1] == None: # No requirement
                    prev_inline[-1] = same_line
                elif prev_inline[-1] == False: # Should be multiline
                    if same_line:
                        raise RequireNewlineException.from_marker(marker)
                elif not same_line: # Should be inlined
                    raise RequireInlineException.from_marker(marker)
            ### Deal marker
            if not marker.is_end:
                stack.append(marker)
                prev_inline.append(True if prev_inline and prev_inline[-1] else None)
                prev_marker = marker
            else:
                if not stack:
                    raise OpenMarkerNotFoundException.from_marker(marker)
                openMarker = stack.pop()
                same_line = prev_inline.pop()
                prev_marker = marker
                ### Set duals
                openMarker.dual = marker
                marker.dual = openMarker
                ### Extract body
                openMarker.extract_body(marker, same_line)
                if same_line:
                    state = 1
                    # Set start / end indexes
                    openMarker.header_start = openMarker.header_open
                    openMarker.header_end = openMarker.header_close
                    marker.header_start = marker.header_open
                    marker.header_end = marker.header_close
                else:
                    state = 2
                    # Set end indexes
                    openMarker.header_end = openMarker.header_close
                    i = self.string.find('\n', marker.header_close)
                    marker.header_end = i+1 if i >= 0 else len(self.string)
        if stack:
            raise EndMarkerNotFoundException.from_marker(stack[-1])

class Marker:
    def __init__(self, string, is_edit, open, close, end, as_comment, headerInline, directEnclosure):
        self.string = string
        self.is_edit = is_edit
        self.is_end = False
        self.open = open
        self.close = close
        self.end = end
        self.as_comment = as_comment # True or False
        self.direct_enclosure = directEnclosure # True or False
        # Header
        self.header_inline = headerInline # True: inline, False: Multiline, None: Both
        self.header_empty = True
        self.header_column = 0
        self.header = ""
        self._header_stripped = None
        self.header_start = 0 # Index, multiline / inline dependant
        self.header_end = 0 # Index, multiline / inline dependant
        self.header_open = 0 # Index, l-prolonged
        self.header_close = 0 # Index, r-prolonged
        self.header_indent_column = 0
        self.header_indent = ""
        # Body
        self.body_inline = False
        self.body_empty = True
        self.body_column = 0
        self.body = ""
        self._body_dedented = None
        self.body_start = 0 # Index, with indentation
        self.body_end = 0 # Index
        # Dual
        self.dual = None # Open or end marker

    @property
    def header_stripped(self):
        if self._header_stripped == None:
            self._header_stripped = self.header.strip()
        return self._header_stripped
    @property
    def body_dedented(self):
        if self._body_dedented == None:
            self._body_dedented = self.dedent_body()
        return self._body_dedented

    def same_line(self, startidx, idx):
        i = self.string.rfind('\n', startidx, idx)
        return i < 0

    def extract_indent(self):
        start = self.string.rfind('\n', 0, self.header_open)+1
        end = start
        body = self.header_open
        i = self.header_open
        while i > start:
            i -= 1
            if self.string[i] != ' ' and self.string[i] != '\t':
                end = i+1 # Comment end
                if not self.as_comment:
                    body = start
                    while i > start:
                        i -= 1
                        if self.string[i] == ' ' or self.string[i] == '\t':
                            body = i+1 # Comment start
                            break
                break
        self.header_column = self.header_open - start
        self.header_start = start
        self.header_indent_column = end - start
        self.header_indent = ''.join(['\t' if x == '\t' else ' ' for x in self.string[start:self.header_open]])
        self.body_column = body - start

    def extract_header(self):
        marker_content = io.StringIO()
        self.header_empty = True
        idx = self.header_close - len(self.close)
        start = self.header_open + len(self.open)
        ### Same line
        if self.same_line(self.header_open, idx):
            if self.header_inline == False:
                raise RequireHeaderMultilineException.from_marker(self)
            if self.string[start] == ' ':
                start += 1
            if self.string[idx-1] == ' ':
                idx -= 1
            marker_content.write(self.string[start:idx])
            self.header_empty = idx <= start
        ### Different lines
        else:
            if self.header_inline == True:
                raise RequireHeaderInlineException.from_marker(self)
            # First line
            i = self.string.find('\n', start, idx)
            if i > start:
                if self.string[start] == ' ':
                    start += 1
                marker_content.write(self.string[start:i])
                self.header_empty = False
            # Other lines
            while True:
                start = i+1
                i = self.string.find('\n', start, idx)
                # Middle lines
                if i >= 0:
                    self.check_indent(start, i)
                    if not self.header_empty:
                        marker_content.write('\n')
                    marker_content.write(self.string[start+self.header_column:i])
                    self.header_empty = False
                # Last line
                else:
                    self.check_indent(start, idx)
                    if idx-start > self.header_column:
                        if self.string[idx-1] == ' ':
                            idx -= 1
                        if not self.header_empty:
                            marker_content.write('\n')
                        marker_content.write(self.string[start+self.header_column:idx])
                        self.header_empty = False
                    break
        self.header = marker_content.getvalue()
        self.is_end = self.header == self.end

    def extract_body(self, end_marker, same_line):
        body = io.StringIO()
        ### Same line
        if same_line:
            self.body_inline = True
            i = self.string.find(' ', self.header_close, end_marker.header_open)
            if i < 0:
                self.body_start = self.header_close
            else:
                self.body_start = i+1
                self.header_close = i # Adjust marker (marker prolongement)
            i = self.string.rfind(' ', self.header_close, end_marker.header_open)
            if i < 0:
                self.body_end = end_marker.header_open
            else:
                self.body_end = i
                end_marker.header_open = i+1 # Adjust marker (marker prolongement)
            body.write(self.string[self.body_start:self.body_end])
        ### Different lines
        else:
            self.body_inline = False
            self.body_start = self.string.find('\n', self.header_close) + 1
            self.body_end = self.string.rfind('\n', self.header_close, end_marker.header_open) + 1
            self.header_close = self.body_start
            body.write(self.string[self.body_start:self.body_end-1])
        self.body = body.getvalue()
        self.body_empty = len(self.body) == 0

    def check_indent(self, start, end):
        idx = start + self.header_indent_column
        for i in range(start, start+self.header_column):
            if i < end:
                if self.string[i] == ' ':
                    if self.header_indent[i-start] != '\t': continue
                elif self.string[i] == '\t':
                    if self.header_indent[i-start] == '\t': continue
                elif i < idx: continue # Eat until comment end
            elif i >= idx and self.string[i] == '\n':
                break
            raise WrongHeaderIndentationException.from_marker(self, i)

    def dedent_body(self):
        if self.body_empty:
            return None
        if self.body_inline:
            return self.body
        return self.dedent(self.body)

    def dedent(self, output):
        result = io.StringIO()
        start = 0
        while True:
            idx = output.find('\n', start, len(output))
            mid = min(start + self.body_column, len(output) if idx < 0 else idx)
            for i in range(start, mid):
                if output[i] != ' ' and output[i] != '\t':
                    result.write(output[i:mid])
                    break
            if idx < 0:
                result.write(output[mid:])
                break
            else:
                end = idx+1
                result.write(output[mid:end])
                start = end
        return result.getvalue()

class Block:
    def __init__(self, marker):
        self.marker = marker

    @property
    def raw_header(self):
        return self.marker.header
    @property
    def header(self):
        return self.marker.header_stripped

    @property
    def raw_body(self):
        return self.marker.body
    @property
    def body(self):
        return self.marker.body_dedented

    def get_code(self, additional_lines = (0, 0)):
        if self.marker.body_inline:
            start = self.marker.header_start
            end = self.marker.dual.header_end
            # Complete line
            start = self.marker.string.rfind('\n', 0, start)+1
            i = self.marker.string.find('\n', end)
            if i >= 0:
                end = i+1
            else:
                end = len(self.marker.string)
        else:
            start = self.marker.header_start
            end = self.marker.dual.header_end
        for i in range(additional_lines[0]):
            if start == 0:
                break
            start = self.marker.string.rfind('\n', 0, start-1)+1
        for i in range(additional_lines[1]):
            if end > len(self.marker.string):
                break
            i = self.marker.string.find('\n', end+1)
            if i >= 0:
                end = i
            else:
                end = len(self.marker.string)
        if end > 0 and self.marker.string[end-1] == '\n':
            end -= 1
        return self.marker.string[start:end]

class CogBlock(Block):
    def __init__(self, marker):
        super().__init__(marker)

class EditBlock(Block):
    def __init__(self, marker):
        super().__init__(marker)
        self._body = None
        self.allow_code_loss = False # Use at your own risk
    def __str__(self):
        return f"{self.__repr__()} named {self.name}"

    @property
    def name(self):
        return self.header

    @property
    def body(self):
        return self._body or super().body
    @body.setter
    def body(self, body):
        self._body = body
