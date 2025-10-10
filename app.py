import streamlit as st
import random
import time
from dataclasses import dataclass
from typing import List

# Page config
st.set_page_config(
    page_title="🐸 Frog & Treasure Island",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Question data
@dataclass
class Question:
    word: str
    meaning: str
    distractors: List[str]
    difficulty: int

QUESTIONS = [
    # Easy
    Question("Ephemeral", "Short-lived", ["Eternal", "Permanent", "Long-lasting"], 1),
    Question("Loquacious", "Talkative", ["Silent", "Brief", "Quiet"], 1),
    Question("Tenacious", "Persistent", ["Weak", "Quitting", "Lazy"], 1),
    Question("Verbose", "Wordy", ["Concise", "Brief", "Short"], 1),
    Question("Benevolent", "Kind", ["Cruel", "Mean", "Hostile"], 1),
    Question("Luminous", "Bright", ["Dark", "Dim", "Shadowy"], 1),
    
    # Medium
    Question("Ubiquitous", "Everywhere", ["Rare", "Unique", "Absent"], 2),
    Question("Serendipity", "Lucky discovery", ["Bad luck", "Planning", "Disaster"], 2),
    Question("Ameliorate", "Make better", ["Worsen", "Destroy", "Ruin"], 2),
    Question("Cacophony", "Harsh sounds", ["Harmony", "Silence", "Melody"], 2),
    Question("Magnanimous", "Generous", ["Petty", "Selfish", "Cruel"], 2),
    Question("Sanguine", "Optimistic", ["Pessimistic", "Gloomy", "Sad"], 2),
    Question("Zealous", "Enthusiastic", ["Apathetic", "Indifferent", "Lazy"], 2),
    Question("Enigmatic", "Mysterious", ["Clear", "Obvious", "Plain"], 2),
    Question("Resilient", "Strong recovery", ["Fragile", "Weak", "Delicate"], 2),
    
    # Hard
    Question("Perspicacious", "Keen insight", ["Foolish", "Confused", "Ignorant"], 3),
    Question("Esoteric", "Specialized", ["Common", "Popular", "Universal"], 3),
    Question("Perfidious", "Untrustworthy", ["Loyal", "Honest", "Faithful"], 3),
    Question("Obsequious", "Overly obedient", ["Defiant", "Independent", "Proud"], 3),
    Question("Recalcitrant", "Stubbornly resistant", ["Compliant", "Obedient", "Agreeable"], 3),
]

def initialize_game():
    """Initialize game state"""
    st.session_state.level = 1
    st.session_state.lives = 3
    st.session_state.score = 0
    st.session_state.streak = 0
    st.session_state.best_streak = 0
    st.session_state.used_questions = set()
    st.session_state.game_over = False
    st.session_state.victory = False
    st.session_state.feedback = None
    st.session_state.start_time = time.time()
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
    """Process answer"""
    q = st.session_state.current_question
    is_correct = (selected == q.meaning)
    response_time = time.time() - st.session_state.question_start_time
    
    st.session_state.total_attempts = st.session_state.get('total_attempts', 0) + 1
    
    if is_correct:
        st.session_state.correct_answers = st.session_state.get('correct_answers', 0) + 1
        st.session_state.streak += 1
        st.session_state.best_streak = max(st.session_state.best_streak, st.session_state.streak)
        
        # Calculate score
        base = q.difficulty * 10
        time_bonus = max(0, int(base * 0.5 * (1 - min(response_time / 15, 1))))
        streak_bonus = min(st.session_state.streak * 2, 20)
        total = base + time_bonus + streak_bonus
        
        st.session_state.score += total
        st.session_state.level += 1
        
        st.session_state.feedback = {
            'type': 'correct',
            'message': f"✅ Correct!",
            'definition': f"'{q.word}' = {q.meaning}",
            'bonus': f"+{total} pts (Base: {base} | Speed: {time_bonus} | Streak: {streak_bonus})"
        }
        
        if st.session_state.level > 10:
            st.session_state.victory = True
            st.session_state.game_over = True
    else:
        st.session_state.lives -= 1
        st.session_state.streak = 0
        
        st.session_state.feedback = {
            'type': 'wrong',
            'message': f"❌ Wrong!",
            'definition': f"'{q.word}' = {q.meaning}",
            'bonus': f"You selected: {selected}"
        }
        
        if st.session_state.lives <= 0:
            st.session_state.game_over = True

# Initialize
if 'level' not in st.session_state:
    initialize_game()

# Custom CSS
st.markdown("""
<style>
    [data-testid="stMainBlockContainer"] {
        background: linear-gradient(to bottom, #87CEEB 0%, #4A90E2 50%, #2E5C8A 100%);
        padding: 20px;
    }
    
    .header-text {
        text-align: center;
        color: white;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
    }
    
    .stat-box {
        background: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .stat-value {
        font-size: 32px;
        font-weight: bold;
        color: #2c3e50;
    }
    
    .stat-label {
        font-size: 14px;
        color: #7f8c8d;
        margin-top: 8px;
    }
    
    .question-box {
        background: rgba(0, 0, 0, 0.8);
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        margin: 30px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }
    
    .question-word {
        font-size: 56px;
        color: #f39c12;
        font-weight: bold;
        margin-bottom: 15px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .question-prompt {
        font-size: 20px;
        color: white;
        margin-bottom: 10px;
    }
    
    .lily-pad-btn {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 70%, #1e8449 100%);
        color: white;
        border: 4px solid #196f3d;
        padding: 30px;
        border-radius: 100px;
        font-size: 18px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    .lily-pad-btn:hover {
        transform: translateY(-10px) scale(1.05);
        box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        border-color: #f39c12;
    }
    
    .feedback-box {
        background: white;
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        margin: 30px 0;
        box-shadow: 0 10px 50px rgba(0,0,0,0.3);
    }
    
    .feedback-correct {
        border-left: 8px solid #27ae60;
    }
    
    .feedback-wrong {
        border-left: 8px solid #e74c3c;
    }
    
    .feedback-title {
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    
    .feedback-definition {
        font-size: 18px;
        color: #2c3e50;
        padding: 15px;
        background: #ecf0f1;
        border-radius: 10px;
        margin: 15px 0;
    }
    
    .feedback-bonus {
        font-size: 16px;
        color: #7f8c8d;
        margin-top: 15px;
    }
    
    .island {
        background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
        padding: 20px 40px;
        border-radius: 50% 50% 0 0;
        text-align: center;
        margin: 0 auto 30px;
        width: fit-content;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    }
    
    .treasure {
        font-size: 48px;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .stButton button {
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="header-text"><h1>🐸 Frog & Treasure Island 🏝️</h1><p>Jump to the correct meaning!</p></div>', unsafe_allow_html=True)

# Stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="stat-box"><div class="stat-value">{"❤️" * st.session_state.lives}</div><div class="stat-label">Lives</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="stat-box"><div class="stat-value">{st.session_state.score}</div><div class="stat-label">Score</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="stat-box"><div class="stat-value">{st.session_state.level}/10</div><div class="stat-label">Level</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="stat-box"><div class="stat-value">🔥 {st.session_state.streak}</div><div class="stat-label">Streak</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Island
st.markdown('<div class="island"><div class="treasure">💎</div></div>', unsafe_allow_html=True)

# Progress
progress = (st.session_state.level - 1) / 10
st.progress(progress)
st.markdown(f'<div style="text-align: center; color: white; font-size: 18px; font-weight: bold;">🐸 {int(progress * 100)}% to treasure! 🏝️</div>', unsafe_allow_html=True)

# Game Over
if st.session_state.game_over:
    if st.session_state.victory:
        st.balloons()
        st.markdown('<div style="text-align: center; font-size: 48px;">🎉 VICTORY! 🎉</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: center; color: white; font-size: 24px;">You reached the treasure!</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align: center; font-size: 48px;">💀 Game Over</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: center; color: white; font-size: 24px;">The frog didn\'t make it...</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Final Score", st.session_state.score)
    with col2:
        accuracy = (st.session_state.correct_answers / st.session_state.total_attempts * 100) if st.session_state.total_attempts > 0 else 0
        st.metric("Accuracy", f"{accuracy:.0f}%")
    with col3:
        st.metric("Best Streak", st.session_state.best_streak)
    
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
            <div class="feedback-definition"><strong>{fb['definition']}</strong></div>
            <div class="feedback-bonus">{fb['bonus']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Continue →", use_container_width=True):
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
            <div style="color: #e67e22; font-size: 18px;">{"⭐" * q.difficulty}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<h3 style="text-align: center; color: white; margin: 30px 0;">🪷 Jump to the correct lily pad! 🪷</h3>', unsafe_allow_html=True)
        
        # Lily pads
        col1, col2 = st.columns(2)
        for idx, option in enumerate(st.session_state.options):
            with col1 if idx % 2 == 0 else col2:
                if st.button(f"🪷 {option}", key=f"opt_{idx}", use_container_width=True):
                    handle_answer(option)
                    st.rerun()
