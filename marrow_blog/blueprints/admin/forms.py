from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired, Length, Optional
from marrow_blog.blueprints.admin.validations import allowed_file


class UploadForm(FlaskForm):
    doc_file = FileField('Upload a Text or Docx File', [FileRequired(), allowed_file])
    submit = SubmitField('Upload a Document')

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    token = StringField("MFA Token", validators=[Optional(), Length(min=6, max=6)])
    submit = SubmitField("Login")
