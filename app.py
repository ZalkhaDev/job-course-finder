import streamlit as st
import random
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Page config
st.set_page_config(page_title="🐸 Frog & Treasure Island", layout="wide")

# Constants
MAX_LIVES = 3
TOTAL_LEVELS = 10
NUM_OPTIONS = 4

@dataclass
class Question:
    word: str
    meaning: str
    distractors: List[str]
    difficulty: int  # 1=easy, 2=medium, 3=hard

class PlayerProfiler:
    """Tracks player performance and estimates success probability"""
    def __init__(self):
        self.difficulty_stats = {1: [], 2: [], 3: []}
        self.recent_performance = []
        
    def update_performance(self, difficulty: int, correct: bool):
        self.difficulty_stats[difficulty].append(1 if correct else 0)
        self.recent_performance.append(1 if correct else 0)
        if len(self.recent_performance) > 5:
            self.recent_performance.pop(0)
    
    def get_success_probability(self, difficulty: int) -> float:
        """Estimate player's probability of success for a given difficulty"""
        stats = self.difficulty_stats[difficulty]
        if not stats:
            return 0.5  # Default 50% if no data
        return sum(stats) / len(stats)
    
    def get_overall_skill(self) -> float:
        """Get overall player skill level"""
        if not self.recent_performance:
            return 0.5
        return sum(self.recent_performance) / len(self.recent_performance)

class MinimaxAI:
    """AI Question Master using a two-ply adversarial selection"""
    def __init__(self, questions: List[Question], profiler: PlayerProfiler):
        self.questions = questions
        self.profiler = profiler
        self.max_depth = 2  # currently using two-ply (AI -> Player)
        
    def evaluate_state(self, level: int, lives: int) -> float:
        """
        Heuristic evaluation function returning a utility for the AI (higher = better for AI).
        The AI prefers questions that reduce player's chance to progress.
        """
        progress_ratio = level / TOTAL_LEVELS
        lives_factor = lives / MAX_LIVES
        
        # Utility components:
        # - Less player progress is better for AI -> contribute positively when progress low
        # - Fewer lives is better for AI
        ai_score = (1.0 - progress_ratio) * 20 + ( (MAX_LIVES - lives) * 5 )
        return ai_score
    
    def evaluate_question_for_ai(self, level: int, lives: int, question: Question) -> float:
        """
        Evaluate the AI utility for a specific question by estimating the player's response.
        We compute the *worst-case* (for AI) player choice (i.e., the player will choose the option
        that gives the lowest AI utility). Then AI selects question that maximizes that worst-case.
        """
        # estimate probability of player answering correctly for that difficulty
        success_prob = self.profiler.get_success_probability(question.difficulty)
        # For each possible choice, simulate outcome (correct or wrong). Player will pick the best choice for them
        # (i.e., the choice that results in the lowest AI utility). So AI assumes player acts optimally.
        # We don't need to iterate actual textual options because correctness is binary.
        # But to keep logic close to reality we'll consider two branches: correct or incorrect.
        
        # Branch: player picks correct answer (probability = success_prob)
        level_if_correct = min(TOTAL_LEVELS, level + 1)
        lives_if_correct = lives
        util_if_correct = self.evaluate_state(level_if_correct, lives_if_correct)
        
        # Branch: player picks wrong answer (probability = 1 - success_prob)
        level_if_wrong = level
        lives_if_wrong = max(0, lives - 1)
        util_if_wrong = self.evaluate_state(level_if_wrong, lives_if_wrong)
        
        # From AI perspective, the player will choose action that minimizes AI utility.
        # But in expectation, the player's actual response is probabilistic; for adversarial (worst-case)
        # assume player picks whatever gives the minimum utility to AI.
        worst_case_util = min(util_if_correct, util_if_wrong)
        
        # To combine both the difficulty and the worst-case util, add a difficulty bonus
        difficulty_bonus = (question.difficulty - 1) * 3  # higher difficulty slightly increases AI utility
        return worst_case_util + difficulty_bonus
    
    def select_question(self, level: int, lives: int, used_questions: set) -> Question:
        """Select the best question using two-ply adversarial reasoning"""
        available = [q for q in self.questions if id(q) not in used_questions]
        
        if not available:
            return random.choice(self.questions)
        
        # Adjust available questions based on player skill (simple filtering)
        skill = self.profiler.get_overall_skill()
        
        if skill < 0.4:
            preferred = [q for q in available if q.difficulty <= 2]
        elif skill > 0.7:
            preferred = [q for q in available if q.difficulty >= 2]
        else:
            preferred = available
        
        if not preferred:
            preferred = available
        
        # If list is large, sample to limit runtime (Minimax depth is small but keep responsive)
        candidate_list = preferred[:16]  # take up to 16 candidates to evaluate
        
        best_q = None
        best_score = float('-inf')
        
        for q in candidate_list:
            score = self.evaluate_question_for_ai(level, lives, q)
            # choose question that maximizes AI's worst-case utility
            if score > best_score:
                best_score = score
                best_q = q
        
        return best_q if best_q else random.choice(preferred)

