from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, session
from flask_login import login_required, current_user
from models import db, Skill, Assessment, Resource, ChatSession, ChatMessage
from services.llm_service import LLMService

user_bp = Blueprint('user', __name__)
llm_service = LLMService()

@user_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_tutor:
        return redirect(url_for('tutor.dashboard'))
    
    skills = Skill.query.all()
    user_assessments = Assessment.query.filter_by(user_id=current_user.id).all()
    
    # Map skills to assessment results
    assessed_skills = {assessment.skill_id: assessment.proficiency_level for assessment in user_assessments}
    
    return render_template('user/dashboard.html', 
                          skills=skills, 
                          assessed_skills=assessed_skills)

@user_bp.route('/start_assessment/<int:skill_id>')
@login_required
def start_assessment(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    
    # Generate questions for the assessment
    questions = llm_service.generate_questions(skill.name, num_questions=5)
    
    # Store questions in session
    session['assessment_questions'] = questions
    session['current_skill_id'] = skill_id
    
    return render_template('user/assessment.html', 
                          skill=skill, 
                          questions=questions)

@user_bp.route('/submit_assessment', methods=['POST'])
@login_required
def submit_assessment():
    if 'assessment_questions' not in session:
        flash('Assessment session expired')
        return redirect(url_for('user.dashboard'))
    
    questions = session['assessment_questions']
    skill_id = session['current_skill_id']
    
    # Collect user answers
    user_answers = []
    for i, q in enumerate(questions):
        question_id = f"q{i}"
        user_answer = request.form.get(question_id)
        
        user_answers.append({
            'question': q['question_text'],
            'user_answer': user_answer,
            'correct_answer': q['options'][q['correct_answer']]
        })
    
    # Assess proficiency
    assessment_result = llm_service.assess_proficiency(
        Skill.query.get(skill_id).name, 
        user_answers
    )
    
    # Save assessment result
    new_assessment = Assessment(
        user_id=current_user.id,
        skill_id=skill_id,
        proficiency_level=assessment_result['score']
    )
    db.session.add(new_assessment)
    db.session.commit()
    
    # Clean up session
    session.pop('assessment_questions', None)
    session.pop('current_skill_id', None)
    
    return redirect(url_for('user.view_resources', 
                           skill_id=skill_id,
                           proficiency=assessment_result['score']))

@user_bp.route('/resources/<int:skill_id>')
@login_required
def view_resources(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    proficiency = request.args.get('proficiency', type=int)
    
    if not proficiency:
        # Try to find most recent assessment
        assessment = Assessment.query.filter_by(
            user_id=current_user.id,
            skill_id=skill_id
        ).order_by(Assessment.completed_at.desc()).first()
        
        if assessment:
            proficiency = assessment.proficiency_level
        else:
            proficiency = 1
    
    # Get available resources for this skill
    resources = Resource.query.filter_by(skill_id=skill_id).all()
    
    # Get recommendations
    recommended_resources = llm_service.recommend_resources(
        skill.name, 
        proficiency, 
        resources
    )
    
    # Get resource objects
    if isinstance(recommended_resources, list) and recommended_resources:
        recommendations = [Resource.query.get(r_id) for r_id in recommended_resources if Resource.query.get(r_id)]
    else:
        # Fallback to level-based filtering
        recommendations = [r for r in resources if abs(r.proficiency_level - proficiency) <= 1]
    
    return render_template('user/resources.html',
                          skill=skill,
                          proficiency=proficiency,
                          resources=recommendations)

@user_bp.route('/chat/<int:skill_id>')
@login_required
def start_chat(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    
    # Find or create chat session
    chat_session = ChatSession.query.filter_by(
        user_id=current_user.id,
        skill_id=skill_id
    ).order_by(ChatSession.created_at.desc()).first()
    
    if not chat_session:
        chat_session = ChatSession(
            user_id=current_user.id,
            skill_id=skill_id
        )
        db.session.add(chat_session)
        db.session.commit()
    
    messages = ChatMessage.query.filter_by(session_id=chat_session.id).order_by(ChatMessage.timestamp).all()
    
    return render_template('user/chat.html',
                          skill=skill,
                          session=chat_session,
                          messages=messages)

@user_bp.route('/send_message', methods=['POST'])
@login_required
def send_message():
    session_id = request.form.get('session_id', type=int)
    message_content = request.form.get('message')
    
    if not session_id or not message_content:
        return jsonify({'error': 'Missing data'}), 400
    
    # Verify session belongs to user
    chat_session = ChatSession.query.get_or_404(session_id)
    if chat_session.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Save user message
    user_msg = ChatMessage(
        session_id=session_id,
        is_user=True,
        content=message_content
    )
    db.session.add(user_msg)
    db.session.commit()
    
    # Get relevant resources for context
    skill = Skill.query.get(chat_session.skill_id)
    resources = Resource.query.filter_by(skill_id=chat_session.skill_id).limit(3).all()
    context = "\n".join([r.content for r in resources if r.content])
    
    # Generate AI response
    ai_response = llm_service.answer_question(skill.name, message_content, context)
    
    # Save AI message
    ai_msg = ChatMessage(
        session_id=session_id,
        is_user=False,
        content=ai_response
    )
    db.session.add(ai_msg)
    db.session.commit()
    
    return jsonify({
        'user_message': {
            'id': user_msg.id,
            'content': user_msg.content,
            'timestamp': user_msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        },
        'ai_message': {
            'id': ai_msg.id,
            'content': ai_msg.content,
            'timestamp': ai_msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
    })