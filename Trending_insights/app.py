from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load the trained model
def train_model(dataset_path):
    df = pd.read_csv(dataset_path)
    df.set_index("Role", inplace=True)
    return df

def fetch_job_details(model, role):
    """Fetch job details and generate LinkedIn URL."""
    if role not in model.index:
        return None, f"Role '{role}' not found in the dataset."

    job_details = model.loc[role].to_dict()
    linkedin_url = f"https://www.linkedin.com/jobs/search/?keywords={role.replace(' ', '%20')}&location=India"
    job_details["LinkedIn URL"] = linkedin_url
    return job_details, None

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    name = request.form.get('name')
    role = request.form.get('role')

    # Load the trained model (assuming it's in the same directory)
    model = train_model('trained_model.csv')

    # Fetch job details
    job_info, error = fetch_job_details(model, role)

    return render_template('result.html', name=name, role=role, job_info=job_info, error=error)

if __name__ == '__main__':
    app.run(debug=True,port=8083)
