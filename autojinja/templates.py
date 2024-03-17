from . import exceptions
from . import path
from . import parser
from . import utils

import importlib.util
import inspect
import io
import sys
from types import CodeType, MethodType
from typing import Any, Callable, Dict, Generic, List, MutableMapping, Optional, Set, Tuple, Type, TypeVar, Union

###
### jinja2 API
###

### Huge hack that modifies jinja2.environment.getattr and jinja2.environment.getitem methods to avoid UndefinedErrors with properties.
### We can't simply replace the methods, as the stacktraces of the exceptions won't be located in jinja2 module and won't work.

def modify_and_import(module_name: str, package: str, modification_func: Callable[[str], str]):
    spec = importlib.util.find_spec(module_name, package)
    source = spec.loader.get_source(module_name)
    new_source = modification_func(source)
    module = importlib.util.module_from_spec(spec)
    codeobj = compile(new_source, module.__spec__.origin, "exec")
    exec(codeobj, module.__dict__)
    sys.modules[module_name] = module

def modification_func(src: str) -> str:
    src = src.replace("def getattr", """def getattr(self, obj, attribute):
        try:
            return getattr(obj, attribute)
        except AttributeError as e:
            try:
                return obj[attribute]
            except Exception:
                pass
            raise e
    def oldgetattr""")
    src = src.replace("def getitem", """def getitem(self, obj, argument):
        try:
            return obj[argument]
        except (AttributeError, TypeError, LookupError):
            if isinstance(argument, str):
                try:
                    attr = str(argument)
                except Exception:
                    pass
                else:
                    return getattr(obj, attr)
            return self.undefined(obj=obj, name=argument)
    def oldgetitem""")
    return src

modify_and_import("jinja2.environment", None, modification_func)
import jinja2
importlib.reload(jinja2)
from jinja2.nodes import Template as Jinja2TemplateNode

