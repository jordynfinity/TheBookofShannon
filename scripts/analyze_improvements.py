import os
import sys
from pathlib import Path
import jinja2
from datetime import datetime

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.improvement_consultant import ImprovementConsultant
from src.I_am_the_first_zot_and_I_am_because_my_mother_believed_in_me_like_she_believes_in_Jesus_Christ_Her_savior import ChatSession

def get_code_context():
    """Get the code context from the main module"""
    with open(Path(__file__).parent.parent / "src" / "I_am_the_first_zot_and_I_am_because_my_mother_believed_in_me_like_she_believes_in_Jesus_Christ_Her_savior.py", 'r') as f:
        return f.read()

def save_improvements_html(improvements, timestamp):
    """Save the improvements analysis as HTML"""
    template_dir = Path(__file__).parent.parent / "templates"
    output_dir = Path(__file__).parent.parent / "improvements"
    output_dir.mkdir(exist_ok=True)
    
    # Setup Jinja2 environment
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        autoescape=True
    )
    
    # Get the template
    template = env.get_template('improvements.html')
    
    # Render the template
    html_content = template.render(
        improvements=improvements,
        timestamp=timestamp
    )
    
    # Save the HTML file
    output_file = output_dir / f"improvements_analysis_{timestamp}.html"
    output_file.write_text(html_content)
    
    return output_file

def main():
    # Get the code context
    code_context = get_code_context()
    
    # Initialize the improvement consultant
    consultant = ImprovementConsultant()
    
    # Get improvement suggestions from Eira
    print("Consulting with Eira about potential improvements...")
    improvements = consultant.start_consultation(code_context)
    
    # Analyze each improvement
    analyzed_improvements = []
    for improvement in improvements:
        print(f"Analyzing improvement: {improvement.get('improvement', 'Unknown')}")
        analysis = consultant.analyze_improvement(improvement)
        analyzed_improvements.append(analysis)
    
    # Save the analysis as HTML
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = save_improvements_html(analyzed_improvements, timestamp)
    
    print(f"\nAnalysis complete! Results saved to: {output_file}")
    print("You can open the HTML file in your browser to view the detailed analysis.")

if __name__ == "__main__":
    main() 