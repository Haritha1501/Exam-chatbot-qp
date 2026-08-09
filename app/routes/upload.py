from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from app.services import extract_text_from_pdf
from app.database import db, Document

upload_bp = Blueprint('upload', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@upload_bp.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    files = request.files.getlist('file')
    
    # If the user does not select a file, the browser submits an empty file
    if not files or files[0].filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    subject = request.form.get('subject', 'Unknown')
    year = request.form.get('year', None)
    
    valid_files = [f for f in files if allowed_file(f.filename)]
    
    if not valid_files:
        return jsonify({'error': 'Allowed file types are pdf'}), 400
        
    try:
        extracted_text = ""
        filenames = []
        
        for file in valid_files:
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            # Save file locally
            file.save(filepath)
            
            # Extract text
            text = extract_text_from_pdf(filepath)
            extracted_text += f"\n--- {filename} ---\n{text}\n"
            filenames.append(filename)
            
            # Clean up temp file after text extraction
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception:
                    pass
            
        combined_filename = ", ".join(filenames)
        
        # Save securely to database using SQLAlchemy
        doc = Document(
            filename=combined_filename,
            subject=subject,
            year=str(year) if year else None,
            raw_text=extracted_text
        )
        db.session.add(doc)
        db.session.commit()
        
        return jsonify({
            'message': f'{len(valid_files)} file(s) successfully uploaded and processed',
            'document_id': doc.id,
            'filename': combined_filename,
            'subject': subject,
            'year': year
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
