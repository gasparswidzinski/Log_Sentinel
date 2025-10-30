# read_logs.py

def read_log_file(log_path):
    
    try:
        
        with open(log_path, 'r', encoding="utf-8") as f:
            count = 0
            for line in f:
                line = line.strip()
                if line:
                    print(line)
                    count += 1
            print(f"\n Total de lineas leidas: {count}")
        
    except FileNotFoundError:
        print(f"Error: El archivo {log_path} no se encontro")
    
if __name__ == "__main__":
    log_path = "logs/sample.log"
    read_log_file(log_path)
    
    