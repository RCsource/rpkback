from pydantic import BaseModel


def to_camel(attr: str) -> str:
    words = iter(attr.split("_"))
    return next(words) + "".join(map(lambda s: s.title(), words))


class BaseModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class DetailSchema(BaseModel):
    detail: str
