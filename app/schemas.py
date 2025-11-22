from pydantic import BaseModel

class PostCreate(BaseModel):
    """FAST API  has automated data validation, which means it is going to check it's data to see if 
    it is valid or not. So we use this as body request, something like hidden information. The schema
    below inherits from BaseModel and use this as type to receive body data inside of our functions.
    """
    title: str
    content: str

class PostResponse(BaseModel):
    title: str
    content: str