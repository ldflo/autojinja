from . import exceptions
from . import parser
from . import utils

import io
import jinja2
import os.path

class RawTemplate:
    """ Shared Jinja2 environment """
    environment = None

    @staticmethod
    def create_environment(*args, **kwargs):
        if "keep_trailing_newline" not in kwargs:
            kwargs["keep_trailing_newline"] = True
        if "lstrip_blocks" not in kwargs:
            kwargs["lstrip_blocks"] = True
        if "trim_blocks" not in kwargs:
            kwargs["trim_blocks"] = True
        if "undefined" not in kwargs:
            kwargs["undefined"] = jinja2.StrictUndefined
        return jinja2.Environment(*args, **kwargs)

    def __init__(self, string, input = None, output = None, encoding = None, newline = None, globals = None):
        if RawTemplate.environment == None:
            RawTemplate.environment = RawTemplate.create_environment()
        template = RawTemplate.environment.from_string(source = string, globals = globals)
        if input != None:
            template.filename = input
        else:
            template.filename = exceptions.format_text(string)
        self.jinja2_template = template
        self.string = string
        self.input = input
        self.output = output
        self.encoding = encoding
        self.newline = newline
    def __getattr__(self, attr):
        return getattr(self.template, attr)

    @staticmethod
    def from_file(input, output = None, encoding = None, newline = None, globals = None):
        try:
            with open(input, 'r', encoding = encoding or "utf-8") as file:
                return RawTemplate(file.read(), input, output, encoding, newline, globals)
        except BaseException as e:
            raise exceptions.clean_traceback(e) from None
    @staticmethod
    def from_string(string, output = None, encoding = None, newline = None, globals = None):
        try:
            return RawTemplate(string, None, output, encoding, newline, globals)
        except BaseException as e:
            raise exceptions.clean_traceback(e) from None

    def render_file(self, output = None, encoding = None, newline = None):
        try:
            return self.context().render_file(output, encoding, newline)
        except BaseException as e:
            raise exceptions.clean_traceback(e) from None
    def render(self):
        try:
            return self.context().render()
        except BaseException as e:
            raise exceptions.clean_traceback(e) from None

    def context(__autojinja_self__, *args, **kwargs):
        if "self" in kwargs:
            kwargs["this"] = kwargs["self"] # Avoid conflict with Jinja2
            del kwargs["self"]
        return RawTemplate.Context(__autojinja_self__, args, kwargs)

    class Context:
        """ Forwards Jinja2 data model """
        def __init__(self, template, args = (), kwargs = {}):
            self.template = template
            self.args = args
            self.kwargs = kwargs
        def __getattr__(self, attr):
            return getattr(self.template, attr)

        def render_file(self, output = None, encoding = None, newline = None):
            try:
                output = output or self.output
                assert output != None, "output filepath parameter can't be None"
                result = self.jinja2_template.render(*self.args, **self.kwargs)
                utils.generate_file(output, result, None, encoding or self.encoding, newline or self.newline)
                return result
            except BaseException as e:
                raise exceptions.clean_traceback(e) from None
        def render(self):
            try:
                return self.jinja2_template.render(*self.args, **self.kwargs)
            except BaseException as e:
                raise exceptions.clean_traceback(e) from None

