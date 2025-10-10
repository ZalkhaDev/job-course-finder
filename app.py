import pygame
import json
import math
import random
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Colors
WATER_BLUE = (52, 152, 219)
LILY_GREEN = (46, 204, 113)
LILY_WRONG = (231, 76, 60)
LILY_CORRECT = (39, 174, 96)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (241, 196, 15)
SKY_BLUE = (135, 206, 235)

# Game Settings
MAX_LIVES = 3
TOTAL_LEVELS = 10
NUM_OPTIONS = 4

@dataclass
class Question:
    word: str
    meaning: str
    distractors: List[str]
    difficulty: int  # 1=easy, 2=medium, 3=hard
    
@dataclass
class GameState:
    level: int
    lives: int
    score: int
    correct_answers: int
    total_attempts: int
    
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
    """AI Question Master using Minimax with Alpha-Beta Pruning"""
    def __init__(self, questions: List[Question], profiler: PlayerProfiler):
        self.questions = questions
        self.profiler = profiler
        self.max_depth = 2
        
    def evaluate_state(self, state: GameState, question: Question) -> float:
        """Heuristic evaluation function"""
        success_prob = self.profiler.get_success_probability(question.difficulty)
        
        # AI wants to challenge player (minimize player's expected score)
        difficulty_factor = question.difficulty / 3.0
        progress_penalty = state.level / TOTAL_LEVELS
        lives_factor = state.lives / MAX_LIVES
        
        # Lower score is better for AI (harder for player)
        score = -(success_prob * 10) + (difficulty_factor * 5) - (progress_penalty * 3)
        
        return score
    
    def minimax(self, state: GameState, depth: int, alpha: float, beta: float, 
                maximizing_player: bool, available_questions: List[Question]) -> Tuple[float, Optional[Question]]:
        """Minimax with Alpha-Beta Pruning"""
        if depth == 0 or not available_questions:
            return 0, None
        
        if maximizing_player:  # AI's turn (actually minimizing player success)
            max_eval = float('-inf')
            best_question = None
            
            for question in available_questions:
                eval_score = self.evaluate_state(state, question)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_question = question
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Alpha-Beta pruning
            
            return max_eval, best_question
        
    def select_question(self, state: GameState, used_questions: set) -> Question:
        """Select the best question using Minimax"""
        available = [q for q in self.questions if id(q) not in used_questions]
        
        if not available:
            return random.choice(self.questions)
        
        # Adjust available questions based on player skill
        skill = self.profiler.get_overall_skill()
        
        # Filter questions by appropriate difficulty
        if skill < 0.4:
            preferred = [q for q in available if q.difficulty <= 2]
        elif skill > 0.7:
            preferred = [q for q in available if q.difficulty >= 2]
        else:
            preferred = available
        
        if not preferred:
            preferred = available
        
        _, best_question = self.minimax(state, self.max_depth, float('-inf'), 
                                       float('inf'), True, preferred[:8])
        
        return best_question if best_question else random.choice(preferred)

class Frog:
    """Player character"""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.jumping = False
        self.jump_progress = 0
        self.size = 40
        
    def jump_to(self, x: int, y: int):
        self.target_x = x
        self.target_y = y
        self.jumping = True
        self.jump_progress = 0
    
    def update(self):
        if self.jumping:
            self.jump_progress += 0.08
            if self.jump_progress >= 1:
                self.x = self.target_x
                self.y = self.target_y
                self.jumping = False
                self.jump_progress = 0
            else:
                # Smooth interpolation with arc
                t = self.jump_progress
                self.x = self.x + (self.target_x - self.x) * t
                arc_height = math.sin(t * math.pi) * 80
                self.y = self.y + (self.target_y - self.y) * t - arc_height
    
    def draw(self, screen):
        # Simple frog representation
        pygame.draw.circle(screen, (34, 139, 34), (int(self.x), int(self.y)), self.size)
        # Eyes
        pygame.draw.circle(screen, WHITE, (int(self.x - 12), int(self.y - 8)), 8)
        pygame.draw.circle(screen, WHITE, (int(self.x + 12), int(self.y - 8)), 8)
        pygame.draw.circle(screen, BLACK, (int(self.x - 12), int(self.y - 8)), 4)
        pygame.draw.circle(screen, BLACK, (int(self.x + 12), int(self.y - 8)), 4)

