###############################################################
#                                                             #
#                 LSD - LARGE SCALE DEVELOPMENT               #              
#                    A Flask Project Factory                  #
#                                                             #
###############################################################

Running:    python3 wsgi.py launches the __init__.py in core
            which runs a Flask app with a complete Namespace 
            based on the Names defined in setup/Namespace.txt


Setup:      1. rm -r /run/core
            2. in setup/meta, define your namespace in 
               Namespace.txt
            3. run: python3 make_lsd.py
            4. run: python3 /run/wsgi.py

Useage:     1. Going to localhost will yield a list of your
               defined namespace
            2. localhost/name is the first defined route
            3. localhost/name/anystring is the second defined route
        
This script is easily customizable to quickly deploy a large site with 
many products.  The controllers and html pages created by the factory scripts
are in setup/meta, the script make_lsd calls them one by one.

Customize   1. edit your templates in setup/meta/templates
            2. run make_lsd.py again

