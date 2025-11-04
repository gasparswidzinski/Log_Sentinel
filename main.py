# main.py


from core.parser import LogParser
from core.analyzer import LogAnalyzer
from core.reporter import LogReporter

def main():
    
    print("ola")
    log_path = "logs/sample.log"
    parser = LogParser()
    analyzer = LogAnalyzer(parser)   
    reporter = LogReporter()
    
    
    try:
        df = analyzer.read_log_file(log_path)
        print(f"se procesaron {len(df)} lineas ")
        analyzer.summarize(df)
        
        fuera = analyzer.detect_offhour(df)
        print("\nEventos fuera de horario laboral:")
        reporter.show_offhours(fuera)
        reporter.save_report(fuera)
    except Exception as e:
        print(f"Error durante el procesamiento: {e}")
     
            
if __name__ == "__main__":
    main()