def load_questions() -> List[Question]:
    """Load vocabulary questions"""
    return [
        Question("Ephemeral", "Lasting for a very short time", 
                ["Eternal", "Permanent", "Lasting"], 1),
        Question("Ubiquitous", "Present everywhere", 
                ["Rare", "Unique", "Absent"], 2),
        Question("Serendipity", "Finding good things by chance", 
                ["Misfortune", "Planning", "Disaster"], 2),
        Question("Perspicacious", "Having keen insight", 
                ["Foolish", "Confused", "Ignorant"], 3),
        Question("Ameliorate", "To make better or improve", 
                ["Worsen", "Destroy", "Neglect"], 2),
        Question("Cacophony", "Harsh, discordant mixture of sounds", 
                ["Harmony", "Silence", "Melody"], 2),
        Question("Esoteric", "Intended for a small group", 
                ["Common", "Popular", "Universal"], 3),
        Question("Loquacious", "Very talkative", 
                ["Silent", "Brief", "Quiet"], 1),
        Question("Magnanimous", "Generous and forgiving", 
                ["Petty", "Selfish", "Cruel"], 2),
        Question("Perfidious", "Deceitful and untrustworthy", 
                ["Loyal", "Honest", "Faithful"], 3),
        Question("Sanguine", "Optimistic and positive", 
                ["Pessimistic", "Gloomy", "Sad"], 2),
        Question("Tenacious", "Persistent and determined", 
                ["Weak", "Giving up", "Lazy"], 1),
        Question("Verbose", "Using more words than needed", 
                ["Concise", "Brief", "Short"], 1),
        Question("Zealous", "Showing great enthusiasm", 
                ["Apathetic", "Indifferent", "Lazy"], 2),
        Question("Benevolent", "Kind and generous", 
                ["Cruel", "Mean", "Hostile"], 1),
    ]

def initialize_game():
    """Initialize game state"""
    st.session_state.level = 1
    st.session_state.lives = MAX_LIVES
    st.session_state.score = 0
    st.session_state.correct_answers = 0
    st.session_state.total_attempts = 0
    st.session_state.used_questions = set()
    st.session_state.game_over = False
    st.session_state.victory = False
    st.session_state.feedback = None
    st.session_state.questions = load_questions()
    st.session_state.profiler = PlayerProfiler()
    st.session_state.ai = MinimaxAI(st.session_state.questions, st.session_state.profiler)
    setup_new_question()

def setup_new_question():
    """Setup a new question"""
    question = st.session_state.ai.select_question(
        st.session_state.level, 
        st.session_state.lives,
        st.session_state.used_questions
    )
    st.session_state.used_questions.add(id(question))
    st.session_state.current_question = question
    
    # Create answer options (ensure NUM_OPTIONS if possible)
    options = [question.meaning] + question.distractors
    # If fewer distractors than needed, fill with other meanings
    if len(options) < NUM_OPTIONS:
        extras = [q.meaning for q in st.session_state.questions if q.meaning not in options]
        random.shuffle(extras)
        while len(options) < NUM_OPTIONS and extras:
            options.append(extras.pop())
    random.shuffle(options)
    st.session_state.options = options

def handle_answer(selected_option: str):
    """Process player's answer"""
    question = st.session_state.current_question
    st.session_state.total_attempts += 1
    
    if selected_option == question.meaning:
        # Correct answer
        st.session_state.correct_answers += 1
        st.session_state.score += 10 * question.difficulty
        st.session_state.level += 1
        st.session_state.feedback = ("correct", f"✅ Correct! '{question.word}' means '{question.meaning}'")
        st.session_state.profiler.update_performance(question.difficulty, True)
        
        if st.session_state.level > TOTAL_LEVELS:
            st.session_state.victory = True
            st.session_state.game_over = True
    else:
        # Wrong answer
        st.session_state.lives -= 1
        st.session_state.feedback = ("wrong", f"❌ Wrong! '{question.word}' means '{question.meaning}'")
        st.session_state.profiler.update_performance(question.difficulty, False)
        
        if st.session_state.lives <= 0:
            st.session_state.game_over = True

