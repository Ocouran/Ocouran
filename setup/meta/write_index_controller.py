#!/usr/bin/env python3

def make():
    
    import os, csv
    import re
    
    namespace = 'namespace.txt'
    variable = '{contr}'
    template = './templates/index_controller_template.py'
    depose_dir = '../../run/core/controllers/'
    #extension = '.py'
    filename = 'index.py'
    
    with open((depose_dir+filename),'w') as c:   #create a new __init__.py file
        with open(template, 'r') as t:                                     #read the template file
            with open(namespace, 'r') as f:
                rows = csv.reader(f)
                lines_to_read = csv.reader(t)
                for line_read in lines_to_read:
                    if ','.join(line_read).find(variable) > 0:                                      #check if you need to programatically replace a variable 
                        rows = list(rows)
                        for row in rows:
                            c.write(','.join(line_read).replace("{contr}",''.join(row)))        #replace variable
                            c.write('\n')                                                                              #add carriage return
                    else:
                        c.write(','.join(line_read))
                        c.write('\n')                                                           #add carriage return
    return 'Index Generated, called index.py'        

                    














