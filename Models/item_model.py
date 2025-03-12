from pydantic import BaseModel, Field, HttpUrl, EmailStr

class ImageModel(BaseModel):
    url: HttpUrl
    name: str

class ItemModel(BaseModel):
    name: str
    description: str | None
    quantity: int
    price: float
    category: set[str] = []
    image: ImageModel

class BaseUserModel(BaseModel):
    name: str
    email: EmailStr
    age: int

class UserOutModel(BaseUserModel):
    pass

class UserInModel(BaseUserModel):
    password: str
    
class FilterModel(BaseModel):
    model_config = {"extra": "forbid"}
    limit: int | None = Field(None, le=100, ge=0)

class LoginInModel(BaseModel):
    username: str = Field(min_length=8, max_length=25)
    password: str = Field(min_length=8)