class LilyPad:
    """Answer option lily pad"""
    def __init__(self, x: int, y: int, text: str, is_correct: bool):
        self.x = x
        self.y = y
        self.text = text
        self.is_correct = is_correct
        self.radius = 60
        self.color = LILY_GREEN
        self.hover = False
        
    def contains_point(self, x: int, y: int) -> bool:
        dist = math.sqrt((x - self.x)**2 + (y - self.y)**2)
        return dist <= self.radius
    
    def draw(self, screen, font):
        color = self.color
        if self.hover:
            color = tuple(min(c + 30, 255) for c in color)
        
        pygame.draw.circle(screen, color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, (30, 100, 70), (self.x, self.y), self.radius, 3)
        
        # Draw text (wrapped if needed)
        words = self.text.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            test_text = ' '.join(current_line)
            if font.size(test_text)[0] > self.radius * 1.6:
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(test_text)
                    current_line = []
        if current_line:
            lines.append(' '.join(current_line))
        
        y_offset = self.y - (len(lines) * 10)
        for line in lines:
            text_surf = font.render(line, True, WHITE)
            text_rect = text_surf.get_rect(center=(self.x, y_offset))
            screen.blit(text_surf, text_rect)
            y_offset += 20

class FrogGame:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🐸 Frog & Treasure Island")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.title_font = pygame.font.Font(None, 48)
        
        # Load questions
        self.questions = self.load_questions()
        
        # Game components
        self.profiler = PlayerProfiler()
        self.ai = MinimaxAI(self.questions, self.profiler)
        self.state = GameState(1, MAX_LIVES, 0, 0, 0)
        self.used_questions = set()
        
        # Game objects
        self.frog = Frog(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.lily_pads = []
        self.current_question = None
        
        # Game flow
        self.waiting_for_answer = False
        self.feedback_timer = 0
        self.game_over = False
        self.victory = False
        
        self.setup_level()
    
    def load_questions(self) -> List[Question]:
        """Load or create vocabulary questions"""
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
        ]
    
    def setup_level(self):
        """Setup a new level with question and lily pads"""
        self.current_question = self.ai.select_question(self.state, self.used_questions)
        self.used_questions.add(id(self.current_question))
        
        # Create answer options
        options = [self.current_question.meaning] + self.current_question.distractors
        random.shuffle(options)
        
        # Position lily pads
        self.lily_pads = []
        y_pos = SCREEN_HEIGHT - 300
        spacing = SCREEN_WIDTH // (NUM_OPTIONS + 1)
        
        for i, option in enumerate(options):
            x_pos = spacing * (i + 1)
            is_correct = (option == self.current_question.meaning)
            lily_pad = LilyPad(x_pos, y_pos, option, is_correct)
            self.lily_pads.append(lily_pad)
        
        self.waiting_for_answer = True
    
    def handle_answer(self, lily_pad: LilyPad):
        """Process player's answer"""
        self.state.total_attempts += 1
        
        if lily_pad.is_correct:
            self.state.correct_answers += 1
            self.state.score += 10 * self.current_question.difficulty
            self.state.level += 1
            lily_pad.color = LILY_CORRECT
            self.profiler.update_performance(self.current_question.difficulty, True)
            
            # Move frog to lily pad
            self.frog.jump_to(lily_pad.x, lily_pad.y)
            
            if self.state.level > TOTAL_LEVELS:
                self.victory = True
                self.game_over = True
        else:
            self.state.lives -= 1
            lily_pad.color = LILY_WRONG
            self.profiler.update_performance(self.current_question.difficulty, False)
            
            # Show correct answer
            for lp in self.lily_pads:
                if lp.is_correct:
                    lp.color = LILY_CORRECT
            
            if self.state.lives <= 0:
                self.game_over = True
        
        self.waiting_for_answer = False
        self.feedback_timer = 90  # 1.5 seconds at 60 FPS
    
    def draw(self):
        """Render the game"""
        # Sky/water background
        self.screen.fill(SKY_BLUE)
        pygame.draw.rect(self.screen, WATER_BLUE, (0, SCREEN_HEIGHT - 400, SCREEN_WIDTH, 400))
        
        # Draw treasure island at top
        if not self.game_over:
            island_y = 50
            pygame.draw.ellipse(self.screen, (139, 69, 19), 
                              (SCREEN_WIDTH - 200, island_y - 20, 150, 60))
            treasure_text = self.font.render("🏝️ TREASURE", True, GOLD)
            self.screen.blit(treasure_text, (SCREEN_WIDTH - 180, island_y))
        
        # Draw lily pads
        for lily_pad in self.lily_pads:
            lily_pad.draw(self.screen, self.font)
        
        # Draw frog
        self.frog.draw(self.screen)
        
        # Draw question
        if self.current_question and not self.game_over:
            question_text = f"What does '{self.current_question.word}' mean?"
            text_surf = self.title_font.render(question_text, True, WHITE)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
            pygame.draw.rect(self.screen, (0, 0, 0, 128), 
                           text_rect.inflate(40, 20))
            self.screen.blit(text_surf, text_rect)
        
        # Draw HUD
        lives_text = self.font.render(f"Lives: {'❤️' * self.state.lives}", True, WHITE)
        score_text = self.font.render(f"Score: {self.state.score}", True, WHITE)
        level_text = self.font.render(f"Level: {self.state.level}/{TOTAL_LEVELS}", True, WHITE)
        
        self.screen.blit(lives_text, (20, 20))
        self.screen.blit(score_text, (20, 50))
        self.screen.blit(level_text, (20, 80))
        
        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            if self.victory:
                title = self.title_font.render("🎉 VICTORY! 🎉", True, GOLD)
                msg = self.font.render(f"You reached the treasure! Score: {self.state.score}", True, WHITE)
            else:
                title = self.title_font.render("Game Over", True, WHITE)
                msg = self.font.render(f"Final Score: {self.state.score}", True, WHITE)
            
            accuracy = (self.state.correct_answers / self.state.total_attempts * 100) if self.state.total_attempts > 0 else 0
            stats = self.font.render(f"Accuracy: {accuracy:.1f}%", True, WHITE)
            restart = self.font.render("Press SPACE to play again", True, GOLD)
            
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 250)))
            self.screen.blit(msg, msg.get_rect(center=(SCREEN_WIDTH // 2, 320)))
            self.screen.blit(stats, stats.get_rect(center=(SCREEN_WIDTH // 2, 360)))
            self.screen.blit(restart, restart.get_rect(center=(SCREEN_WIDTH // 2, 420)))
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.game_over:
                        # Restart game
                        self.__init__()
                
                elif event.type == pygame.MOUSEMOTION:
                    mx, my = event.pos
                    for lily_pad in self.lily_pads:
                        lily_pad.hover = lily_pad.contains_point(mx, my)
                
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    if self.waiting_for_answer and not self.frog.jumping:
                        mx, my = event.pos
                        for lily_pad in self.lily_pads:
                            if lily_pad.contains_point(mx, my):
                                self.handle_answer(lily_pad)
                                break
            
            # Update
            self.frog.update()
            
            if self.feedback_timer > 0:
                self.feedback_timer -= 1
                if self.feedback_timer == 0 and not self.game_over:
                    self.setup_level()
            
            # Draw
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

# Run the game
if __name__ == "__main__":
    game = FrogGame()
    game.run()
