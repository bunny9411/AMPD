from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Word, db
import urllib.parse

main = Blueprint('main', __name__)

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

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.username)

@main.route('/add_practice_word', methods=['POST'])
@login_required
def add_practice_word():
    word = request.form.get('word', '').strip()
    
    if not word:
        flash('Please enter a word.', 'error')
        return redirect(url_for('main.practice'))
    
    # Check if word already exists
    existing_word = Word.query.filter_by(word=word.lower()).first()
    if existing_word:
        flash('This word already exists in the practice list.', 'info')
        return redirect(url_for('main.practice'))
    
    # Generate audio URL
    audio_url = generate_audio_url(word)
    
    # Create new word
    new_word = Word(
        word=word.lower(),
        audio_url=audio_url,
        added_by=current_user.id,
        is_active=True
    )
    
    try:
        db.session.add(new_word)
        db.session.commit()
        flash(f'Word "{word}" has been added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while adding the word.', 'error')
    
    return redirect(url_for('main.practice'))

@main.route('/practice')
@login_required
def practice():
    words = Word.query.filter_by(is_active=True).order_by(Word.created_at.desc()).all()
    return render_template('main/practice.html', 
                         name=current_user.username,
                         words=words) 