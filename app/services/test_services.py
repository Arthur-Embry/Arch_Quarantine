#import base dependencies for stable functions
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Union, List
from pydantic import BaseModel
import app.fallback as fallback
import os, sys, shutil

#import the models
from app.models.test_models import *

#Function specific dependencies
import requests
import openai
from openai.error import RateLimitError
import logging
import backoff

#configure libraries
openai.api_key = os.getenv("OPENAI_API_KEY")
logging.basicConfig(level=logging.INFO)

noop_config = fallback.noop_config

#create echo test function
def echo_test_run(item: echo_test_params, noop=noop_config) -> Union[str,None] | None | JSONResponse:
    """
    ## Echo Test
    A function that returns the response parameter to test if the server can be pinged
    With the JS SDK, we can use ```echo_test({"response":"hello world"}).then(res=>console.log(res))``` to test if the server is up
    """
    def driver(params):
        #echo response
        return params.response
    return fallback.fallback(driver, item, noop)

#create proxy test function
def proxy_test_run(item: proxy_test_params, noop=noop_config) -> Union[str,None] | None | JSONResponse:
    """
    ## Proxy Test
    A function that returns the runs a proxy request to the url parameter to test if the connection is working on the request side
    With the JS SDK, we can use ```proxy_test({"url":"https://stackoverflow.com/"}).then(res=>console.log(res))``` to test if the server is up
    """
    def driver(params):
        #set headers
        req_headers = {
        'accept-language':params.acceptLanguage,
        'dnt':params.dnt,
        'sec-ch-ua':params.secChua,
        'sec-ch-ua-mobile':params.secChuaMobile,
        'sec-ch-ua-platform':params.secChuaPlatform,
        'sec-fetch-dest':params.secFetchDest,
        'user-agent':params.userAgent
        }

        #get and parse
        req = requests.get(params.url, headers=req_headers)

        #return response
        return req
    return fallback.fallback(driver, item, noop)


#create gpt stream test function
def gpt_stream_test_run(item: gpt_stream_test_params, noop=noop_config) -> StreamingResponse | JSONResponse:
    """
    ## GPT Stream Test
    A function that returns the runs a proxy request to the url parameter to test if the connection is working on the request side
    With the JS SDK, we can use ```gpt_stream_test({}).then(res=>console.log(res))``` to test if the server is up
    """
    def stable_chat(params):

        #setup logging
        def log_backoff(details):
            logging.info(f"Backing off {details['wait']} seconds afters {details['tries']} tries calling function {details['target']}")

        #catch rate limits
        @backoff.on_exception(backoff.expo, RateLimitError, max_tries=8, on_backoff=log_backoff)
        def call_openai(params):
            #call openai
            gpt_iter = openai.ChatCompletion.create(
                engine=params.engine,
                messages=params.messageLog,
                temperature=params.temperature,
                max_tokens=params.maxTokens,
                stream=True
            )
            #stream openai response
            def iterfile():
                for i in gpt_iter:
                    yield str(i.choices[0].text)
            
            return StreamingResponse(iterfile(), media_type="text/plain")
        
        return call_openai(params)
    
    return fallback.fallback(stable_chat, item, noop)