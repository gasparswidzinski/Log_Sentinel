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
    
    """caso 1 ---> usuario invalido, regex: r"invalid user (\w+)" """
    m = re.search(r"invalid user (\w+)")
    if m:
        return m.group(1)
    
    
    """caso 2 ---> for root, regex: r"for (\w+)" """
    m = re.search(r"for (\w+)")
    if m:
        return m.group(1)
    
    """caso 3 ---> sudo: username, regex: r"sudo:\s+(\w+)" """
    m = re.search(r"sudo:\s+(\w+)")
    if m:
        return m.group(1)
    
    """caso 4 ---> (root), regex: r"\((\w+)\)" """
    m = re.search(r"\((\w+)\)")
    if m:
        return m.group(1)
    
    
def classify_event(line):
    """ intenta clasificar el evento del log"""
    
    if "Failed password" in line:
        return "failed_login"
    
    if "Accepted password" in line:
        return "successful_login"
    
    if "sudo" in line:
        return "sudo_command"
    
    if "cron" in line:
        return "cron_job"  
    
    if "GET" in line or "POST" in line:
        return "web_request"
    
    return "other"

def parse_line(line):
    """ intenta devolver un diccionario ya armado"""
    
    return {
        "raw_line": line,
        "ip": extract_ip(line),
        "user": extract_user(line),
        "event_type": classify_event(line),
        "time": datetime.now()
    }
    
