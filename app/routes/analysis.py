from flask import Blueprint, jsonify, current_app
from app.database import db, Document
from app.services import analyze_question_paper
import json

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/analyze/<int:doc_id>', methods=['POST'])
def analyze_document(doc_id):
    doc = Document.query.get(doc_id)
    
    if not doc:
        return jsonify({'error': 'Document not found'}), 404
        
    # If already analyzed, return the cached result
    if doc.analysis_result:
        try:
            parsed = json.loads(doc.analysis_result)
        except Exception:
            parsed = doc.analysis_result
        return jsonify({
            'message': 'Retrieved from database',
            'analysis': parsed
        }), 200

    raw_text = doc.raw_text
    
    try:
        # Analyze the extracted text using the Gemini formulation
        analysis_data = analyze_question_paper(raw_text)
        
        if isinstance(analysis_data, dict) and "error" in analysis_data:
            return jsonify(analysis_data), 500
            
        # Save the structured analysis result back to the database as a JSON string
        doc.analysis_result = json.dumps(analysis_data)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
    return jsonify({
        'message': 'Analysis complete',
        'analysis': analysis_data
    }), 200
