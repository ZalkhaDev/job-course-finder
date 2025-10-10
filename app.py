import streamlit as st
import random
import time
import math
from dataclasses import dataclass
from typing import List

# Page config
st.set_page_config(
    page_title="🐸 Frog & Treasure Island",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# Question data with categories
@dataclass
class Question:
    word: str
    meaning: str
    distractors: List[str]
    difficulty: int
    category: str

QUESTIONS = [
    # Easy - Basic
    Question("Happy", "Feeling joy", ["Sad", "Angry", "Tired"], 1, "Emotions"),
    Question("Quick", "Moving fast", ["Slow", "Lazy", "Sluggish"], 1, "Speed"),
    Question("Bright", "Full of light", ["Dark", "Dim", "Dull"], 1, "Light"),
    Question("Small", "Little in size", ["Large", "Huge", "Giant"], 1, "Size"),
    Question("Loud", "Making much noise", ["Quiet", "Silent", "Soft"], 1, "Sound"),
    Question("Hot", "High temperature", ["Cold", "Cool", "Chilly"], 1, "Temperature"),
    Question("Fast", "High speed", ["Slow", "Sluggish", "Dawdling"], 1, "Speed"),
    
    # Medium - Intermediate
    Question("Ephemeral", "Short-lived", ["Eternal", "Permanent", "Lasting"], 2, "Time"),
    Question("Ubiquitous", "Everywhere", ["Rare", "Unique", "Absent"], 2, "Presence"),
    Question("Serendipity", "Lucky chance", ["Misfortune", "Bad luck", "Disaster"], 2, "Fortune"),
    Question("Ameliorate", "Improve things", ["Worsen", "Destroy", "Damage"], 2, "Change"),
    Question("Cacophony", "Harsh sounds", ["Harmony", "Music", "Melody"], 2, "Sound"),
    Question("Sanguine", "Optimistic", ["Pessimistic", "Gloomy", "Sad"], 2, "Attitude"),
    Question("Zealous", "Very eager", ["Apathetic", "Lazy", "Indifferent"], 2, "Emotion"),
    Question("Enigmatic", "Mysterious", ["Clear", "Obvious", "Plain"], 2, "Mystery"),
    Question("Resilient", "Quick recovery", ["Fragile", "Weak", "Delicate"], 2, "Strength"),
    Question("Pragmatic", "Practical", ["Idealistic", "Theoretical", "Abstract"], 2, "Nature"),
    Question("Eloquent", "Fluent speaker", ["Inarticulate", "Stammering", "Mute"], 2, "Speech"),
    
    # Hard - Advanced
    Question("Perspicacious", "Keen judgment", ["Foolish", "Naive", "Gullible"], 3, "Intelligence"),
    Question("Esoteric", "For specialists", ["Common", "Popular", "Universal"], 3, "Knowledge"),
    Question("Perfidious", "Dishonest", ["Loyal", "Trustworthy", "Faithful"], 3, "Character"),
    Question("Obsequious", "Overly servile", ["Defiant", "Bold", "Assertive"], 3, "Behavior"),
    Question("Recalcitrant", "Stubborn", ["Compliant", "Obedient", "Agreeable"], 3, "Attitude"),
    Question("Munificent", "Extremely generous", ["Stingy", "Miserly", "Selfish"], 3, "Generosity"),
    Question("Pellucid", "Crystal clear", ["Obscure", "Confusing", "Vague"], 3, "Clarity"),
    Question("Phlegmatic", "Calm personality", ["Excitable", "Passionate", "Emotional"], 3, "Temperament"),
]

def initialize_game():
    """Initialize game state"""
    st.session_state.level = 1
    st.session_state.lives = 3
    st.session_state.score = 0
    st.session_state.streak = 0
    st.session_state.best_streak = 0
    st.session_state.total_attempts = 0
    st.session_state.correct_answers = 0
    st.session_state.used_questions = set()
    st.session_state.game_over = False
    st.session_state.victory = False
    st.session_state.feedback = None
    st.session_state.start_time = time.time()
    st.session_state.game_history = []
    st.session_state.category_stats = {}
    setup_question()

def setup_question():
    """Setup new question"""
    available = [q for idx, q in enumerate(QUESTIONS) if idx not in st.session_state.used_questions]
    
    if not available:
        st.session_state.used_questions.clear()
        available = QUESTIONS
    
    question = random.choice(available)
    idx = QUESTIONS.index(question)
    st.session_state.used_questions.add(idx)
    st.session_state.current_question = question
    st.session_state.question_start_time = time.time()
    
    # Shuffle options
    options = [question.meaning] + question.distractors
    random.shuffle(options)
    st.session_state.options = options

def handle_answer(selected):
    """Process answer with enhanced feedback"""
    q = st.session_state.current_question
    is_correct = (selected == q.meaning)
    response_time = time.time() - st.session_state.question_start_time
    
    st.session_state.total_attempts += 1
    
    if is_correct:
        st.session_state.correct_answers += 1
        st.session_state.streak += 1
        st.session_state.best_streak = max(st.session_state.best_streak, st.session_state.streak)
        
        # Enhanced scoring system
        base = q.difficulty * 10
        time_bonus = max(0, int(base * 0.5 * (1 - min(response_time / 15, 1))))
        streak_bonus = min(st.session_state.streak * 3, 30)
        difficulty_multiplier = 1 + (q.difficulty - 1) * 0.5
        
        total = int((base + time_bonus + streak_bonus) * difficulty_multiplier)
        st.session_state.score += total
        st.session_state.level += 1
        
        # Track category stats
        if q.category not in st.session_state.category_stats:
            st.session_state.category_stats[q.category] = {'correct': 0, 'total': 0}
        st.session_state.category_stats[q.category]['correct'] += 1
        st.session_state.category_stats[q.category]['total'] += 1
        
        # Determine bonus message
        if st.session_state.streak >= 5:
            streak_msg = f"🔥 ON FIRE! {st.session_state.streak} in a row!"
        elif st.session_state.streak >= 3:
            streak_msg = f"🔥 Hot streak! {st.session_state.streak} correct!"
        else:
            streak_msg = f"Keep it up! {st.session_state.streak} in a row"
        
        st.session_state.feedback = {
            'type': 'correct',
            'message': f"✅ Perfect!",
            'definition': f"'{q.word}' = {q.meaning}",
            'category': f"Category: {q.category}",
            'bonus': f"+{total} pts | {streak_msg}",
            'breakdown': f"Base: {base} | Speed: {time_bonus} | Streak: {streak_bonus}"
        }
        
        st.session_state.game_history.append({
            'level': st.session_state.level - 1,
            'word': q.word,
            'correct': True,
            'time': response_time
        })
        
        if st.session_state.level > 10:
            st.session_state.victory = True
            st.session_state.game_over = True
    else:
        st.session_state.lives -= 1
        st.session_state.streak = 0
        
        # Track category stats
        if q.category not in st.session_state.category_stats:
            st.session_state.category_stats[q.category] = {'correct': 0, 'total': 0}
        st.session_state.category_stats[q.category]['total'] += 1
        
        st.session_state.feedback = {
            'type': 'wrong',
            'message': f"❌ Oops!",
            'definition': f"'{q.word}' = {q.meaning}",
            'category': f"Category: {q.category}",
            'bonus': f"You selected: {selected}",
            'breakdown': ""
        }
        
        st.session_state.game_history.append({
            'level': st.session_state.level,
            'word': q.word,
            'correct': False,
            'time': response_time
        })
        
        if st.session_state.lives <= 0:
            st.session_state.game_over = True

# Initialize
if 'level' not in st.session_state:
    initialize_game()

# Custom CSS with animations
st.markdown("""
<style>
    [data-testid="stMainBlockContainer"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4a90e2 75%, #2c5282 100%);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        padding: 20px;
        min-height: 100vh;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .header-text {
        text-align: center;
        color: white;
        text-shadow: 4px 4px 8px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    
    .header-text h1 {
        font-size: 56px;
        margin: 0;
        animation: slideDown 0.8s ease-out;
    }
    
    @keyframes slideDown {
        from { transform: translateY(-30px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .stat-box {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        border: 2px solid rgba(255,255,255,0.3);
        transition: all 0.3s ease;
    }
    
    .stat-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.3);
    }
    
    .stat-value {
        font-size: 32px;
        font-weight: bold;
        color: #2c3e50;
    }
    
    .stat-label {
        font-size: 13px;
        color: #7f8c8d;
        margin-top: 8px;
        font-weight: 600;
    }
    
    .question-box {
        background: linear-gradient(135deg, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.7) 100%);
        padding: 50px 40px;
        border-radius: 25px;
        text-align: center;
        margin: 40px 0;
        box-shadow: 0 15px 50px rgba(0,0,0,0.5);
        border: 3px solid rgba(243, 156, 18, 0.3);
        animation: fadeInScale 0.6s ease-out;
    }
    
    @keyframes fadeInScale {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }
    
    .question-word {
        font-size: 64px;
        color: #f39c12;
        font-weight: 900;
        margin-bottom: 20px;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.6);
        letter-spacing: 2px;
    }
    
    .question-prompt {
        font-size: 22px;
        color: #ecf0f1;
        margin-bottom: 15px;
        font-weight: 600;
    }
    
    .difficulty-stars {
        font-size: 24px;
        color: #f39c12;
        margin: 15px 0;
        letter-spacing: 3px;
    }
    
    .lily-pads-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 25px;
        max-width: 900px;
        margin: 40px auto;
    }
    
    .stButton button {
        width: 100% !important;
        height: 140px !important;
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 70%, #1e8449 100%) !important;
        color: white !important;
        border: 5px solid #196f3d !important;
        border-radius: 80px !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3) !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        cursor: pointer !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton button:hover {
        transform: translateY(-12px) scale(1.08) !important;
        box-shadow: 0 20px 50px rgba(0,0,0,0.4) !important;
        border-color: #f39c12 !important;
        background: linear-gradient(135deg, #27ae60 0%, #229954 70%, #186a3b 100%) !important;
    }
    
    .stButton button:active {
        transform: translateY(-5px) scale(1.02) !important;
    }
    
    .feedback-box {
        background: white;
        padding: 50px;
        border-radius: 25px;
        text-align: center;
        margin: 40px 0;
        box-shadow: 0 15px 60px rgba(0,0,0,0.4);
        animation: popIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        border-top: 8px solid;
    }
    
    @keyframes popIn {
        0% { opacity: 0; transform: scale(0.8); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    .feedback-correct {
        border-top-color: #27ae60;
    }
    
    .feedback-wrong {
        border-top-color: #e74c3c;
    }
    
    .feedback-title {
        font-size: 44px;
        font-weight: 900;
        margin-bottom: 20px;
    }
    
    .feedback-definition {
        font-size: 20px;
        color: #2c3e50;
        padding: 20px;
        background: linear-gradient(135deg, #ecf0f1 0%, #f8f9fa 100%);
        border-radius: 15px;
        margin: 20px 0;
        font-weight: 600;
    }
    
    .feedback-category {
        font-size: 16px;
        color: #7f8c8d;
        margin: 10px 0;
    }
    
    .feedback-bonus {
        font-size: 18px;
        color: #2c3e50;
        margin-top: 15px;
        font-weight: 700;
    }
    
    .feedback-breakdown {
        font-size: 14px;
        color: #7f8c8d;
        margin-top: 10px;
    }
    
    .island {
        background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
        padding: 25px 50px;
        border-radius: 50% 50% 0 0;
        text-align: center;
        margin: 0 auto 30px;
        width: fit-content;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        border: 3px solid #654321;
    }
    
    .treasure {
        font-size: 56px;
        animation: bounce 2s infinite;
        display: inline-block;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-15px) rotate(5deg); }
    }
    
    .progress-container {
        background: rgba(255,255,255,0.15);
        border-radius: 25px;
        padding: 15px;
        margin: 25px 0;
        box-shadow: inset 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #2ecc71, #27ae60) !important;
        height: 30px !important;
        border-radius: 15px !important;
    }
    
    .progress-text {
        text-align: center;
        color: white;
        font-size: 18px;
        font-weight: bold;
        margin-top: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .game-over-title {
        font-size: 56px;
        font-weight: 900;
        margin: 30px 0;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
    }
    
    .stats-summary {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin: 30px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="header-text"><h1>🐸 Frog & Treasure Island 🏝️</h1><p style="font-size: 20px; margin: 5px;">Jump to the correct meaning!</p></div>', unsafe_allow_html=True)

# Stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="stat-box"><div class="stat-value">{"❤️" * st.session_state.lives}</div><div class="stat-label">LIVES</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="stat-box"><div class="stat-value">{st.session_state.score}</div><div class="stat-label">SCORE</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="stat-box"><div class="stat-value">{st.session_state.level}/10</div><div class="stat-label">LEVEL</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="stat-box"><div class="stat-value">🔥 {st.session_state.streak}</div><div class="stat-label">STREAK</div></div>', unsafe_allow_html=True)

# Island
st.markdown('<div class="island"><div class="treasure">💎</div></div>', unsafe_allow_html=True)

# Progress
progress = (st.session_state.level - 1) / 10
st.markdown('<div class="progress-container">', unsafe_allow_html=True)
st.progress(progress)
st.markdown(f'<div class="progress-text">🐸 {int(progress * 100)}% to Treasure Island! 🏝️</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Game Over
if st.session_state.game_over:
    if st.session_state.victory:
        st.balloons()
        st.markdown(f'<div class="game-over-title" style="color: gold;">🎉 VICTORY! 🎉</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: center; color: white; font-size: 28px; margin: 20px;">You conquered the treasure island!</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="game-over-title" style="color: #e74c3c;">💀 Game Over</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: center; color: white; font-size: 28px; margin: 20px;">The frog\'s adventure ends...</div>', unsafe_allow_html=True)
    
    accuracy = (st.session_state.correct_answers / st.session_state.total_attempts * 100) if st.session_state.total_attempts > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Final Score", st.session_state.score, delta=None)
    with col2:
        st.metric("Accuracy", f"{accuracy:.1f}%", delta=None)
    with col3:
        st.metric("Best Streak", st.session_state.best_streak, delta=None)
    
    # Category breakdown
    if st.session_state.category_stats:
        st.markdown("### 📊 Performance by Category")
        cat_cols = st.columns(len(st.session_state.category_stats))
        for idx, (category, stats) in enumerate(st.session_state.category_stats.items()):
            with cat_cols[idx]:
                cat_accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
                st.metric(category, f"{cat_accuracy:.0f}%", f"{stats['correct']}/{stats['total']}")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🔄 Play Again", use_container_width=True):
        initialize_game()
        st.rerun()

# Active Game
elif not st.session_state.game_over:
    if st.session_state.feedback:
        fb = st.session_state.feedback
        fb_class = "feedback-correct" if fb['type'] == 'correct' else "feedback-wrong"
        
        st.markdown(f"""
        <div class="feedback-box {fb_class}">
            <div class="feedback-title">{fb['message']}</div>
            <div class="feedback-definition">{fb['definition']}</div>
            <div class="feedback-category">{fb['category']}</div>
            <div class="feedback-bonus">{fb['bonus']}</div>
            {f'<div class="feedback-breakdown">{fb["breakdown"]}</div>' if fb['breakdown'] else ''}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Continue →", use_container_width=True, key="continue"):
            st.session_state.feedback = None
            if not st.session_state.game_over:
                setup_question()
            st.rerun()
    else:
        q = st.session_state.current_question
        
        # Question
        st.markdown(f"""
        <div class="question-box">
            <div class="question-word">{q.word}</div>
            <div class="question-prompt">Choose the correct meaning:</div>
            <div class="difficulty-stars">{"⭐" * q.difficulty}</div>
            <div style="color: #ecf0f1; font-size: 14px;">Category: {q.category}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<h3 style="text-align: center; color: white; margin: 40px 0;">🪷 Jump to the correct lily pad! 🪷</h3>', unsafe_allow_html=True)
        
        # Lily pads
        col1, col2 = st.columns(2)
        for idx, option in enumerate(st.session_state.options):
            with col1 if idx % 2 == 0 else col2:
                if st.button(f"🪷 {option}", key=f"opt_{idx}"):
                    handle_answer(option)
                    st.rerun()
