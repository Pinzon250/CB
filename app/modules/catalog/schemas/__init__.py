from pydantic import BaseModel

class PageMeta(BaseModel):
    page: int
    size: int
    total: int

class Page(BaseModel):
    meta: PageMeta
    items: list