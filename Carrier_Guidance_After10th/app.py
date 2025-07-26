from flask import Flask, render_template, request, redirect, url_for, session, send_file
import io
import pandas as pd
from xhtml2pdf import pisa

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Load dataset
df = pd.read_csv("Career_Guidance_Dataset.csv")

# Extract unique values for form
unique_values = {col: sorted(df[col].dropna().unique()) for col in df.columns[:-5]}

def calculate_similarity(row, user_input):
    score = 0
    for col in user_input:
        if col in df.columns:
            if isinstance(user_input[col], str):
                if str(row[col]).lower() == str(user_input[col]).lower():
                    score += 1
            else:
                score -= abs(row[col] - user_input[col])
    return score

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Collect user inputs
        user_input = {col: request.form.get(col) for col in unique_values.keys()}
        puc_or_diploma = request.form.get('puc_or_diploma', '')
        city = request.form.get('city', 'Mysore')  # Get city input or default to Mysore

        # Handle numerical columns
        numerical_columns = df.select_dtypes(include=['int64', 'float64']).columns
        for col in numerical_columns:
            if col in user_input and user_input[col] is not None and user_input[col] != '':
                user_input[col] = float(user_input[col])

        # Calculate similarity
        df['Similarity_Score'] = df.apply(lambda row: calculate_similarity(row, user_input), axis=1)
        closest_match = df.loc[df['Similarity_Score'].idxmax()]

        # Store recommendations in session (remove Distance_To_College here)
        session['recommendations'] = {
            'Recommended_Path': closest_match['Recommended_Path'],
            'Suitable_Careers': closest_match['Suitable_Careers'],
            'Suggested_Courses': closest_match['Suggested_Courses'],
            'Skills_To_Develop': closest_match['Skills_To_Develop'],
            'Challenges_To_Overcome': closest_match['Challenges_To_Overcome'],
            'PUC_or_Diploma': puc_or_diploma,
            'City': city  # Store city in recommendations
        }
        
        return redirect(url_for('results'))
    
    return render_template('index.html', unique_values=unique_values)

@app.route('/results', methods=['GET'])
def results():
    recommendations = session.get('recommendations', None)
    if recommendations:
        # Generate Google Maps link (without Distance_To_College)
        query_type = recommendations.get('PUC_or_Diploma', '').lower()
        city = recommendations.get('City', 'Mysore')  # Get the city from recommendations

        if query_type:
            # Modify the query to reflect the user's city
            maps_url = f"https://www.google.com/maps/search/{query_type}+colleges+in+{city}"
            recommendations['google_maps_link'] = maps_url

    return render_template('results.html', recommendations=recommendations)

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    recommendations = session.get('recommendations', None)
    user_name = request.form.get('user_name')  # Get the user's name from the form

    if not recommendations or not user_name:
        return redirect(url_for('index'))  # Redirect if no recommendations or name is missing

    # Render the HTML content using the template
    html_content = render_template('recommendation_template.html', recommendations=recommendations, user_name=user_name)

    # Create a BytesIO buffer to save the PDF in memory
    buffer = io.BytesIO()

    # Convert the HTML to PDF using xhtml2pdf
    pisa_status = pisa.CreatePDF(html_content, dest=buffer)
    
    if pisa_status.err:
        return "Error while generating PDF", 500
    
    # Move buffer position to the beginning
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name="career_recommendations.pdf", mimetype="application/pdf")

if __name__ == '__main__':
    app.run(debug=True, port=8080)
