# main.py

from read_logs import read_log_file

def main():
    
    log_path = "logs/sample.log"
    
    try:
        read_log_file(log_path)
    
    except Exception as e:
        print(f"Error al leer el archivo de log: {e}")

if __name__ == "__main__":
    main()
