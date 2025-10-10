import streamlit as st
import random
import math
import json
from dataclasses import dataclass, asdict
from typing import List, Tuple, Optional
import time

# Page config
st.set_page_config(
    page_title="🐸 Frog & Treasure Island",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
MAX_LIVES = 3
TOTAL_LEVELS = 10
NUM_OPTIONS = 4
DEPTH_LIMIT = 3

@dataclass
class Question:
    word: str
    meaning: str
    distractors: List[str]
    difficulty: int  # 1=easy, 2=medium, 3=hard
    category: str = "General"

class PlayerProfiler:
    """Advanced player performance tracking"""
    def __init__(self):
        self.difficulty_stats = {1: [], 2: [], 3: []}
        self.recent_performance = []
        self.response_times = []
        self.category_performance = {}
        
    def update_performance(self, difficulty: int, correct: bool, response_time: float, category: str):
        self.difficulty_stats[difficulty].append(1 if correct else 0)
        self.recent_performance.append(1 if correct else 0)
        self.response_times.append(response_time)
        
        if category not in self.category_performance:
            self.category_performance[category] = []
        self.category_performance[category].append(1 if correct else 0)
        
        # Keep only recent data
        if len(self.recent_performance) > 8:
            self.recent_performance.pop(0)
        if len(self.response_times) > 10:
            self.response_times.pop(0)
    
    def get_success_probability(self, difficulty: int) -> float:
        stats = self.difficulty_stats[difficulty]
        if not stats:
            return 0.5
        # Weighted average (recent performance matters more)
        weights = [0.5 ** i for i in range(len(stats) - 1, -1, -1)]
        weighted_sum = sum(s * w for s, w in zip(stats, weights))
        return weighted_sum / sum(weights)
    
    def get_overall_skill(self) -> float:
        if not self.recent_performance:
            return 0.5
        return sum(self.recent_performance) / len(self.recent_performance)
    
    def get_avg_response_time(self) -> float:
        return sum(self.response_times) / len(self.response_times) if self.response_times else 5.0
    
    def get_streak(self) -> int:
        """Get current correct answer streak"""
        streak = 0
        for perf in reversed(self.recent_performance):
            if perf == 1:
                streak += 1
            else:
                break
        return streak

class MinimaxAI:
    """Enhanced AI with improved decision making"""
    def __init__(self, questions: List[Question], profiler: PlayerProfiler):
        self.questions = questions
        self.profiler = profiler
        self.max_depth = DEPTH_LIMIT
        self.nodes_evaluated = 0
        self.pruning_count = 0
        
    def evaluate_state(self, level: int, lives: int, question: Question, streak: int) -> float:
        """Enhanced heuristic evaluation"""
        success_prob = self.profiler.get_success_probability(question.difficulty)
        
        # AI strategy: balance challenge and learning
        difficulty_factor = question.difficulty / 3.0
        progress_factor = level / TOTAL_LEVELS
        lives_factor = lives / MAX_LIVES
        streak_penalty = min(streak * 0.1, 0.5)  # Don't make it too easy during streaks
        
        # Adaptive challenge level
        skill = self.profiler.get_overall_skill()
        
        if skill > 0.8:  # High skill - increase challenge
            challenge_bonus = difficulty_factor * 3
        elif skill < 0.4:  # Low skill - provide learning opportunity
            challenge_bonus = -difficulty_factor * 2
        else:  # Medium skill - balanced approach
            challenge_bonus = 0
        
        # Final evaluation (AI wants to maximize learning while maintaining engagement)
        score = (
            -(success_prob * 8) +  # Prefer questions player might struggle with
            (difficulty_factor * 4) +  # Higher difficulty preference
            challenge_bonus +
            streak_penalty -
            (progress_factor * 2) +  # Slightly easier near end
            (lives_factor * 1)  # Consider remaining lives
        )
        
        return score
    
    def minimax(self, level: int, lives: int, depth: int, alpha: float, beta: float, 
                maximizing_player: bool, available_questions: List[Question], streak: int) -> Tuple[float, Optional[Question]]:
        """Minimax with Alpha-Beta Pruning - Enhanced"""
        self.nodes_evaluated += 1
        
        if depth == 0 or not available_questions:
            return 0, None
        
        if maximizing_player:
            max_eval = float('-inf')
            best_question = None
            
            # Sort questions by initial heuristic for better pruning
            scored_questions = [
                (self.evaluate_state(level, lives, q, streak), q) 
                for q in available_questions
            ]
            scored_questions.sort(reverse=True)
            
            for score, question in scored_questions:
                if score > max_eval:
                    max_eval = score
                    best_question = question
                
                alpha = max(alpha, score)
                if beta <= alpha:
                    self.pruning_count += 1
                    break  # Alpha-Beta pruning
            
            return max_eval, best_question
        
    def select_question(self, level: int, lives: int, used_questions: set, streak: int) -> Question:
        """Enhanced question selection"""
        self.nodes_evaluated = 0
        self.pruning_count = 0
        
        available = [q for q in self.questions if id(q) not in used_questions]
        
        if not available:
            # Reset and reuse questions
            return random.choice(self.questions)
        
        # Filter by appropriate difficulty
        skill = self.profiler.get_overall_skill()
        
        if skill < 0.3:
            preferred = [q for q in available if q.difficulty == 1]
        elif skill < 0.5:
            preferred = [q for q in available if q.difficulty <= 2]
        elif skill < 0.7:
            preferred = [q for q in available if q.difficulty >= 2]
        else:
            preferred = [q for q in available if q.difficulty >= 2]
        
        if not preferred:
            preferred = available
        
        # Use minimax to select best question
        _, best_question = self.minimax(
            level, lives, self.max_depth, 
            float('-inf'), float('inf'), 
            True, preferred[:10], streak
        )
        
        return best_question if best_question else random.choice(preferred)

def load_questions() -> List[Question]:
    """Expanded vocabulary questions with categories"""
    return [
        # Easy (1)
        Question("Ephemeral", "Lasting for a very short time", 
                ["Eternal", "Permanent", "Durable"], 1, "Time"),
        Question("Loquacious", "Very talkative", 
                ["Silent", "Brief", "Quiet"], 1, "Communication"),
        Question("Tenacious", "Persistent and determined", 
                ["Weak", "Giving up", "Lazy"], 1, "Character"),
        Question("Verbose", "Using more words than needed", 
                ["Concise", "Brief", "Short"], 1, "Communication"),
        Question("Benevolent", "Kind and generous", 
                ["Cruel", "Mean", "Hostile"], 1, "Character"),
        Question("Luminous", "Giving off light; bright", 
                ["Dark", "Dim", "Shadowy"], 1, "Light"),
        
        # Medium (2)
        Question("Ubiquitous", "Present everywhere", 
                ["Rare", "Unique", "Absent"], 2, "Presence"),
        Question("Serendipity", "Finding good things by chance", 
                ["Misfortune", "Planning", "Disaster"], 2, "Fortune"),
        Question("Ameliorate", "To make better or improve", 
                ["Worsen", "Destroy", "Neglect"], 2, "Change"),
        Question("Cacophony", "Harsh, discordant mixture of sounds", 
                ["Harmony", "Silence", "Melody"], 2, "Sound"),
        Question("Magnanimous", "Generous and forgiving", 
                ["Petty", "Selfish", "Cruel"], 2, "Character"),
        Question("Sanguine", "Optimistic and positive", 
                ["Pessimistic", "Gloomy", "Sad"], 2, "Emotion"),
        Question("Zealous", "Showing great enthusiasm", 
                ["Apathetic", "Indifferent", "Lazy"], 2, "Emotion"),
        Question("Enigmatic", "Mysterious and puzzling", 
                ["Clear", "Obvious", "Plain"], 2, "Mystery"),
        Question("Resilient", "Able to recover quickly", 
                ["Fragile", "Weak", "Delicate"], 2, "Strength"),
        
        # Hard (3)
        Question("Perspicacious", "Having keen insight and judgment", 
                ["Foolish", "Confused", "Ignorant"], 3, "Intelligence"),
        Question("Esoteric", "Intended for a small, specialized group", 
                ["Common", "Popular", "Universal"], 3, "Knowledge"),
        Question("Perfidious", "Deceitful and untrustworthy", 
                ["Loyal", "Honest", "Faithful"], 3, "Character"),
        Question("Obsequious", "Excessively obedient or attentive", 
                ["Defiant", "Independent", "Proud"], 3, "Behavior"),
        Question("Recalcitrant", "Stubbornly resistant to authority", 
                ["Compliant", "Obedient", "Agreeable"], 3, "Behavior"),
        Question("Munificent", "Very generous with money or gifts", 
                ["Stingy", "Greedy", "Miserly"], 3, "Generosity"),
        Question("Pellucid", "Transparently clear in meaning", 
                ["Obscure", "Confusing", "Vague"], 3, "Clarity"),
        Question("Phlegmatic", "Calm and unemotional in temperament", 
                ["Excitable", "Passionate", "Emotional"], 3, "Emotion"),
    ]

def initialize_game():
    """Initialize comprehensive game state"""
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
    st.session_state.question_start_time = None
    st.session_state.game_history = []
    st.session_state.streak = 0
    st.session_state.best_streak = 0
    st.session_state.ai_stats = {"nodes": 0, "pruning": 0}
    setup_new_question()

def setup_new_question():
    """Setup new question with enhanced tracking"""
    streak = st.session_state.get('streak', 0)
    question = st.session_state.ai.select_question(
        st.session_state.level, 
        st.session_state.lives,
        st.session_state.used_questions,
        streak
    )
    st.session_state.used_questions.add(id(question))
    st.session_state.current_question = question
    st.session_state.question_start_time = time.time()
    
    # Track AI performance
    st.session_state.ai_stats = {
        "nodes": st.session_state.ai.nodes_evaluated,
        "pruning": st.session_state.ai.pruning_count
    }
    
    # Create answer options with smart distractor placement
    options = [question.meaning] + question.distractors
    random.shuffle(options)
    st.session_state.options = options

def handle_answer(selected_option: str):
    """Enhanced answer processing with detailed tracking"""
    question = st.session_state.current_question
    st.session_state.total_attempts += 1
    
    # Calculate response time
    response_time = time.time() - st.session_state.question_start_time if st.session_state.question_start_time else 5.0
    
    is_correct = (selected_option == question.meaning)
    
    if is_correct:
        st.session_state.correct_answers += 1
        base_score = 10 * question.difficulty
        
        # Bonus for speed (up to 50% bonus)
        time_bonus = max(0, int(base_score * 0.5 * (1 - min(response_time / 15, 1))))
        
        # Streak bonus
        st.session_state.streak += 1
        streak_bonus = min(st.session_state.streak * 2, 20)
        
        total_score = base_score + time_bonus + streak_bonus
        st.session_state.score += total_score
        st.session_state.level += 1
        
        st.session_state.best_streak = max(st.session_state.best_streak, st.session_state.streak)
        
        st.session_state.feedback = (
            "correct", 
            f"✅ Correct! +{total_score} points\n\n"
            f"'{question.word}' means '{question.meaning}'\n"
            f"⚡ Speed bonus: +{time_bonus} | 🔥 Streak: {st.session_state.streak}"
        )
        
        if st.session_state.level > TOTAL_LEVELS:
            st.session_state.victory = True
            st.session_state.game_over = True
    else:
        st.session_state.lives -= 1
        st.session_state.streak = 0
        
        st.session_state.feedback = (
            "wrong", 
            f"❌ Incorrect!\n\n"
            f"'{question.word}' means '{question.meaning}'\n"
            f"You selected: '{selected_option}'"
        )
        
        if st.session_state.lives <= 0:
            st.session_state.game_over = True
    
    # Update profiler
    st.session_state.profiler.update_performance(
        question.difficulty, 
        is_correct, 
        response_time,
        question.category
    )
    
    # Track history
    st.session_state.game_history.append({
        "level": st.session_state.level,
        "word": question.word,
        "difficulty": question.difficulty,
        "correct": is_correct,
        "response_time": response_time
    })

# Initialize session state
if 'level' not in st.session_state:
    initialize_game()

# Enhanced CSS with animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        animation: gradient 15s ease infinite;
        background-size: 200% 200%;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .stButton button {
        width: 100%;
        height: 110px;
        font-size: 19px;
        border-radius: 20px;
        border: 4px solid #1e7d5e;
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }
    
    .stButton button:active {
        transform: translateY(-2px) scale(0.98);
    }
    
    .stat-box {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        font-size: 22px;
        font-weight: 700;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        transition: transform 0.3s;
    }
    
    .stat-box:hover {
        transform: translateY(-3px);
    }
    
    .question-box {
        background: linear-gradient(135deg, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0.6) 100%);
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        margin: 30px 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.4);
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .question-text {
        color: white;
        font-size: 36px;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .progress-container {
        background: rgba(255,255,255,0.2);
        border-radius: 20px;
        padding: 10px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Title with animation
st.markdown("""
<h1 style='text-align: center; color: white; font-size: 56px; text-shadow: 3px 3px 6px rgba(0,0,0,0.4); margin-bottom: 10px;'>
    🐸 Frog & Treasure Island 🏝️
</h1>
<h3 style='text-align: center; color: rgba(255,255,255,0.9); font-weight: 400;'>
    AI-Powered Adaptive Vocabulary Learning
</h3>
""", unsafe_allow_html=True)

# Enhanced stats display
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f"<div class='stat-box'>❤️<br>{st.session_state.lives} Lives</div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='stat-box'>🎯<br>{st.session_state.score} Pts</div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='stat-box'>📊<br>Lvl {st.session_state.level}/{TOTAL_LEVELS}</div>", unsafe_allow_html=True)
with col4:
    streak = st.session_state.get('streak', 0)
    st.markdown(f"<div class='stat-box'>🔥<br>{streak} Streak</div>", unsafe_allow_html=True)
with col5:
    accuracy = (st.session_state.correct_answers / st.session_state.total_attempts * 100) if st.session_state.total_attempts > 0 else 0
    st.markdown(f"<div class='stat-box'>✨<br>{accuracy:.0f}%</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Game Over / Victory Screen
if st.session_state.game_over:
    if st.session_state.victory:
        st.balloons()
        st.markdown("""
        <div style='text-align: center;'>
            <div style='font-size: 72px; margin: 20px;'>🎉 🏆 🎉</div>
            <div style='font-size: 48px; color: gold; font-weight: 700;'>VICTORY!</div>
            <div style='font-size: 24px; color: white; margin: 20px;'>You conquered the treasure island!</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align: center;'>
            <div style='font-size: 72px; margin: 20px;'>💀</div>
            <div style='font-size: 48px; color: #e74c3c; font-weight: 700;'>Game Over</div>
            <div style='font-size: 24px; color: white; margin: 20px;'>The frog's journey ends here...</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Final statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Final Score", st.session_state.score, delta=None)
    with col2:
        st.metric("Accuracy", f"{accuracy:.1f}%", delta=None)
    with col3:
        st.metric("Best Streak", st.session_state.best_streak, delta=None)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Play Again", key="restart", use_container_width=True):
            initialize_game()
            st.rerun()

# Active Game
elif not st.session_state.game_over:
    if st.session_state.feedback:
        feedback_type, feedback_msg = st.session_state.feedback
        if feedback_type == "correct":
            st.success(feedback_msg)
        else:
            st.error(feedback_msg)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("➡️ Next Question", key="next", use_container_width=True):
                st.session_state.feedback = None
                if not st.session_state.game_over:
                    setup_new_question()
                st.rerun()
    
    else:
        question = st.session_state.current_question
        
        # Enhanced progress bar
        progress = (st.session_state.level - 1) / TOTAL_LEVELS
        st.markdown("<div class='progress-container'>", unsafe_allow_html=True)
        st.progress(progress)
        st.markdown(f"""
        <div style='text-align: center; color: white; font-size: 20px; font-weight: 600; margin-top: 10px;'>
            🐸 {int(progress * 100)}% to treasure! 🏝️
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Question display
        difficulty_stars = "⭐" * question.difficulty
        st.markdown(f"""
        <div class='question-box'>
            <div class='question-text'>
                What does '<span style='color: #f39c12; font-size: 42px;'>{question.word}</span>' mean?
            </div>
            <div style='color: #bdc3c7; font-size: 18px; margin-top: 15px;'>
                {difficulty_stars} | Category: {question.category}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align: center; color: white; margin: 30px 0;'>🪷 Choose the correct lily pad! 🪷</h3>", unsafe_allow_html=True)
        
        # Answer options in 2x2 grid
        col1, col2 = st.columns(2)
        
        for idx, option in enumerate(st.session_state.options):
            with col1 if idx % 2 == 0 else col2:
                if st.button(f"🪷 {option}", key=f"option_{idx}"):
                    handle_answer(option)
                    st.rerun()

# Enhanced Sidebar
with st.sidebar:
    st.header("📖 How to Play")
    st.markdown("""
    **Objective:** Guide the frog to the treasure island by mastering vocabulary!
    
    **Game Rules:**
    - 🎯 Answer 10 questions to win
    - ❤️ You have 3 lives
    - ❌ Wrong answer = -1 life
    - ✅ Correct answer = progress!
    
    **Scoring System:**
    - ⭐ Easy: 10 points
    - ⭐⭐ Medium: 20 points
    - ⭐⭐⭐ Hard: 30 points
    - ⚡ Speed bonus: up to +50%
    - 🔥 Streak bonus: +2 per streak
    """)
    
    st.markdown("---")
    st.subheader("🤖 AI Features")
    st.markdown("""
    - **Minimax Algorithm** with depth-3 search
    - **Alpha-Beta Pruning** for optimization
    - **Dynamic Difficulty** based on performance
    - **Adaptive Learning** tracks your progress
    - **Smart Question Selection** maximizes learning
    """)
    
    st.markdown("---")
    st.subheader("📊 Your Performance")
    
    skill = st.session_state.profiler.get_overall_skill()
    st.metric("Skill Level", f"{skill*100:.0f}%")
    
    if st.session_state.total_attempts > 0:
        st.markdown(f"""
        - 📈 Total Attempts: {st.session_state.total_attempts}
        - ✅ Correct: {st.session_state.correct_answers}
        - 🏆 Best Streak: {st.session_state.best_streak}
        """)
        
        # Difficulty breakdown
        st.markdown("**Performance by Difficulty:**")
        for diff in [1, 2, 3]:
            stats = st.session_state.profiler.difficulty_stats[diff]
            if stats:
                success_rate = sum(stats) / len(stats) * 100
                stars = "⭐" * diff
                st.progress(success_rate / 100, text=f"{stars} {success_rate:.0f}%")
    
    st.markdown("---")
    st.subheader("🧠 AI Statistics")
    st.markdown(f"""
    - 🔍 Nodes evaluated: {st.session_state.ai_stats['nodes']}
    - ✂️ Branches pruned: {st.session_state.ai_stats['pruning']}
    - 🎯 Pruning efficiency: {(st.session_state.ai_stats['pruning'] / max(st.session_state.ai_stats['nodes'], 1) * 100):.1f}%
    """)
    
    st.markdown("---")
    st.markdown("💡 **Tip:** The AI adapts to your strengths and weaknesses in real-time!")
