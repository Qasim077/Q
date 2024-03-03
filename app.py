from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired
from PyPDF2 import PdfReader
from openai import OpenAI
import os

app = Flask(__name__)
app.secret_key = "MUD"

UPLOAD_FOLDER = 'uploads'
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

class SecondUploadFileForm(FlaskForm):
    second_file = FileField("Second File", validators=[InputRequired()])
    submit = SubmitField("Upload Second File")


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def extract_text_from_pdf(pdf_file):
    text = ''
    with open(pdf_file, 'rb') as file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
    return text


OPENAI_API_KEY = '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'

client = OpenAI(api_key=OPENAI_API_KEY)

def teach(content):

    user_prompt = content
    system_prompt = 'You are the lesson planner. You will provide in detail responses for each bullet point and answer the points as if you were a student. leave a line between each bullet point in the specification and on only use letters and symbols to make it easier to format'

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    )
    material_t = completion.choices[0].message.content
    materials = material_t.split("\n")
    with open("flashcards.txt", "w") as f:
        f.write(materials[0])

    return materials

def question_planner(content):

    user_prompt = content
    system_prompt = 'You are the lesson planner. You need to ask ten questions based on the subject material'

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    )
    questions = completion.choices[0].message.content
    question_list = questions.split("\n")

    return question_list
 
def activity_planner(content):

    user_prompt = content
    system_prompt = 'You are the lesson planner. You need to devise an activity for the students such as an experiment or presentation'

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    )
    activity_info = completion.choices[0].message.content
    activities = activity_info.split("\n")

    return activities


@app.route('/', methods=['GET',"POST"])
@app.route('/home', methods=['GET',"POST"])
def home():
    form = UploadFileForm()
    explanation=''
    activity=''
    questions=''
    if form.validate_on_submit():
        file = form.file.data # First grab the file
        file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))
        file.save(file_path) # Then save the file
        content = extract_text_from_pdf(file_path)

        

        explanation = teach(content)
        questions = question_planner(content)
        activity = activity_planner(content)

    return render_template('index.html', form=form, response=explanation, questions=questions, activity=activity)

if __name__ == '__main__':
    app.run(debug=True)