class BaseTemplate:
    def __init__(self, string, input = None, output = None, settings = None, remove_markers = None, encoding = None, newline = None, globals = None):
        self.string = string
        self.input = input
        self.output = output
        self.settings = settings or parser.ParserSettings()
        self.remove_markers = remove_markers
        self.encoding = encoding
        self.newline = newline
        self.globals = globals
        self.overriden_edits = None
        self.parser = None

    @property
    def remove_markers(self):
        return self._removeMarkers or self.settings.remove_markers
    @remove_markers.setter
    def remove_markers(self, remove_markers):
        self._removeMarkers = remove_markers

    @property
    def encoding(self):
        return self._encoding or self.settings.encoding
    @encoding.setter
    def encoding(self, encoding):
        self._encoding = encoding

    @property
    def newline(self):
        return self._newline or self.settings.newline
    @newline.setter
    def newline(self, newline):
        self._newline = newline

    @property
    def markers(self):
        return self.parser.markers
    @property
    def blocks(self):
        return self.parser.blocks
    @property
    def cog_blocks(self):
        return self.parser.cog_blocks
    @property
    def edit_blocks(self):
        return self.parser.edit_blocks

    @property
    def edits(self):
        if self.overriden_edits == None:
            return self.parser.edits
        return self.overriden_edits.copy()
    @edits.setter
    def edits(self, edits):
        self.overriden_edits = edits

    def render_file(self, output = None, remove_markers = None, encoding = None, newline = None):
        try:
            return self.context().render_file(output, remove_markers, encoding, newline)
        except BaseException as e:
            raise exceptions.clean_traceback(e) from None
    def render(self, output = None, remove_markers = None):
        try:
            return self.context().render(output, remove_markers)
        except BaseException as e:
            raise exceptions.clean_traceback(e) from None

    def context(__autojinja_self__, *args, **kwargs):
        if "self" in kwargs:
            kwargs["this"] = kwargs["self"] # Avoid conflict with Jinja2
            del kwargs["self"]
        return BaseTemplate.Context(__autojinja_self__, args, kwargs)

    class Context:
        """ Forwards Jinja2 data model """
        def __init__(self, template, args = (), kwargs = {}):
            self.template = template
            self.args = args
            self.kwargs = kwargs
        def __getattr__(self, attr):
            return getattr(self.template, attr)

        def render_file(self, output = None, remove_markers = None, encoding = None, newline = None):
            try:
                output = output or self.output
                assert output != None, "output filepath parameter can't be None"
                ### Retrieve output edits
                edit_blocks_to_generate = {} # Dict[str, EditBlock], for generation
                if not os.path.isfile(output): # File doesn't exist
                    old_content = None
                elif self.input and os.path.samefile(self.input, output): # Same file
                    old_content = self.string
                else: # Not same file
                    with open(output, 'r', encoding = encoding or self.encoding or "utf-8") as file:
                        old_content = file.read()
                        edit_blocks = utils.edit_blocks_from_string(old_content, self.settings)
                        edit_blocks_to_generate.update(edit_blocks)
                ### Render
                result = self.parser.generate(edit_blocks_to_generate, self.overriden_edits, remove_markers or self.remove_markers, self.globals, self.args, self.kwargs)
                utils.generate_file(output, result, old_content, encoding or self.encoding, newline or self.newline)
                return result
            except BaseException as e:
                raise exceptions.clean_traceback(e) from None
        def render(self, output = None, remove_markers = None):
            try:
                ### Retrieve output edits
                edit_blocks_to_generate = {} # Dict[str, EditBlock], for generation
                if output != None:
                    edit_blocks = utils.edit_blocks_from_string(output, self.settings)
                    edit_blocks_to_generate.update(edit_blocks)
                ### Render
                return self.parser.generate(edit_blocks_to_generate, self.overriden_edits, remove_markers or self.remove_markers, self.globals, self.args, self.kwargs)
            except BaseException as e:
                raise exceptions.clean_traceback(e) from None

class CogTemplate(BaseTemplate):
    def __init__(self, string, input = None, output = None, settings = None, remove_markers = None, encoding = None, newline = None, globals = None):
        super().__init__(string, input, output or input, settings, remove_markers, encoding, newline, globals)
        self.parser = CogGenerator(string, self.settings)
        self.parser.parse()

    @staticmethod
    def from_file(input, output = None, settings = None, remove_markers = None, encoding = None, newline = None, globals = None):
        try:
            with open(input, 'r', encoding = encoding or (settings.encoding if settings else None) or "utf-8") as file:
                return CogTemplate(file.read(), input, output, settings, remove_markers, encoding, newline, globals)
        except BaseException as e:
            raise exceptions.clean_traceback(e) from None
    @staticmethod
    def from_string(string, output = None, settings = None, remove_markers = None, encoding = None, newline = None, globals = None):
        try:
            return CogTemplate(string, None, output, settings, remove_markers, encoding, newline, globals)
        except BaseException as e:
            raise exceptions.clean_traceback(e) from None

