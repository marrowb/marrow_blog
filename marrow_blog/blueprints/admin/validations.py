from wtforms.validators import ValidationError
from flask import current_app


def allowed_file(form, field):
    extensions = current_app.config["DOC_UPLOAD_ALLOWED_EXTENSIONS"]
    filename = field.data.filename
    if not (
        filename
        and "." in filename
        and filename.rsplit(".", 1)[1].lower() in extensions
    ):
        raise ValidationError(
            f"File must be one of the following file extensions: {str(extensions)}"
        )
