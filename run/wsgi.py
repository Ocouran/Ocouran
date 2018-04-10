#!/usr/bin/env python3

from core import omnibus
import os

if __name__ == '__main__':
    #For google authentication, don't leave this as is for productions
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    #Local Testing Env
    omnibus.run(host='127.0.0.1',port=8080,debug=True)
    #Local Stagin Env
    #omnibus.run(host='0.0.0.0',port=5000,debug=True)
