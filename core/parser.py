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
    
    def classify_event(self,line):
        """intenta clasificar el evento del log"""
        
        if "Failed password" in line:
            return "failed_login"
        
        if "Accepted password" in line:
            return "successful_login"
        
        if "sudo:" in line:
            return "sudo_command"
        
        if "CRON" in line:
            return "cron_job"
        
        if "GET" in line or "POST" in line:
            return "web_request"
        
        return "other"

    def extract_timestamp(self, line: str):
        # 1) Syslog clásico: "Oct 29 18:32:45 ..."
        m = re.search(r'([A-Z][a-z]{2})\s+(\d{1,2})\s+(\d{2}:\d{2}:\d{2})', line)
        if m:
            current_year = datetime.now().year
            ts = f"{current_year} {m.group(1)} {m.group(2)} {m.group(3)}"
            try:
                return datetime.strptime(ts, "%Y %b %d %H:%M:%S")
            except ValueError:
                pass

        # 2) Apache/Nginx: "[30/Oct/2025:10:46:14 +0000]"
        m2 = re.search(r'\[(\d{2}/[A-Za-z]{3}/\d{4}:\d{2}:\d{2}:\d{2}) [+\-]\d{4}\]', line)
        if m2:
            try:
                # si querés conservar tz, usá %z; si no, parseá sin tz
                return datetime.strptime(m2.group(1), "%d/%b/%Y:%H:%M:%S")
            except ValueError:
                pass

        return None

    def parse_line(self,line):
        """intenta devolver un diccionario con los datos parseados de la linea"""
        
        return {
            "raw_line":line,
            "ip":self.extract_ip(line),
            "user":self.extract_user(line),
            "event": self.classify_event(line),
            "timestamp": self.extract_timestamp(line),    
        }
        