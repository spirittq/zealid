from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.html5 import DateField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired


class DataForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    date = DateField('Date of Birth', validators=[DataRequired()])
    image = FileField('Image File', validators=[FileRequired(), FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Submit')

# [validators.regexp(u'^[^/\\\\]\.jpg$')]
