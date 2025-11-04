# main.py

import json
from core.parser import LogParser
from core.analyzer import LogAnalyzer
from core.reporter import LogReporter

def main():
    
    with open("rules.json",'r', encoding='utf-8') as f:
        rules = json.load(f)
    
    log_path = "logs/sample.log"
    parser = LogParser()
    analyzer = LogAnalyzer(parser, rules = rules)   
    reporter = LogReporter()
    
    
    try:
        df = analyzer.read_log_file(log_path)
        print(f"se procesaron {len(df)} lineas ")
        analyzer.summarize(df)
        
        fuera = analyzer.detect_offhour(df)
        brute = analyzer.detect_bruteforce(df)
        print("\nEventos fuera de horario laboral:")
        reporter.show_offhours(fuera)
        reporter.show_offhours(brute)
        reporter.save_report(df, "reports/full_log_report.csv")
        reporter.save_report(fuera, "alerts/offhours_report.csv")
        reporter.save_report(brute, "alerts/bruteforce_report.csv")
    except Exception as e:
        print(f"Error durante el procesamiento: {e}")
     
            
if __name__ == "__main__":
    main()
