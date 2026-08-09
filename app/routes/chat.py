from flask import Blueprint, request, jsonify, current_app
from app.database import db, Document, ChatSession, ChatMessage
from app.services import generate_chat_response
import json

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint for students to ask questions about a specific document.
    """
    data = request.get_json()
    if not data or 'query' not in data or 'document_id' not in data:
        return jsonify({'error': 'Missing query or document_id'}), 400

    query = data['query']
    doc_id = data['document_id']
    session_id = data.get('session_id')
    user_id = data.get('user_id', 1)

    doc = Document.query.get(doc_id)
    if not doc:
        return jsonify({'error': 'Document not found'}), 404

    context = doc.analysis_result
    if context:
        try:
            context = json.loads(context)
        except Exception:
            pass
    else:
        context = doc.raw_text

    chat_history = []
    if not session_id:
        new_session = ChatSession(user_id=user_id, title=f"Chat about Doc {doc_id}")
        db.session.add(new_session)
        db.session.commit()
        session_id = new_session.id
    else:
        messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.timestamp.asc()).all()
        chat_history = [{'sender_type': msg.sender_type, 'content': msg.content} for msg in messages]

    # Save User Query
    user_msg = ChatMessage(session_id=session_id, sender_type='User', content=query)
    db.session.add(user_msg)
    db.session.commit()

    # Generate AI Response
    ai_response_text = generate_chat_response(query, context, chat_history)

    # Save AI Response
    ai_msg = ChatMessage(session_id=session_id, sender_type='AI', content=ai_response_text)
    db.session.add(ai_msg)
    db.session.commit()

    return jsonify({
        'session_id': session_id,
        'response': ai_response_text
    }), 200
