from flask import Flask, render_template, request, flash, redirect
from forms import DataForm
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import requests
import json
import base64
import hashlib
from methods import mrz_extract, compare
from datetime import datetime

ALLOWED_EXTENSIONS = {'png', 'jpg'}

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
csrf = CSRFProtect(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class PersonData(db.Model):
    __tablename__ = "persondata"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    surname = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date(), nullable=False)
    image = db.Column(db.String(20), nullable=False)

    def __init__(self, name, surname, date, image):
        self.name = name
        self.surname = surname
        self.date = date
        self.image = image


@app.route('/', methods=['GET', 'POST'])
def index():
    db.create_all()
    form = DataForm()
    if form.validate_on_submit():

        # Task 1 - take information from form and save in database
        name = form.name.data
        surname = form.surname.data
        date = form.date.data
        f = form.image.data
        filename = secure_filename(f.filename)
        directory = os.path.join(os.path.dirname(app.instance_path), 'static')
        f.save(os.path.join(directory, 'pass_photo', filename))
        provided_info = {
            'name': name,
            'surname': surname,
            'date': date,
            'filename': filename
        }
        entry = PersonData(provided_info['name'], provided_info['surname'], provided_info['date'],
                           provided_info['filename'])
        db.session.add(entry)
        db.session.commit()

        # Task 2 - make an API call in required format, gather ocr_texts[0] for further usage
        
        # api_key/api_key.txt is DELETED, as it was given for the task only.
        
        with open("static/api_key/api_key.txt", 'r') as file:
            api_key = file.read()

        API_KEY = api_key

        with open(f"static/pass_photo/{filename}", 'rb') as img_file:
            img_filedata = img_file.read()
            encoded_base64 = base64.b64encode(img_filedata).decode('utf-8')
            hashed = hashlib.sha1(img_filedata).hexdigest()

        headers = {'Content-type': 'application/json', 'x-api-key': API_KEY}
        data = {
            'document': f'{encoded_base64}',
            'digest': f'{hashed}',
            'type': 'lt_pass_rev'
        }

        r = requests.post('https://api.identiway.com/docs/validate', headers=headers, json=data)
        result = json.loads(r.text)
        ocr_texts = result['ocr_texts'][0]

        # Task 3 - use mrz_extract method from methods.py to get relevant values from ocr_texts[0] and store them in dictionary
        try:
            mrz_info = mrz_extract(ocr_texts)
        except:
            mrz_error = 'Please try another document photo'
            return render_template("result.html", mrz_error=mrz_error)

        # Task 4 - use compare method from methods.py to compare results from information provided by hand and gathered from pass photo
        check = {
            'name_check': compare(provided_info['name'], mrz_info['name']),
            'surname_check': compare(provided_info['surname'], mrz_info['surname']),
            'birth_date_check': compare(provided_info['date'].strftime('%Y-%m-%d'), mrz_info['birth_date']),
        }

        # Task 5 - if results are same, check is True, if different - check is False. Results rendered into html page
        return render_template("result.html", provided_info=provided_info, mrz_info=mrz_info, check=check)
    return render_template("index.html", form=form)


if __name__ == "__main__":
    # app.run()
    app.run(debug=True)
