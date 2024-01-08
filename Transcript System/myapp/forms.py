from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Email


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class UploadTranscriptForm(FlaskForm):
    student_email = StringField("Student Email", validators=[DataRequired(), Email()])
    transcript_file = FileField("Transcript File", validators=[DataRequired()])
    submit = SubmitField("Upload")
