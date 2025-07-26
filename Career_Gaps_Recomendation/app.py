from flask import Flask, render_template, request, make_response
from xhtml2pdf import pisa
import io
import json

app = Flask(__name__)

# Load skills from the job-skills dataset
def load_skills_data(file_path):
    skills_data = {}
    with open(file_path, 'r') as file:
        parsed_data = json.load(file)
        for entry in parsed_data:
            for role, skills in entry.items():
                skills_data[role] = [skill.strip() for skill in skills[0].split(', ')]
    return skills_data

def load_all_skills(file_path):
    with open(file_path, 'r') as file:
        return [skill.strip() for skill in file.readlines()]

# Load datasets
skills_data = load_skills_data('datasets/job-skills.txt')
all_skills = load_all_skills('datasets/all_skills.txt')

def create_pdf(pdf_data):
    """Generate a PDF from HTML content."""
    pdf_file = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.BytesIO(pdf_data.encode('utf-8')), dest=pdf_file)
    if pisa_status.err:
        return None
    pdf_file.seek(0)
    return pdf_file

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        job_role = request.form['job_role']
        user_skills = set(request.form.getlist('skills'))

        if job_role not in skills_data:
            return f"Sorry, we don't have information for the job role '{job_role}'. Please choose another."

        required_skills = set(skills_data[job_role])
        missing_skills = required_skills - user_skills

        # Calculate percentage of missing skills
        total_skills = len(required_skills)
        missing_percentage = (len(missing_skills) / total_skills) * 100 if total_skills > 0 else 0

        # Determine feedback message
        if missing_percentage > 80:
            feedback = "You need to work hard on these skills to get that career path."
        else:
            feedback = "You are almost fit for this job, but still work on these skills."

        # Check if the user wants to export the PDF
        if 'export_pdf' in request.form:
            pdf_data = render_template(
                'pdf_template.html',
                job_role=job_role,
                user_skills=user_skills,
                required_skills=required_skills,
                missing_skills=missing_skills
            )
            pdf_file = create_pdf(pdf_data)
            if pdf_file:
                response = make_response(pdf_file.read())
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = f'attachment; filename="{job_role}_skills_report.pdf"'
                return response
            return "Failed to generate PDF"

        return render_template(
            'result.html',
            job_role=job_role,
            user_skills=user_skills,
            missing_skills=missing_skills,
            feedback=feedback
        )

    return render_template('index.html', all_skills=all_skills, job_roles=list(skills_data.keys()))

if __name__ == '__main__':
    app.run(debug=True, port=8081)
