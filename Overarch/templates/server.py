from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import types
import re
import markdown

description = """
Black-Wire-884601 API helps you do awesome stuff.

## Notes

___notes___

## Pages


# Restfull Endpoints
"""

app = FastAPI(
    title="Black-Wire-884601",
    description=description,
)


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#exposure template
def expose(endpoint,service):
    
    #import the service and define the function and parameters
    service_import=__import__("app.services."+service+'_services')
    function_import=service_import.__dict__['services'].__dict__[service+'_services'].__dict__[endpoint+'_run']
    function_params=service_import.__dict__['models'].__dict__[service+'_models'].__dict__[endpoint+'_params']

    # Decorate it with your decorator and then pass it to FastAPI
    def template(item: function_params):
        """TODO: add comments to this function"""
        #catch special case of default parameters changing from string to tuple
        for i in item:
            if type(i[1])==tuple:
                setattr(item, i[0].split("=")[0], i[1][0])

        return function_import(item)

    globals()[endpoint+"_global"] = types.FunctionType(template.__code__, {}, name=template.__name__, argdefs=template.__defaults__, closure=template.__closure__)
    globals()[endpoint+"_global"].__name__ = service + " - " + endpoint
    globals()[endpoint+"_global"].__annotations__ = {"item": function_params}
    if function_import.__doc__!=None:
        first_pass=markdown.markdown(str(function_import.__doc__))
        #isolate the code block
        code_block=first_pass.split("<code>")[1].split("</code>")[0]
        second_pass=markdown.markdown(code_block)
        app.post("/"+endpoint, description=second_pass)(globals()[endpoint+"_global"])
    else:
        app.post("/"+endpoint)(globals()[endpoint+"_global"])

        # Define special streaming catch
    def template_static(item: function_params):
        """This is a static function - it returns a promise, not a stream"""
        #catch special case of default parameters changing from string to tuple
        for i in item:
            if type(i[1])==tuple:
                setattr(item, i[0].split("=")[0], i[1][0])
        output=""
        #check for generator output and convert to string
        try:
            for i in function_import(item):
                output+=i
        except:
            output=function_import(item)
        return output
    globals()[endpoint+"_static_global"] = types.FunctionType(template_static.__code__, {}, name=template_static.__name__, argdefs=template_static.__defaults__, closure=template_static.__closure__)
    globals()[endpoint+"_static_global"].__name__ = service + " - " + endpoint + " static"
    globals()[endpoint+"_static_global"].__annotations__ = {"item": function_params}
    app.post("/static/"+endpoint)(globals()[endpoint+"_static_global"])

#find all files in os.getcwd() app/api
for i in os.listdir(os.getcwd()+"/app/services"):
    #find all files that end with _services.py
    if i.endswith("_services.py"):
        #list all functions in the file that end with _run
        actions_ref=""
        with open("app/services/"+i) as f:
            actions_ref=f.read()
        for j in re.findall("def (.*):",actions_ref):
            if("_run" in j):
                expose(j.split("_run")[0],i.split("_services")[0])

"""def remap(path, new_path):
    path = "app/"+path if "/code" in os.getcwd() else path
    @app.get("/"+new_path, response_class=HTMLResponse)
    async def serve_page():
        with open(path) as f:
            lines = f.readlines()
        return ''.join(lines)"""