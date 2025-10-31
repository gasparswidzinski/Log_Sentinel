# main.py

from read_logs import *
from core.parser import LogParser
from core.analyzer import LogAnalyzer
from core.reporter import LogReporter

def main():
    
    log_path = "logs/sample.log"
    parser = LogParser()
    analyzer = LogAnalyzer()   
    reporter = LogReporter()
    
    
    try:
        df = read_log_file(log_path)
        print(f"se procesaron {len(df)} lineas ")
        analyze_logs(df)
        save_report(df)
        print("analisis completado")
    except FileNotFoundError as e:
        print(f"{e}")
    except Exception as e:
        print(f"Error inesperado: {e}")    
    
if __name__ == "__main__":
    main()
