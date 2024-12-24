from datetime import datetime
import json
import csv
from pathlib import Path
import plotly.graph_objects as go
from jinja2 import Template

class ReportGenerator:
    def __init__(self, test_results, output_dir="reports"):
        self.test_results = test_results
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def generate_html_report(self):
        """Generate detailed HTML report with charts"""
        # Calculate statistics
        stats = self._calculate_statistics()
        
        # Create charts
        success_chart = self._create_pie_chart(
            stats['pass_rate'], 
            "Test Pass Rate"
        )
        
        duration_chart = self._create_bar_chart(
            stats['duration_by_module'],
            "Test Duration by Module"
        )
        
        # Generate HTML using template
        template = self._load_template()
        html_content = template.render(
            stats=stats,
            success_chart=success_chart,
            duration_chart=duration_chart,
            timestamp=self.timestamp
        )
        
        # Save report
        report_path = self.output_dir / f"report_{self.timestamp}.html"
        report_path.write_text(html_content)
        return report_path

    def export_results(self, format_type="json"):
        """Export results in specified format"""
        if format_type == "json":
            return self._export_json()
        elif format_type == "csv":
            return self._export_csv()
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def _calculate_statistics(self):
        """Calculate test statistics"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test['status'] == 'passed')
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'pass_rate': (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            'duration_by_module': self._group_by_module(),
            'error_summary': self._summarize_errors()
        }

    # ... (additional helper methods) 