from typing import Any, Generic, List, Optional, Set, TypeVar, Union

from pydantic import BaseModel, Extra, Field, validator
from pydantic.dataclasses import dataclass
from pydantic.generics import GenericModel


class Model(BaseModel):
    x: int
    y: str

    def method(self) -> None:
        pass

    class Config:
        alias_generator = None
        allow_mutation = False
        extra = Extra.forbid

        def config_method(self) -> None:
            ...


model = Model(x=1, y='y', z='z')
model = Model(x=1)
model.y = 'a'
Model.from_orm({})
Model.from_orm({})  # type: ignore[pydantic-orm]  # noqa F821


class ForbidExtraModel(BaseModel):
    class Config:
        extra = 'forbid'


ForbidExtraModel(x=1)


class ForbidExtraModel2(BaseModel):
    class Config:
        extra = 'forbid'
        validate_all = False

    Config.validate_all = True


ForbidExtraModel2(x=1)


class BadExtraModel(BaseModel):
    class Config:
        extra = 1  # type: ignore[pydantic-config]  # noqa F821
        extra = 1


class BadConfig1(BaseModel):
    class Config:
        orm_mode: Any = {}  # not sensible, but should still be handled gracefully


class BadConfig2(BaseModel):
    class Config:
        orm_mode = list  # not sensible, but should still be handled gracefully


class InheritingModel(Model):
    class Config:
        allow_mutation = True


class DefaultTestingModel(BaseModel):
    # Required
    a: int
    b: int = ...
    c: int = Field(...)
    d: Union[int, str]
    e = ...

    # Not required
    f: Optional[int]
    g: int = 1
    h: int = Field(1)
    i: int = Field(None)
    j = 1


DefaultTestingModel()


class UndefinedAnnotationModel(BaseModel):
    undefined: Undefined  # noqa F821


UndefinedAnnotationModel()


Model.model_construct(x=1)
Model.model_construct(_fields_set={'x'}, x=1, y='2')
Model.model_construct(x='1', y='2')

# Strict mode fails
inheriting = InheritingModel(x='1', y='1')
Model(x='1', y='2')


class Blah(BaseModel):
    fields_set: Optional[Set[str]] = None


# (comment to keep line numbers unchanged)
T = TypeVar('T')


class Response(GenericModel, Generic[T]):
    data: T
    error: Optional[str]


response = Response[Model](data=model, error=None)
response = Response[Model](data=1, error=None)


class AliasModel(BaseModel):
    x: str = Field(..., alias='y')
    z: int


AliasModel(y=1, z=2)

x_alias = 'y'


class DynamicAliasModel(BaseModel):
    x: str = Field(..., alias=x_alias)
    z: int


DynamicAliasModel(y='y', z='1')


class DynamicAliasModel2(BaseModel):
    x: str = Field(..., alias=x_alias)
    z: int

    class Config:
        allow_population_by_field_name = True


DynamicAliasModel2(y='y', z=1)
DynamicAliasModel2(x='y', z=1)


class AliasGeneratorModel(BaseModel):
    x: int

    class Config:
        alias_generator = lambda x: x + '_'  # noqa E731


AliasGeneratorModel(x=1)
AliasGeneratorModel(x_=1)
AliasGeneratorModel(z=1)


class AliasGeneratorModel2(BaseModel):
    x: int = Field(..., alias='y')

    class Config:  # type: ignore[pydantic-alias]  # noqa F821
        alias_generator = lambda x: x + '_'  # noqa E731


class UntypedFieldModel(BaseModel):
    x: int = 1
    y = 2
    z = 2  # type: ignore[pydantic-field]  # noqa F821


AliasGeneratorModel2(x=1)
AliasGeneratorModel2(y=1, z=1)


class CoverageTester(Missing):  # noqa F821
    def from_orm(self) -> None:
        pass


CoverageTester().from_orm()


@dataclass(config={})
class AddProject:
    name: str
    slug: Optional[str]
    description: Optional[str]


p = AddProject(name='x', slug='y', description='z')


# Same as Model, but with frozen = True
class FrozenModel(BaseModel):
    x: int
    y: str

    class Config:
        alias_generator = None
        frozen = True
        extra = Extra.forbid


frozenmodel = FrozenModel(x=1, y='b')
frozenmodel.y = 'a'


class InheritingModel2(FrozenModel):
    class Config:
        frozen = False


inheriting2 = InheritingModel2(x=1, y='c')
inheriting2.y = 'd'


def _default_factory() -> str:
    return 'x'


test: List[str] = []


class FieldDefaultTestingModel(BaseModel):
    # Default
    e: int = Field(None)
    f: int = None

    # Default factory
    g: str = Field(default_factory=set)
    h: int = Field(default_factory=_default_factory)
    i: List[int] = Field(default_factory=list)
    l_: str = Field(default_factory=3)

    # Default and default factory
    m: int = Field(default=1, default_factory=list)


class ModelWithAnnotatedValidator(BaseModel):
    name: str

    @validator('name')
    def noop_validator_with_annotations(self, name: str) -> str:
        # This is a mistake: the first argument to a validator is the class itself,
        # like a classmethod.
        self.instance_method()
        return name

    def instance_method(self) -> None:
        ...