class JinjaTemplate(BaseTemplate):
    def __init__(self, string, input = None, output = None, settings = None, remove_markers = None, encoding = None, newline = None, globals = None):
        super().__init__(string, input, output, settings, remove_markers, encoding, newline, globals)
        self.parser = JinjaGenerator(string, self.settings)
        self.parser.parse()

    @staticmethod
    def from_file(input, output = None, settings = None, remove_markers = None, encoding = None, newline = None, globals = None):
        try:
            with open(input, 'r', encoding = encoding or (settings.encoding if settings else None) or "utf-8") as file:
                return JinjaTemplate(file.read(), input, output, settings, remove_markers, encoding, newline, globals)
        except BaseException as e:
            raise exceptions.clean_traceback(e) from None
    @staticmethod
    def from_string(string, output = None, settings = None, remove_markers = None, encoding = None, newline = None, globals = None):
        try:
            return JinjaTemplate(string, None, output, settings, remove_markers, encoding, newline, globals)
        except BaseException as e:
            raise exceptions.clean_traceback(e) from None

### Generators

class BaseGenerator(parser.Parser):
    def __init__(self, string, settings):
        super().__init__(string, settings)

    def generate(self, edit_blocks_to_generate, overriden_edits, remove_markers, globals, args, kwargs):
        ### Save settings
        old_remove_markers = self.settings.remove_markers
        if self.settings.remove_markers != remove_markers:
            self.settings.remove_markers = remove_markers
        try:
            ### Generate
            self.edit_blocks_to_generate = self.edit_blocks.copy()
            self.overriden_edits = overriden_edits
            self.edit_blocks_generated = set()
            self.globals = globals
            self.args = args
            self.kwargs = kwargs
            output = self.generate_output(edit_blocks_to_generate) # To inherit
            ### Check unused edits
            diff = set(self.edit_blocks_to_generate) - self.edit_blocks_generated
            for name in diff:
                block = self.edit_blocks_to_generate[name]
                if not block.allow_code_loss:
                    raise exceptions.NonGeneratedEditException.from_marker(block.marker)
        finally:
            ### Restore settings
            if self.settings.remove_markers != old_remove_markers:
                self.settings.remove_markers = old_remove_markers
        return output

    def evaluate(self, string):
        generator = CogGenerator(string, self.settings)
        generator.parse()
        generator.edit_blocks_to_generate = generator.edit_blocks.copy()
        generator.edit_blocks_to_generate.update(self.edit_blocks_to_generate)
        generator.overriden_edits = self.overriden_edits
        generator.edit_blocks_generated = self.edit_blocks_generated
        generator.globals = self.globals
        generator.args = self.args
        generator.kwargs = self.kwargs
        return generator.generate_output({})

