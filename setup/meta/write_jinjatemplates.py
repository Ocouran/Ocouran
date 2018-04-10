#!/usr/bin/env python3

def make():
    
    import os, csv
    import re
    
    namespace = 'namespace.txt'
    variable = '{contr}'
    template = './templates/jinja_template.html'
    depose_dir = '../../run/core/templates/'
    extension = '.html'
    
    with open(namespace, 'r') as f:
        rows = csv.reader(f)
        for row in rows:
            with open(template, 'r') as t:                                     #read the template file
                with open((depose_dir+variable+extension).format(contr=row[0]),'w') as c:   #create a new controller file
                    lines_to_read = csv.reader(t)
                    for line_read in lines_to_read:                                                 #read template file
                        if variable in ''.join(line_read):                                          #check if you need to programatically replace a variable 
                            c.write(','.join(line_read).replace("{contr}",''.join(row)))             #replace variable
                        else:
                            c.write(','.join(line_read))
                        c.write('\n')                                                           #add carriage return
                        
    return 'Jinja Templates Generated, held in '+depose_dir













