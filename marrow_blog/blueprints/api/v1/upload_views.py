import os
import uuid

from flask import jsonify, request
from flask_login import login_required
from werkzeug.utils import secure_filename

from marrow_blog.blueprints.api.v1 import V1FlaskView


class UploadView(V1FlaskView):
    route_base = "/upload"
    trailing_slash = False

    @login_required
    def post(self):
        """Upload a file."""
        print("In image upload endpoint...")
        if "image" not in request.files:
            return jsonify({"error": "No image provided"}), 400

        file = request.files["image"]
        if file.filename == "":
            return jsonify({"error": "No image selected"}), 400

        if file and self._allowed_file(file.filename):
            # Create unique filename
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"

            # Save to the static folder
            upload_path = os.path.join("/app/data/", "uploads")
            os.makedirs(upload_path, exist_ok=True)
            file_path = os.path.join(upload_path, unique_filename)
            file.save(file_path)

            # Return the path for markdown insertion
            return jsonify(
                {
                    "filename": unique_filename,
                    "path": f"/uploads/{unique_filename}",
                }
            ), 200

        return jsonify({"error": "Invalid file type"}), 400

    def _allowed_file(self, filename):
        """Check if the file extension is allowed."""
        ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
        return (
            "." in filename
            and filename.lower().split(".")[-1] in ALLOWED_EXTENSIONS
        )
