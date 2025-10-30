# read_logs.py

from utils import parse_line
from collections import Counter

def read_log_file(log_path):
    """ Lee un archivo de log y muestra el contenido del mismo en la consola"""
    count = Counter()
    try:
        
        with open(log_path, 'r', encoding="utf-8") as f:
            
            for line in f:
                line = line.strip()
                if not line:
                     continue
                 
                 
            
                data = parse_line(line)
                event = data['event']
                count[event] += 1
                print(f"{data['event']:<16} | {data['user'] or '-':<10} | {data['ip'] or '-':<15} | {data['raw_line']} | {data['time']} | {data.get('processed_at', '')}")
            
        print("\nResumen de eventos:")  
        for evt, qtv in count.items():
            print(f"{evt:<16} : {qtv}")         
        
    except FileNotFoundError:
        print(f"Error: El archivo {log_path} no se encontro")
    