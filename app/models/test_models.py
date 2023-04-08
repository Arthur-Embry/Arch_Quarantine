from fastapi.responses import StreamingResponse
from typing import Union, List
from pydantic import BaseModel


class echo_test_params(BaseModel):
    response: Union[str,None]="hello world"

class proxy_test_params(BaseModel):
    url: Union[str,None]="https://stackoverflow.com/"
    acceptLanguage: Union[str,None]="en-US,en;q=0.9"
    dnt: Union[str,None] = "1"
    secChua: Union[str,None] = '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"'
    secChuaMobile: Union[str,None] = '?0'
    secChuaPlatform: Union[str,None] = '"Windows"'
    secFetchDest: Union[str,None] = 'empty'
    userAgent: Union[str,None] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36'

class message_params(BaseModel):
    role: str
    content: str
class gpt_stream_test_params(BaseModel):
    engine: Union[str,None]="gpt-4" # can be text-davinci-gpt-3.5-turbo, gpt-4 as this is uses the chat completion
    temperature: float=0.9
    messageLog: List[message_params] = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
        {"role": "user", "content": "Where was it played?"}
    ]
    prompt: Union[str,None]="Hello"
    maxTokens: int=2048