import jinja2
import pkg_resources
import os

class PkgResourceLoader(jinja2.BaseLoader):

    def __init__(self, lang):
        self.pkgname = __name__
        self.lang = lang

    def get_source(self, environment, name):
        path = os.path.join("templates",self.lang, f'{name}.jinja')
        if not pkg_resources.resource_exists(__name__, path):
            raise jinja2.TemplateNotFound(path)
        
        source = pkg_resources.resource_string(__name__, path)
        return source.decode(), path, lambda: True
        
templateEnv = jinja2.Environment(loader=PkgResourceLoader('python'))


class Base:        

    def render(self):
        return templateEnv.get_template(self.__class__.__name__.lower()).render(input=self)

class Model(Base):
    def __init__(self, parent, name, is_internal, attrs, indexes, unique, references, actions, config):
        super().__init__()
        self.parent = parent
        self.name = name
        self.is_internal = is_internal
        self.attrs = attrs
        self.indexes = indexes
        self.unique = unique
        self.references = references
        self.actions = actions
        self.config = config
        self.reverseRef = []

    def resolveReferences(self):
        for ref in self.references:
            fieldName = ref.model.name.lower()
            islist = False if ref.relation == '1-1' else True

            localModelAttr = Attr(self, f'{fieldName}_ref', None, ref.model, islist, ref.optional, None, True)

            # Add unique index
            if not islist:
                self.indexes.append(Index(self,[FieldOrder(self, localModelAttr, False)]))

            #Create attr in local model
            self.attrs.append(localModelAttr)

            #Create attr in referenced model
            # remoteModelAttr = Attr(ref.model, f'{fieldName}ReverseRef', None, self, islist, ref.optional, None, True)
            ref.model.reverseRef.append(self)


class Attr(Base):
    def __init__(self, parent, name, simpletype, model_or_enum, list, optional, default, ref=False):
        super().__init__()
        self.parent = parent
        self.name = name
        self.model_or_enum = model_or_enum
        self.simpletype = simpletype
        self.list = list
        self.optional = optional
        self.default = default
        self.ref = ref

        if isinstance(self.simpletype, StrSpec) and self.default is not None:
            self.default = f'"{self.default}"'
        if self.optional and self.list and self.default == None:
            self.default = []

        if self.simpletype and self.optional and self.default == None:
            if isinstance(self.simpletype, IntSpec):
                self.default = 0
            elif isinstance(self.simpletype, FloatSpec):
                self.default = 0.0
            elif isinstance(self.simpletype, BoolSpec):
                self.default = False
            elif isinstance(self.simpletype, StrSpec):
                self.default = '""'            

class IntSpec(Base):
    def __init__(self, parent, max, min, multiple, default):
        super().__init__()
        self.parent = parent
        self.name = 'int'
        self.max = max
        self.min = min
        self.multiple = multiple
        self.default = default

    def has_params(self):
        return self.max or self.min

class FloatSpec(Base):
    def __init__(self, parent, max, min):
        super().__init__()
        self.parent = parent
        self.max = max
        self.min = min

    def has_params(self):
        return self.max or self.min

class StrSpec(Base):
    def __init__(self, parent, maxlen, minlen, regex, startswith, endswith, contains):
        super().__init__()
        self.parent = parent
        self.name = 'str'
        self.maxlen = maxlen
        self.minlen = minlen
        self.regex = regex
        self.startswith = startswith
        self.endswith = endswith
        self.contains = contains

    def has_params(self):
        return self.maxlen or self.minlen or self.regex or self.startswith or self.endswith or self.contains

class BoolSpec(Base):
    def __init__(self, parent, x):
        super().__init__()
        self.name = 'bool'
        self.parent = parent

    def has_params(self):
        return False
class EmailSpec(Base):
    def __init__(self, parent, x):
        super().__init__()
        self.parent = parent

    def has_params(self):
        return False
        
class Datetime(Base):
    def __init__(self, parent, x):
        super().__init__()
        self.parent = parent

    def has_params(self):
        return False
class Date(Base):
    def __init__(self, parent, x):
        super().__init__()
        self.parent = parent

    def has_params(self):
        return False

class Time(Base):
    def __init__(self, parent, x):
        super().__init__()
        self.parent = parent

    def has_params(self):
        return False

class IpAddressv4(Base):
    def __init__(self, parent, x):
        super().__init__()
        self.parent = parent

    def has_params(self):
        return False

class IpAddressv6(Base):
    def __init__(self, parent, x):
        super().__init__()
        self.parent = parent

    def has_params(self):
        return False

class Secret(Base):
    def __init__(self, parent, x):
        super().__init__()
        self.parent = parent
        self.name = 'secret'

    def has_params(self):
        return False
class Index(Base):
    def __init__(self, parent, fields):
        super().__init__()
        self.parent = parent
        self.fields = fields

class FieldOrder(Base):
    def __init__(self, parent, field, sort):
        super().__init__()
        self.parent = parent
        self.field = field
        self.sort = sort

class Unique(Base):
    def __init__(self, parent, fields, tenant):
        super().__init__()
        self.parent = parent
        self.fields = fields
        self.tenant = tenant

class Reference(Base):
    def __init__(self, parent, model, attrs, relation, optional):
        super().__init__()
        self.parent = parent
        self.model = model
        self.attrs = attrs
        self.relation = relation
        self.optional = optional


class Enum(Base):
    def __init__(self, parent, name, str, fields) -> None:
        super().__init__()
        self.parent = parent
        self.name = name
        self.str = str
        self.fields = fields

        # Set proper values for enum to be rendered in template
        if not self.str:
            for index, field in enumerate(self.fields):
                if not field.value:
                    if index == 0:
                        field.value = 0
                    else:
                        field.value = self.fields[index-1].value + 1


class Action(Base):
    def __init__(self, parent, name, params) -> None:
        super().__init__()
        self.parent = parent
        self.name = name
        self.params = params

class StdApiFile(Base):
    def __init__(self, models) -> None:
        super().__init__()
        self.models = models


class ModelsFile(Base):
    def __init__(self, models) -> None:
        super().__init__()
        self.models = models

class EnumsFile(Base):
    def __init__(self, enums) -> None:
        super().__init__()
        self.enums = enums