# Initialize session state
if 'level' not in st.session_state:
    initialize_game()

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(to bottom, #87CEEB 0%, #52A4D9 100%);
    }
    .stButton button {
        width: 100%;
        height: 100px;
        font-size: 18px;
        border-radius: 15px;
        border: 3px solid #1e7d5e;
        background-color: #2ecc71;
        color: white;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton button:hover {
        background-color: #27ae60;
        transform: scale(1.05);
    }
    .stat-box {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-size: 20px;
        font-weight: bold;
    }
    .question-box {
        background-color: rgba(0, 0, 0, 0.7);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin: 20px 0;
    }
    .question-text {
        color: white;
        font-size: 32px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 style='text-align: center; color: white;'>🐸 Frog & Treasure Island 🏝️</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: white;'>AI-Powered Vocabulary Learning Game</h3>", unsafe_allow_html=True)

# Game stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"<div class='stat-box'>❤️ Lives: {st.session_state.lives}</div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='stat-box'>🎯 Score: {st.session_state.score}</div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='stat-box'>📊 Level: {st.session_state.level}/{TOTAL_LEVELS}</div>", unsafe_allow_html=True)
with col4:
    accuracy = (st.session_state.correct_answers / st.session_state.total_attempts * 100) if st.session_state.total_attempts > 0 else 0
    st.markdown(f"<div class='stat-box'>✨ Accuracy: {accuracy:.0f}%</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Game Over / Victory Screen
if st.session_state.game_over:
    if st.session_state.victory:
        st.balloons()
        st.markdown("<div style='text-align: center; font-size: 48px;'>🎉 VICTORY! 🎉</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; font-size: 24px; color: white;'>You reached the treasure island!</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align: center; font-size: 48px;'>💀 Game Over 💀</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; font-size: 24px; color: white;'>The frog didn't make it...</div>", unsafe_allow_html=True)
    
    st.markdown(f"<div style='text-align: center; font-size: 28px; color: gold; margin: 20px;'>Final Score: {st.session_state.score}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center; font-size: 22px; color: white;'>Accuracy: {accuracy:.1f}%</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Play Again", key="restart"):
            initialize_game()
            st.rerun()

# Active Game
elif not st.session_state.game_over:
    # Show feedback if available
    if st.session_state.feedback:
        feedback_type, feedback_msg = st.session_state.feedback
        if feedback_type == "correct":
            st.success(feedback_msg)
        else:
            st.error(feedback_msg)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("➡️ Next Question", key="next"):
                st.session_state.feedback = None
                if not st.session_state.game_over:
                    setup_new_question()
                st.rerun()
    
    else:
        # Display question
        question = st.session_state.current_question
        
        # Progress bar
        progress = (st.session_state.level - 1) / TOTAL_LEVELS
        st.progress(progress)
        st.markdown(f"<div style='text-align: center; color: white; font-size: 18px;'>🐸 {int(progress * 100)}% to the treasure island! 🏝️</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Question display
        st.markdown(f"""
        <div class='question-box'>
            <div class='question-text'>What does '<span style='color: #f1c40f;'>{question.word}</span>' mean?</div>
            <div style='color: #bdc3c7; font-size: 16px; margin-top: 10px;'>Difficulty: {'⭐' * question.difficulty}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h4 style='text-align: center; color: white;'>🪷 Jump to the correct lily pad! 🪷</h4>", unsafe_allow_html=True)
        
        # Answer options (lily pads)
        cols = st.columns(2)
        for idx, option in enumerate(st.session_state.options):
            with cols[idx % 2]:
                if st.button(f"🪷 {option}", key=f"option_{idx}"):
                    handle_answer(option)
                    st.rerun()

# Sidebar with instructions
with st.sidebar:
    st.header("📖 How to Play")
    st.markdown("""
    **Objective:** Help the frog reach the treasure island by answering vocabulary questions correctly!
    
    **Rules:**
    - Answer 10 questions correctly to win
    - You have 3 lives
    - Wrong answer = lose 1 life
    - The AI adapts difficulty to your skill level
    
    **Scoring:**
    - Easy (⭐): 10 points
    - Medium (⭐⭐): 20 points
    - Hard (⭐⭐⭐): 30 points
    
    **AI Features:**
    - Two-ply adversarial reasoning (AI chooses question, assumes player chooses best answer)
    - Dynamic difficulty adjustment
    - Player performance profiling
    """)
    
    st.markdown("---")
    st.markdown("**💡 Tip:** The AI learns your strengths and weaknesses!")
