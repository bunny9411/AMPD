from app import create_app, db
from app.models import Word, User

app = create_app()

initial_words = [
    {
        "word": "banana",
        "audio_url": "https://ssl.gstatic.com/dictionary/static/sounds/oxford/banana--_gb_1.mp3"
    },
    {
        "word": "elephant",
        "audio_url": "https://ssl.gstatic.com/dictionary/static/sounds/oxford/elephant--_gb_1.mp3"
    },
    {
        "word": "computer",
        "audio_url": "https://ssl.gstatic.com/dictionary/static/sounds/oxford/computer--_gb_1.mp3"
    },
    {
        "word": "guitar",
        "audio_url": "https://ssl.gstatic.com/dictionary/static/sounds/oxford/guitar--_gb_1.mp3"
    },
    {
        "word": "tomato",
        "audio_url": "https://ssl.gstatic.com/dictionary/static/sounds/oxford/tomato--_gb_1.mp3"
    },
    {
        "word": "window",
        "audio_url": "https://ssl.gstatic.com/dictionary/static/sounds/oxford/window--_gb_1.mp3"
    },
    {
        "word": "mountain",
        "audio_url": "https://ssl.gstatic.com/dictionary/static/sounds/oxford/mountain--_gb_1.mp3"
    },
    {
        "word": "robot",
        "audio_url": "https://ssl.gstatic.com/dictionary/static/sounds/oxford/robot--_gb_1.mp3"
    }
]

with app.app_context():
    # Get admin user
    admin = User.query.filter_by(email='admin@example.com').first()
    
    if admin:
        # Add words
        for word_data in initial_words:
            # Check if word already exists
            if not Word.query.filter_by(word=word_data['word']).first():
                word = Word(
                    word=word_data['word'],
                    audio_url=word_data['audio_url'],
                    added_by=admin.id,
                    is_active=True
                )
                db.session.add(word)
        
        db.session.commit()
        print("Initial words added successfully!")
    else:
        print("Error: Admin user not found!") 