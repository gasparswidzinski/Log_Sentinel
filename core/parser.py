# lo que hace utils.py

import re
from datetime import datetime

class LogParser:
    
    def __init__(self,):
        pass
    
    def extract_ip(self,line):
        """ intenta encontrar una ip"""
        
        match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',line)
        if match:
            return match.group(0)
        else:
            return None
    
    def extract_user(self,line):
        """intenta encontrar un usuario"""
        
        """caso 1 ---> usuario invalido, regex: r"invalid user (\w+)" """
        m = re.search(r"invalid user (\w+)",line)
        if m:
            return m.group(1)
        
        """caso 2 ---> for root, regex: r"for (\w+)" """
        m = re.search(r"for (\w+)",line)
        if m:
            return m.group(1)
        
        """caso 3 ---> sudo: username, regex: r"sudo:\s+(\w+)" """
        m = re.search(r"sudo:\s+(\w+)",line)
        if m:
            return m.group(1)
        
        """caso 4 ---> (root), regex: r"\((\w+)\)" """
        m = re.search(r"\((\w+)\)",line)    
        if m:
            return m.group(1)