class CogGenerator(BaseGenerator):
    def __init__(self, string, settings):
        super().__init__(string, settings)

    def generate_output(self, edit_blocks_to_generate):
        self.edit_blocks_to_generate.update(edit_blocks_to_generate) # Update for generation
        stringio = io.StringIO()
        idx = 0
        depth = 0
        for marker in self.markers:
            ### End marker
            if marker.is_end:
                depth -= 1
                if depth == 0:
                    if not self.settings.remove_markers:
                        ### Write header
                        stringio.write(self.string[marker.header_start:marker.header_end])
                    idx = marker.header_end
            ### Open marker
            else:
                depth += 1
                if depth == 1:
                    stringio.write(self.string[idx:marker.header_start])
                    if not self.settings.remove_markers:
                        ### Write header
                        stringio.write(self.string[marker.header_start:marker.header_end])
                    ### Generate
                    output = self.generate_marker(marker)
                    ### Same line
                    if marker.body_inline:
                        if output == None:
                            output = ""
                        elif '\n' in output:
                            raise exceptions.RequireBodyInlineException.from_marker(marker)
                        if not self.settings.remove_markers:
                            stringio.write(f" {output} ")
                        else:
                            stringio.write(output)
                    ### Different lines
                    elif output != None:
                        bodyIndent = marker.header_indent[:marker.body_column]
                        output = output.replace('\n', f"\n{bodyIndent}")
                        stringio.write(f"{bodyIndent}{output}\n")
        ### End of file
        stringio.write(self.string[idx:])
        return stringio.getvalue()

    def generate_marker(self, marker):
        if not marker.is_edit:
            if marker.header_empty:
                return None
            ### Generate raw template
            template = RawTemplate(marker.header, globals = self.globals)
            output = template.context(*self.args, **self.kwargs).render()
        else:
            ### Check if edit already used
            key = marker.header_stripped
            if key in self.edit_blocks_generated:
                raise exceptions.AlreadyGeneratedEditException.from_marker(marker)
            self.edit_blocks_generated.add(key)
            ### Get edit body
            if self.overriden_edits != None and key in self.overriden_edits:
                output = self.overriden_edits[key]
            else:
                edit_block = self.edit_blocks_to_generate.get(key)
                output = edit_block.body if edit_block else None
            if output == None:
                return None
        if len(output) == 0:
            return ""
        try:
            ### Parse and generate again
            result = self.evaluate(output)
            if result.endswith('\n'):
                result = result[:-1]
            if self.settings.remove_markers and len(result) == 0:
                return None
            return result
        except BaseException as e:
            raise exceptions.CommonException.from_exception(e, marker) from None

class JinjaGenerator(BaseGenerator):
    def __init__(self, string, settings):
        super().__init__(string, settings)

    def generate_output(self, edit_blocks_to_generate):
        to_reinsert = {} # str -> [Marker, Marker]
        stringio = io.StringIO()
        idx = 0
        depth = 0
        prev_list = None
        for marker in self.markers:
            ### End marker
            if marker.is_end:
                if not marker.is_edit:
                    depth -= 1
                    if depth == 0:
                        prev_list[1] = marker # Update previous reinsert
                        idx = marker.header_end
                else:
                    if depth == 0:
                        stringio.write(self.string[idx:marker.header_end])
                        idx = marker.header_end
            ### Open marker
            else:
                if not marker.is_edit:
                    depth += 1
                    if depth == 1:
                        prev_list = [marker, None]
                        id = self.unique_id(idx)
                        to_reinsert[id] = prev_list # Update reinserts
                        stringio.write(self.string[idx:marker.header_start])
                        stringio.write(id) # Write id for later reinsertion
                else:
                    if depth == 0:
                        del self.edit_blocks_to_generate[marker.header_stripped] # Update for generation
        ### End of file
        stringio.write(self.string[idx:])
        return self.generate_reinsert(stringio.getvalue(), to_reinsert, edit_blocks_to_generate)

    def generate_reinsert(self, string, to_reinsert, edit_blocks_to_generate):
        ### Generate raw template
        template = RawTemplate(string, globals = self.globals)
        output = template.context(*self.args, **self.kwargs).render()
        ### Reinsert cog markers
        for id, (marker_start, marker_end) in to_reinsert.items():
            if not marker_start.is_edit:
                content = self.string[marker_start.header_start:marker_end.header_end]
                output = output.replace(id, content)
        ### Parse and generate again
        self.edit_blocks_to_generate.update(edit_blocks_to_generate) # Update for generation
        if len(output) > 0:
            output = self.evaluate(output)
        return output

    def unique_id(self, idx):
        return f"°#@[AUTOJINJA_{idx}]+&*"
