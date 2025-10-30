# read_logs.py

from utils import parse_line

def read_log_file(log_path):
    """ Lee un archivo de log y muestra el contenido del mismo en la consola"""
    try:
        
        with open(log_path, 'r', encoding="utf-8") as f:
            count = 0
            for line in f:
                line = line.strip()
                if not line:
                     continue
                 
                 
            data = parse_line(line)
            print(f"{data['event']:<16} | {data['user'] or '-':<10} | {data['ip'] or '-':<15} | {data['raw']}")
            count += 1
        
        print(f"\nTotal de lineas procesadas: {count}")         
        
    except FileNotFoundError:
        print(f"Error: El archivo {log_path} no se encontro")
    
if __name__ == "__main__":
    log_path = "logs/sample.log"
    read_log_file(log_path)
    
    