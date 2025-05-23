from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from .models import User, Word, Feedback, db
from datetime import datetime
import urllib.parse

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need to be an admin to access this page.')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def generate_audio_url(word):
    """Generate Google Translate TTS URL for a word"""
    base_url = "https://translate.google.com/translate_tts"
    params = {
        'ie': 'UTF-8',
        'q': word,
        'tl': 'en',
        'client': 'tw-ob'
    }
    return f"{base_url}?{urllib.parse.urlencode(params)}"

@admin.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.all()
    total_users = len(users)
    total_practice_sessions = sum(len(user.pronunciation_scores) for user in users)
    pending_feedbacks = Feedback.query.filter_by(status='pending').count()
    total_words = Word.query.count()
    
    # Calculate average accuracy
    total_accuracy = 0
    users_with_scores = 0
    for user in users:
        if user.pronunciation_scores:
            users_with_scores += 1
            scores = user.pronunciation_scores.values()
            total_accuracy += sum(scores) / len(scores)
    
    avg_accuracy = round(total_accuracy / users_with_scores if users_with_scores > 0 else 0, 2)
    
    return render_template('admin/dashboard.html',
                         users=users,
                         total_users=total_users,
                         total_practice_sessions=total_practice_sessions,
                         avg_accuracy=avg_accuracy,
                         pending_feedbacks=pending_feedbacks,
                         total_words=total_words)

# Word Management Routes
@admin.route('/admin/words')
@login_required
@admin_required
def manage_words():
    words = Word.query.order_by(Word.created_at.desc()).all()
    return render_template('admin/words.html', words=words)

@admin.route('/admin/words/add', methods=['POST'])
@login_required
@admin_required
def add_word():
    word = request.form.get('word')
    audio_url = request.form.get('audio_url')
    
    if not word:
        flash('Word is required.')
        return redirect(url_for('admin.manage_words'))
    
    if not audio_url:
        # Generate audio URL if not provided
        audio_url = generate_audio_url(word)
    
    if Word.query.filter_by(word=word).first():
        flash('This word already exists.')
        return redirect(url_for('admin.manage_words'))
    
    new_word = Word(
        word=word,
        audio_url=audio_url,
        added_by=current_user.id,
        is_active=True
    )
    db.session.add(new_word)
    db.session.commit()
    
    flash(f'Word "{word}" has been added successfully.')
    return redirect(url_for('admin.manage_words'))

@admin.route('/admin/words/<int:word_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_word(word_id):
    word = Word.query.get_or_404(word_id)
    word.is_active = not word.is_active
    db.session.commit()
    
    status = "activated" if word.is_active else "deactivated"
    flash(f'Word "{word.word}" has been {status}.')
    return redirect(url_for('admin.manage_words'))

@admin.route('/admin/words/<int:word_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_word(word_id):
    word = Word.query.get_or_404(word_id)
    db.session.delete(word)
    db.session.commit()
    
    flash(f'Word "{word.word}" has been deleted.')
    return redirect(url_for('admin.manage_words'))

# Feedback Management Routes
@admin.route('/admin/feedback')
@login_required
@admin_required
def manage_feedback():
    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return render_template('admin/feedback.html', feedbacks=feedbacks)

@admin.route('/admin/feedback/<int:feedback_id>/respond', methods=['POST'])
@login_required
@admin_required
def respond_to_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    response = request.form.get('response')
    status = request.form.get('status', 'reviewed')
    
    if response:
        feedback.admin_response = response
        feedback.status = status
        db.session.commit()
        flash('Response has been saved.')
    else:
        flash('Response cannot be empty.')
    
    return redirect(url_for('admin.manage_feedback'))

# Existing user management routes
@admin.route('/admin/user/<int:user_id>')
@login_required
@admin_required
def user_details(user_id):
    user = User.query.get_or_404(user_id)
    user_feedbacks = Feedback.query.filter_by(user_id=user_id).order_by(Feedback.created_at.desc()).all()
    return render_template('admin/user_details.html', user=user, feedbacks=user_feedbacks)

@admin.route('/admin/user/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    if current_user.id == user_id:
        flash('You cannot modify your own admin status.')
        return redirect(url_for('admin.admin_dashboard'))
    
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    
    flash(f'Admin status for {user.username} has been {"granted" if user.is_admin else "revoked"}.')
    return redirect(url_for('admin.admin_dashboard'))

@admin.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if current_user.id == user_id:
        flash('You cannot delete your own account.')
        return redirect(url_for('admin.admin_dashboard'))
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.username} has been deleted.')
    return redirect(url_for('admin.admin_dashboard')) 