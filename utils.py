# utils.py

import re
from datetime import datetime


def extract_ip(line):
    """ intenta encontrar una ip"""
    
    match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',line)
    if match:
        return match.group(0)
    else:
        return None
    
def extract_user(line):
    """ intenta encontrar un usuario"""
    
    pass

def classify_event(line):
    """ intenta clasificar el evento del log"""
    
    pass

def parse_line(line):
    """ intenta devolver un diccionario ya armado"""
    
    pass
