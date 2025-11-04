# lo que hace utils.py

import re
from datetime import datetime

class LogParser:
    
    def __init__(self,):
        pass
    
    def extract_ip(self,line):
        """ usa regex IPv4 para devolver la primera IP encontrada o None"""
        
        match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',line)
        if match:
            return match.group(0)
        else:
            return None
    
    def extract_user(self,line):
        """intenta extraer un usuario, en orden, utilizando patrones tipicos:
            "invalid user (\w+)" (usuario invalido, caso 1)
            "for (\w+)"(for root, caso 2)
            "sudo:\s+(\w+)" (sudo: username, caso 3)
            "\((\w+)\)" (CRON, caso 4)
        """
        
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
        
        """caso 4 ---> (CRON), regex: r"\((\w+)\)" """
        m = re.search(r"\((\w+)\)",line)    
        if m:
            return m.group(1)
    
    def classify_event(self,line):
        """intenta clasificar el evento del log
            "Failes password" -> "failed_login"
            "Accepted password" -> "successful_login"
            "sudo:" -> "sudo_command"
            "CRON" -> "cron_job"
            "GET" o "POST" -> "web_request"
            si no encuentra ninguno, devuelve "other"
        """
        
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
        """Caso sylog: arma un string con el año actual y lo parsea con datetime.strptime()
           Caso apache: extrae el timestamp entre corchetes y lo parsea con datetime.strptime()
        """
        
        m = re.search(r'([A-Z][a-z]{2})\s+(\d{1,2})\s+(\d{2}:\d{2}:\d{2})', line)
        if m:
            current_year = datetime.now().year
            ts = f"{current_year} {m.group(1)} {m.group(2)} {m.group(3)}"
            try:
                return datetime.strptime(ts, "%Y %b %d %H:%M:%S")
            except ValueError:
                pass

        m2 = re.search(r'\[(\d{2}/[A-Za-z]{3}/\d{4}:\d{2}:\d{2}:\d{2}) [+\-]\d{4}\]', line)
        if m2:
            try:
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
        