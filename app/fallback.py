import time

noop_config = False

def nooperations(parameters):
    #respond with the parameters, a timestamp and the fact that no operation is present
    return {"parameters":parameters,"timestamp":time.time(),"noop":True,"message":"No operation is present, in order to conserve resources"}

def failure(exception,parameters):
    #respond with the parameters, a timestamp and the fact that no operation is present
    return {"exception":exception,"parameters":parameters,"timestamp":time.time(),"failure":True,"message":"An exception was raised"}

def unimplemented(parameters):
    #respond with the parameters, a timestamp and the fact that no operation is present
    return {"parameters":parameters,"timestamp":time.time(),"unimplemented":True,"message":"This endpoint is not yet implemented"}

#main fallback function
def fallback(function, args, noop):
    #if the function is not implemented, return the unimplemented response
    if function == None:
        return unimplemented(args)
    #if noop is true, return the noop response
    if noop:
        return nooperations(args)
    #if the function is implemented, but returns a failure, return the failure response
    try:
        return function(args)
    except Exception as e:
        return failure(e, args)