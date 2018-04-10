import os
import csv

def make():
    ''' 
    This creates the controllers in /controllers and the Html files in /templates
    '''
    with open('namespace.txt', 'r') as f:
        rows = csv.reader(f)
        for row in rows:
            os.system('touch ../../run/core/controllers/{stem}.py'.format(stem=row[0]))
            os.system('touch ../../run/core/templates/{stem}.html'.format(stem=row[0]))
    return 'Files Created'
    
