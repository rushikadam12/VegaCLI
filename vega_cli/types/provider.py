from pydantic import BaseModel

class ProviderConfig(BaseModel):
    name: str
    api_key: str
    api_base: str
    model: str