class CustomEnvironment(jinja2.Environment):
    """ The core component of Jinja is the `Environment`. It contains
        important shared variables like configuration, filters, tests,
        globals and others. Instances of this class may be modified if
        they are not shared and if no template was loaded so far.
        Modifications on environments after the first template was loaded
        will lead to surprising effects and undefined behavior.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
                   
    def from_string(self, source: Union[str, Jinja2TemplateNode], globals: Optional[MutableMapping[str, Any]] = None, template_class: Optional[Type[jinja2.Template]] = None, filename: Optional[str] = None, lineno: Optional[int] = None) -> jinja2.Template:
        """ Load a template from a source string without using
            :attr:`loader`.
            :param source: Jinja source to compile into a template.
            :param globals: Extend the environment :attr:`globals` with
                these extra variables available for all renders of this
                template. If the template has already been loaded and
                cached, its globals are updated with any new items.
            :param template_class: Return an instance of this
                :class:`Template` class.
        """
        gs = self.make_globals(globals)
        cls = template_class or self.template_class
        template = cls.from_code(self, self.compile(source, None, filename, None, False, lineno), gs, None)
        ### Custom lineno method
        template.old_get_corresponding_lineno = template.get_corresponding_lineno
        parent_lineno = lineno or 1
        def new_get_corresponding_lineno(self, lineno):
            return parent_lineno + self.old_get_corresponding_lineno(lineno)-1
        template.get_corresponding_lineno = MethodType(new_get_corresponding_lineno, template)
        return template
    
    def compile(self, source: Union[str, Jinja2TemplateNode], name: Optional[str] = None, filename: Optional[str] = None, raw: bool = False, defer_init: bool = False, lineno: Optional[int] = None) -> Union[str, CodeType]:
        """ Compile a node or template source code. The `name` parameter is
            the load name of the template after it was joined using
            :meth:`join_path` if necessary, not the filename on the file system.
            the `filename` parameter is the estimated filename of the template on
            the file system. If the template came from a database or memory this
            can be omitted.

            The return value of this method is a python code object.  If the `raw`
            parameter is `True` the return value will be a string with python
            code equivalent to the bytecode returned otherwise.  This method is
            mainly used internally.

            `defer_init` is use internally to aid the module code generator.  This
            causes the generated code to be able to import without the global
            environment variable to be set.

            .. versionadded:: 2.4
            `defer_init` parameter added.
        """
        source_hint = None
        try:
            if isinstance(source, str):
                source_hint = source
                source = self._parse(source, name, filename)
            source = self._generate(source, name, filename, defer_init=defer_init)
            if raw:
                return source
            if filename is None:
                filename = "<template>"
            return self._compile(source, filename)
        except jinja2.exceptions.TemplateSyntaxError as e:
            if lineno != None:
                e.lineno += lineno-1
            self.handle_exception(source=source_hint)

class AutoLoader(jinja2.BaseLoader):
    """ Jinja2 loader to find templates near already loaded templates """
    all_dirpaths_used: Set[path.Path] = set()

    def __init__(self, additional_dirpaths: Optional[List[str]]):
        if additional_dirpaths != None:
            for dirpath in additional_dirpaths:
                AutoLoader.all_dirpaths_used.add(path.Path(dirpath).slash)

    def get_source(self, environment: jinja2.Environment, template: str) -> Tuple[str, str, Callable[[], float]]:
        """ Get the template source, filename and reload helper for a template.
            It's passed the environment and template name and has to return a
            tuple in the form ``(source, filename, uptodate)`` or raise a
            `TemplateNotFound` error if it can't locate the template.

            The source part of the returned tuple must be the source of the
            template as a string. The filename should be the name of the
            file on the filesystem if it was loaded from there, otherwise
            ``None``. The filename is used by Python for the tracebacks
            if no loader extension is used.

            The last item in the tuple is the `uptodate` function.  If auto
            reloading is enabled it's always called to check if the template
            changed.  No arguments are passed so the function must store the
            old state somewhere (for example in a closure). If it returns `False`
            the template will be reloaded.
        """
        for dirpath in AutoLoader.all_dirpaths_used:
            filepath = dirpath.join(template)
            if filepath.exists:
                with open(filepath) as f:
                    source = f.read()
                mtime = path.getmtime(filepath)
                return source, filepath, lambda: mtime == path.getmtime(filepath)
        raise jinja2.TemplateNotFound(template)

###
### autojinja API
###

class Template:
    @staticmethod
    def from_file(*args, **kwargs) -> "Template":
        raise NotImplementedError() # To override
    @staticmethod
    def from_string(*args, **kwargs) -> "Template":
        raise NotImplementedError() # To override

    def context(__autojinja_self__, *args, **kwargs) -> "Context[Template]":
        raise NotImplementedError() # To override

    def render_file(self, *args, **kwargs) -> str:
        raise NotImplementedError() # To override
    def render(self) -> str:
        raise NotImplementedError() # To override

_Template = TypeVar("_Template")

class Context(Generic[_Template]):
    def __init__(self, template: _Template, args: Tuple[Any, ...] = (), kwargs: Dict[str, Any] = {}):
        self.template: _Template = template
        self.args: Tuple[Any, ...] = args
        self.kwargs: Dict[str, Any] = kwargs

    def context(__autojinja_self__, *args, **kwargs) -> "Context[_Template]":
        raise NotImplementedError() # To override

    def update(__autojinja_self__, *args, **kwargs) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
        if "self" in kwargs:
            kwargs["this"] = kwargs["self"] # Avoid conflict with Jinja2
            del kwargs["self"]
        new_args = __autojinja_self__.args + args
        new_kwargs = __autojinja_self__.kwargs.copy()
        new_kwargs.update(kwargs)
        return (new_args, new_kwargs)

    def render_file(self, *args, **kwargs) -> str:
        raise NotImplementedError() # To override
    def render(self, *args, **kwargs) -> str:
        raise NotImplementedError() # To override

class RawTemplate(Template):
    """ Shared Jinja2 environment """
    environment: CustomEnvironment = None

    @staticmethod
    def create_loader(additional_dirpaths: Optional[List[str]] = None) -> AutoLoader:
        return AutoLoader(additional_dirpaths)

    @staticmethod
    def create_environment(*args: str, **kwargs: str) -> CustomEnvironment:
        if "loader" not in kwargs:
            kwargs["loader"] = RawTemplate.create_loader()
        if "keep_trailing_newline" not in kwargs:
            kwargs["keep_trailing_newline"] = True
        if "lstrip_blocks" not in kwargs:
            kwargs["lstrip_blocks"] = True
        if "trim_blocks" not in kwargs:
            kwargs["trim_blocks"] = True
        if "undefined" not in kwargs:
            kwargs["undefined"] = jinja2.StrictUndefined
        return CustomEnvironment(*args, **kwargs)

    def __init__(self, string: str, input: Optional[str] = None, output: Optional[str] = None, encoding: Optional[str] = None, newline: Optional[str] = None, globals: Optional[Dict[str, Any]] = None, lineno: Optional[int] = None):
        if RawTemplate.environment == None:
            RawTemplate.environment = RawTemplate.create_environment()
        jinja2_template: jinja2.Template = RawTemplate.environment.from_string(string, globals, None, input or exceptions.format_text(string), lineno)
        if input != None:
            AutoLoader.all_dirpaths_used.add(path.Path(input).dirpath)
        self.jinja2_template: jinja2.Template = jinja2_template
        self.string: str = string
        self.input: Optional[str] = input
        self.output: Optional[str] = output
        self.encoding: Optional[str] = encoding
        self.newline : Optional[str] = newline

    def __getattribute__(self, attr: str):
        try:
            this_attr = object.__getattribute__(self, attr)
            if not inspect.ismethod(this_attr) or hasattr(this_attr, "__self__"):
                return this_attr
        except AttributeError:
            pass
        wrapped: jinja2.Template = object.__getattribute__(self, "jinja2_template")
        return getattr(wrapped, attr)

    @staticmethod
    def from_file(input: str, output: Optional[str] = None, encoding: Optional[str] = None, newline: Optional[str] = None, globals: Optional[Dict[str, Any]] = None) -> "RawTemplate":
        try:
            with open(input, 'r', encoding = encoding or "utf-8") as file:
                return RawTemplate(file.read(), input, output, encoding, newline, globals)
        except Exception as e:
            raise exceptions.clean_traceback(e) from None
    @staticmethod
    def from_string(string: str, output: Optional[str] = None, encoding: Optional[str] = None, newline: Optional[str] = None, globals: Optional[Dict[str, Any]] = None) -> "RawTemplate":
        try:
            return RawTemplate(string, None, output, encoding, newline, globals)
        except Exception as e:
            raise exceptions.clean_traceback(e) from None

    def context(__autojinja_self__, *args, **kwargs) -> "RawTemplateContext":
        if "self" in kwargs:
            kwargs["this"] = kwargs["self"] # Avoid conflict with Jinja2
            del kwargs["self"]
        return RawTemplateContext(__autojinja_self__, args, kwargs)

    def render_file(self, output: Optional[str] = None, encoding: Optional[str] = None, newline: Optional[str] = None) -> str:
        try:
            return self.context().render_file(output, encoding, newline)
        except Exception as e:
            raise exceptions.clean_traceback(e) from None
    def render(self) -> str:
        try:
            return self.context().render()
        except Exception as e:
            raise exceptions.clean_traceback(e) from None

class RawTemplateContext(Context[RawTemplate]):
    def __init__(self, template: RawTemplate, args: Tuple[Any, ...] = (), kwargs: Dict[str, Any] = {}):
        super().__init__(template, args, kwargs)

    def context(__autojinja_self__, *args, **kwargs) -> "RawTemplateContext":
        new_args, new_kwargs = super().update(*args, **kwargs)
        return RawTemplateContext(__autojinja_self__.template, new_args, new_kwargs)

    def render_file(self, output: str = None, encoding: Optional[str] = None, newline: Optional[str] = None) -> str:
        try:
            output = output or self.template.output
            assert output != None, "output filepath parameter can't be None"
            args, kwargs = self.args, self.kwargs
            result = self.template.jinja2_template.render(*args, **kwargs)
            utils.generate_file(output, result, None, encoding or self.template.encoding, newline or self.template.newline)
            return result
        except Exception as e:
            raise exceptions.clean_traceback(e) from None
    def render(self) -> str:
        try:
            args, kwargs = self.args, self.kwargs
            return self.template.jinja2_template.render(*args, **kwargs)
        except Exception as e:
            raise exceptions.clean_traceback(e) from None

### Generators

class BaseGenerator(parser.Parser):
    def __init__(self, string: str, settings: parser.ParserSettings, lineno: Optional[int] = None, column: Optional[int] = None):
        super().__init__(string, settings, lineno, column)

    def generate(self, edit_blocks_to_generate: Dict[str, parser.EditBlock], overriden_edits: Optional[Dict[str, str]], remove_markers: Optional[bool], globals: Optional[Dict[str, Any]], args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> str:
        ### Save settings
        old_remove_markers = self.settings.remove_markers
        if self.settings.remove_markers != remove_markers:
            self.settings.remove_markers = remove_markers
        try:
            ### Generate
            self.edit_blocks_to_generate: Dict[str, parser.EditBlock] = self.edit_blocks.copy()
            self.overriden_edits: Optional[Dict[str, str]] = overriden_edits
            self.edit_blocks_generated: Set[str] = set()
            self.globals: Optional[Dict[str, Any]] = globals
            self.args: Tuple[Any, ...] = args
            self.kwargs: Dict[str, Any] = kwargs
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

    def generate_output(self, edit_blocks_to_generate: Dict[str, parser.EditBlock]) -> str:
        raise NotImplementedError() # To override

    def evaluate(self, string: str, lineno: int, column: int) -> str:
        generator = CogGenerator(string, self.settings, lineno, column)
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
    def __init__(self, string: str, settings: parser.ParserSettings, lineno: Optional[int] = None, column: Optional[int] = None):
        super().__init__(string, settings, lineno, column)

    def generate_output(self, edit_blocks_to_generate: Dict[str, parser.EditBlock]) -> str:
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

    def generate_marker(self, marker: parser.Marker) -> str:
        if not marker.is_edit:
            if marker.header_empty:
                return None
            ### Generate raw template
            template = RawTemplate(marker.header, globals = self.globals, lineno = marker.parent_lineno + marker.header_start_lineno-1)
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
            result = self.evaluate(output, marker.parent_lineno + marker.body_lineno-1, marker.parent_column + marker.body_start_column)
            if result.endswith('\n'):
                result = result[:-1]
            if self.settings.remove_markers and len(result) == 0:
                return None
            return result
        except Exception as e:
            raise exceptions.CommonException.from_exception(e, marker) from None

class JinjaGenerator(BaseGenerator):
    def __init__(self, string: str, settings: parser.ParserSettings, lineno: Optional[int] = None, column: Optional[int] = None):
        super().__init__(string, settings, lineno, column)

    def generate_output(self, edit_blocks_to_generate: Dict[str, parser.EditBlock]) -> str:
        to_reinsert: Dict[str, Tuple[parser.Marker, parser.Marker]] = {}
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

    def generate_reinsert(self, string: str, to_reinsert: Dict[str, Tuple[parser.Marker, parser.Marker]], edit_blocks_to_generate: Dict[str, parser.EditBlock]) -> str:
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
            output = self.evaluate(output, 1, 0)
        return output

    def unique_id(self, idx: int) -> str:
        return f"°#@[AUTOJINJA_{idx}]+&*"

_Generator = TypeVar("_Generator", bound=BaseGenerator, covariant=True)

class BaseTemplate(Generic[_Generator], Template):
    def __init__(self, generator: Type[_Generator], string: str, input: Optional[str] = None, output: Optional[str] = None, settings: Optional[parser.ParserSettings] = None, remove_markers: Optional[bool] = None, encoding: Optional[str] = None, newline: Optional[str] = None, globals: Optional[Dict[str, Any]] = None):
        if input != None:
            AutoLoader.all_dirpaths_used.add(path.Path(input).dirpath)
        self.string: str = string
        self.input: Optional[str] = input
        self.output: Optional[str] = output
        self.settings: parser.ParserSettings = settings or parser.ParserSettings()
        self._remove_markers: Optional[bool] = remove_markers
        self._encoding: Optional[str] = encoding
        self._newline: Optional[str] = newline
        self.globals: Optional[Dict[str, Any]] = globals
        self.overriden_edits: Optional[Dict[str, str]] = None
        self.parser: _Generator = generator(self.string, self.settings)
        self.parser.parse()

    @property
    def remove_markers(self) -> Optional[bool]:
        return self._remove_markers or self.settings.remove_markers
    @remove_markers.setter
    def remove_markers(self, remove_markers: Optional[bool]):
        self._remove_markers = remove_markers

    @property
    def encoding(self) -> Optional[str]:
        return self._encoding or self.settings.encoding
    @encoding.setter
    def encoding(self, encoding: Optional[str]):
        self._encoding = encoding

    @property
    def newline(self) -> Optional[str]:
        return self._newline or self.settings.newline
    @newline.setter
    def newline(self, newline: Optional[str]):
        self._newline = newline

    @property
    def markers(self) -> List[parser.Marker]:
        return self.parser.markers
    @property
    def blocks(self) -> List[parser.Block]:
        return self.parser.blocks
    @property
    def cog_blocks(self) -> List[parser.CogBlock]:
        return self.parser.cog_blocks
    @property
    def edit_blocks(self) -> List[parser.EditBlock]:
        return self.parser.edit_blocks

    @property
    def edits(self) -> Dict[str, str]:
        if self.overriden_edits == None:
            return self.parser.edits
        return self.overriden_edits.copy()
    @edits.setter
    def edits(self, edits: Optional[Dict[str, str]]):
        self.overriden_edits = edits

    @staticmethod
    def from_file(*args, **kwargs) -> "Template":
        raise NotImplementedError() # To override
    @staticmethod
    def from_string(*args, **kwargs) -> "Template":
        raise NotImplementedError() # To override

    def context(__autojinja_self__, *args, **kwargs) -> "BaseTemplateContext":
        raise NotImplementedError() # To override

    def render_file(self, output: Optional[str] = None, remove_markers: Optional[bool] = None, encoding: Optional[str] = None, newline: Optional[str] = None) -> str:
        try:
            return self.context().render_file(output, remove_markers, encoding, newline)
        except Exception as e:
            raise exceptions.clean_traceback(e) from None
    def render(self, output: Optional[str] = None, remove_markers: Optional[bool] = None) -> str:
        try:
            return self.context().render(output, remove_markers)
        except Exception as e:
            raise exceptions.clean_traceback(e) from None

_BaseTemplate = TypeVar("_BaseTemplate", bound=BaseTemplate, covariant=True)

class BaseTemplateContext(Generic[_BaseTemplate], Context[_BaseTemplate]):
    def __init__(self, template: _BaseTemplate, args: Tuple[Any, ...] = (), kwargs: Dict[str, Any] = {}):
        super().__init__(template, args, kwargs)

    def context(__autojinja_self__, *args, **kwargs) -> "BaseTemplateContext[_BaseTemplate]":
        raise NotImplementedError() # To override

    def render_file(self, output: Optional[str] = None, remove_markers: Optional[bool] = None, encoding: Optional[str] = None, newline: Optional[str] = None) -> str:
        try:
            output = output or self.template.output
            assert output != None, "output filepath parameter can't be None"
            ### Retrieve output edits
            edit_blocks_to_generate: Dict[str, parser.EditBlock] = {} # For generation
            if not path.isfile(output): # File doesn't exist
                old_content = None
            elif self.template.input and path.samefile(self.template.input, output): # Same file
                old_content = self.template.string
            else: # Not same file
                with open(output, 'r', encoding = encoding or self.template.encoding or "utf-8") as file:
                    old_content = file.read()
                    edit_blocks = utils.edit_blocks_from_string(old_content, self.template.settings)
                    edit_blocks_to_generate.update(edit_blocks)
            ### Render
            result = self.template.parser.generate(edit_blocks_to_generate, self.template.overriden_edits, remove_markers or self.template.remove_markers, self.template.globals, self.args, self.kwargs)
            utils.generate_file(output, result, old_content, encoding or self.template.encoding, newline or self.template.newline)
            return result
        except Exception as e:
            raise exceptions.clean_traceback(e) from None
    def render(self, output: Optional[str] = None, remove_markers: Optional[bool] = None) -> str:
        try:
            ### Retrieve output edits
            edit_blocks_to_generate: Dict[str, parser.EditBlock] = {} # For generation
            if output != None:
                edit_blocks = utils.edit_blocks_from_string(output, self.template.settings)
                edit_blocks_to_generate.update(edit_blocks)
            ### Render
            return self.template.parser.generate(edit_blocks_to_generate, self.template.overriden_edits, remove_markers or self.template.remove_markers, self.template.globals, self.args, self.kwargs)
        except Exception as e:
            raise exceptions.clean_traceback(e) from None

class CogTemplate(BaseTemplate[CogGenerator]):
    def __init__(self, string: str, input: Optional[str] = None, output: Optional[str] = None, settings: Optional[parser.ParserSettings] = None, remove_markers: Optional[bool] = None, encoding: Optional[str] = None, newline: Optional[str] = None, globals: Optional[Dict[str, Any]] = None):
        super().__init__(CogGenerator, string, input, output or input, settings, remove_markers, encoding, newline, globals)

    @staticmethod
    def from_file(input: str, output: Optional[str] = None, settings: Optional[parser.ParserSettings] = None, remove_markers: Optional[bool] = None, encoding: Optional[str] = None, newline: Optional[str] = None, globals: Optional[Dict[str, Any]] = None) -> "CogTemplate":
        try:
            with open(input, 'r', encoding = encoding or (settings.encoding if settings else None) or "utf-8") as file:
                return CogTemplate(file.read(), input, output, settings, remove_markers, encoding, newline, globals)
        except Exception as e:
            raise exceptions.clean_traceback(e) from None
    @staticmethod
    def from_string(string: str, output: Optional[str] = None, settings: Optional[parser.ParserSettings] = None, remove_markers: Optional[bool] = None, encoding: Optional[str] = None, newline: Optional[str] = None, globals: Optional[Dict[str, Any]] = None) -> "CogTemplate":
        try:
            return CogTemplate(string, None, output, settings, remove_markers, encoding, newline, globals)
        except Exception as e:
            raise exceptions.clean_traceback(e) from None

    def context(__autojinja_self__, *args, **kwargs) -> "CogTemplateContext":
        if "self" in kwargs:
            kwargs["this"] = kwargs["self"] # Avoid conflict with Jinja2
            del kwargs["self"]
        return CogTemplateContext(__autojinja_self__, args, kwargs)

class CogTemplateContext(BaseTemplateContext[CogTemplate]):
    def __init__(self, template: CogTemplate, args: Tuple[Any, ...] = (), kwargs: Dict[str, Any] = {}):
        super().__init__(template, args, kwargs)

    def context(__autojinja_self__, *args, **kwargs) -> "CogTemplateContext":
        new_args, new_kwargs = super().update(*args, **kwargs)
        return CogTemplateContext(__autojinja_self__.template, new_args, new_kwargs)

class JinjaTemplate(BaseTemplate[JinjaGenerator]):
    def __init__(self, string: str, input: Optional[str] = None, output: Optional[str] = None, settings: Optional[parser.ParserSettings] = None, remove_markers: Optional[bool] = None, encoding: Optional[str] = None, newline: Optional[str] = None, globals: Optional[Dict[str, Any]] = None):
        super().__init__(JinjaGenerator, string, input, output, settings, remove_markers, encoding, newline, globals)

    @staticmethod
    def from_file(input: str, output: Optional[str] = None, settings: Optional[parser.ParserSettings] = None, remove_markers: Optional[bool] = None, encoding: Optional[str] = None, newline: Optional[str] = None, globals: Optional[Dict[str, Any]] = None) -> "JinjaTemplate":
        try:
            with open(input, 'r', encoding = encoding or (settings.encoding if settings else None) or "utf-8") as file:
                return JinjaTemplate(file.read(), input, output, settings, remove_markers, encoding, newline, globals)
        except Exception as e:
            raise exceptions.clean_traceback(e) from None
    @staticmethod
    def from_string(string: str, output: Optional[str] = None, settings: Optional[parser.ParserSettings] = None, remove_markers: Optional[bool] = None, encoding: Optional[str] = None, newline: Optional[str] = None, globals: Optional[Dict[str, Any]] = None) -> "JinjaTemplate":
        try:
            return JinjaTemplate(string, None, output, settings, remove_markers, encoding, newline, globals)
        except Exception as e:
            raise exceptions.clean_traceback(e) from None

    def context(__autojinja_self__, *args, **kwargs) -> "JinjaTemplateContext":
        if "self" in kwargs:
            kwargs["this"] = kwargs["self"] # Avoid conflict with Jinja2
            del kwargs["self"]
        return JinjaTemplateContext(__autojinja_self__, args, kwargs)

class JinjaTemplateContext(BaseTemplateContext[JinjaTemplate]):
    def __init__(self, template: JinjaTemplate, args: Tuple[Any, ...] = (), kwargs: Dict[str, Any] = {}):
        super().__init__(template, args, kwargs)

    def context(__autojinja_self__, *args, **kwargs) -> "JinjaTemplateContext":
        new_args, new_kwargs = super().update(*args, **kwargs)
        return JinjaTemplateContext(__autojinja_self__.template, new_args, new_kwargs)
