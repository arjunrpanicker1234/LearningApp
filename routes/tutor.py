from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Skill, Resource, User
from services.pdf_service import PDFService
import os
from config import Config

tutor_bp = Blueprint('tutor', __name__)
pdf_service = PDFService()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@tutor_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_tutor:
        return redirect(url_for('user.dashboard'))
    
    skills = Skill.query.all()
    resources = Resource.query.filter_by(uploaded_by=current_user.id).all()
    
    return render_template('tutor/dashboard.html',
                          skills=skills,
                          resources=resources)

@tutor_bp.route('/add_skill', methods=['GET', 'POST'])
@login_required
def add_skill():
    if not current_user.is_tutor:
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if Skill.query.filter_by(name=name).first():
            flash('Skill already exists')
            return redirect(url_for('tutor.add_skill'))
        
        new_skill = Skill(name=name, description=description)
        db.session.add(new_skill)
        db.session.commit()
        
        flash('Skill added successfully')
        return redirect(url_for('tutor.dashboard'))
    
    return render_template('tutor/add_skill.html')

@tutor_bp.route('/upload_resource', methods=['GET', 'POST'])
@login_required
def upload_resource():
    if not current_user.is_tutor:
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        skill_id = request.form.get('skill_id', type=int)
        title = request.form.get('title')
        content_type = request.form.get('content_type')
        proficiency_level = request.form.get('proficiency_level', type=int)
        
        if not skill_id or not title or not content_type or not proficiency_level:
            flash('All fields are required')
            return redirect(url_for('tutor.upload_resource'))
        
        new_resource = Resource(
            skill_id=skill_id,
            title=title,
            content_type=content_type,
            proficiency_level=proficiency_level,
            uploaded_by=current_user.id
        )
        
        if content_type == 'text':
            new_resource.content = request.form.get('content')
        elif content_type == 'pdf':
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{int(datetime.utcnow().timestamp())}_{file.filename}")
                file_path = pdf_service.save_pdf(file, filename)
                new_resource.file_path = file_path
                
                # Extract text for searching/indexing
                text_content = pdf_service.extract_text(file_path)
                new_resource.content = text_content[:1000]  # Store a preview
            else:
                flash('File type not allowed')
                return redirect(request.url)
        
        db.session.add(new_resource)
        db.session.commit()
        
        flash('Resource uploaded successfully')
        return redirect(url_for('tutor.dashboard'))
    
    skills = Skill.query.all()
    return render_template('tutor/upload_resource.html', skills=skills)

@tutor_bp.route('/view_resource/<int:resource_id>')
@login_required
def view_resource(resource_id):
    if not current_user.is_tutor:
        return redirect(url_for('user.dashboard'))
    
    resource = Resource.query.get_or_404(resource_id)
    
    return render_template('tutor/view_resource.html', resource=resource)