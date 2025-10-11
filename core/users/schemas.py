from pydantic import BaseModel,Field,field_validator
from typing import Optional
from datetime import datetime


class UserRegisterSchema(BaseModel):
    username: str = Field(...,max_length=250,description="username of the user")
    password: str = Field(...,description="password of user")
    password_confirm: str = Field(...,description="confirm password of user")

    @field_validator("password_confirm")
    def check_passwords_match(cls,password_confirm,validation):
        if not (password_confirm == validation.data.get("password")):
            raise ValueError("passwords doesnt match")
        return password_confirm



class UserLoginSchema(BaseModel):
    username: str = Field(...,max_length=250,description="username of the user")
    password: str = Field(...,description="password of user")


