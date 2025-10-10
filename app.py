<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐸 Frog & Treasure Island</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background: linear-gradient(to bottom, #87CEEB 0%, #4A90E2 50%, #2E5C8A 100%);
            min-height: 100vh;
            overflow-x: hidden;
        }

        .game-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            color: white;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
            margin-bottom: 20px;
        }

        .header h1 {
            font-size: 48px;
            margin-bottom: 10px;
        }

        .stats {
            display: flex;
            justify-content: space-around;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            padding: 15px 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            text-align: center;
            min-width: 120px;
        }

        .stat-value {
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
        }

        .stat-label {
            font-size: 14px;
            color: #7f8c8d;
            margin-top: 5px;
        }

        .island {
            background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
            padding: 20px 40px;
            border-radius: 50% 50% 0 0;
            text-align: center;
            margin: 0 auto 40px;
            width: fit-content;
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            position: relative;
        }

        .island::before {
            content: '🌴';
            position: absolute;
            left: 10px;
            top: 10px;
            font-size: 30px;
        }

        .island::after {
            content: '🌴';
            position: absolute;
            right: 10px;
            top: 10px;
            font-size: 30px;
        }

        .treasure {
            font-size: 48px;
            animation: bounce 2s infinite;
        }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        .progress-bar {
            width: 100%;
            height: 30px;
            background: rgba(255,255,255,0.3);
            border-radius: 15px;
            overflow: hidden;
            margin-bottom: 30px;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.2);
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #2ecc71, #27ae60);
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }

        .lake {
            background: linear-gradient(to bottom, rgba(52, 152, 219, 0.6), rgba(41, 128, 185, 0.8));
            padding: 40px 20px;
            border-radius: 30px;
            min-height: 400px;
            position: relative;
            box-shadow: inset 0 5px 20px rgba(0,0,0,0.2);
        }

        .question-card {
            background: rgba(0, 0, 0, 0.8);
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        }

        .question-word {
            font-size: 48px;
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

        .difficulty {
            color: #e67e22;
            font-size: 18px;
        }

        .lily-pads {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 30px;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }

        .lily-pad {
            background: radial-gradient(circle, #2ecc71 0%, #27ae60 70%, #1e8449 100%);
            border: 5px solid #196f3d;
            border-radius: 50%;
            width: 200px;
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 8px 20px rgba(0,0,0,0.3), inset 0 -5px 10px rgba(0,0,0,0.2);
            position: relative;
            margin: 0 auto;
        }

        .lily-pad::before {
            content: '';
            position: absolute;
            width: 60%;
            height: 60%;
            background: radial-gradient(circle, rgba(255,255,255,0.2), transparent);
            border-radius: 50%;
            top: 10%;
            left: 20%;
        }

        .lily-pad:hover {
            transform: translateY(-10px) scale(1.05);
            box-shadow: 0 15px 35px rgba(0,0,0,0.4);
            border-color: #f39c12;
        }

        .lily-pad-text {
            color: white;
            font-size: 18px;
            font-weight: bold;
            text-align: center;
            padding: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            z-index: 1;
        }

        .frog {
            font-size: 60px;
            position: absolute;
            transition: all 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            z-index: 10;
            filter: drop-shadow(0 5px 10px rgba(0,0,0,0.4));
        }

        .feedback {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 40px 60px;
            border-radius: 20px;
            box-shadow: 0 10px 50px rgba(0,0,0,0.5);
            text-align: center;
            z-index: 1000;
            animation: popIn 0.3s ease-out;
        }

        @keyframes popIn {
            0% { transform: translate(-50%, -50%) scale(0.5); opacity: 0; }
            100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
        }

        .feedback h2 {
            font-size: 36px;
            margin-bottom: 15px;
        }

        .feedback.correct h2 { color: #27ae60; }
        .feedback.wrong h2 { color: #e74c3c; }

        .feedback-definition {
            font-size: 18px;
            color: #2c3e50;
            margin: 15px 0;
            padding: 15px;
            background: #ecf0f1;
            border-radius: 10px;
        }

        .feedback-bonus {
            font-size: 16px;
            color: #7f8c8d;
            margin-top: 10px;
        }

        .next-btn {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 25px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s;
        }

        .next-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }

        .game-over {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 2000;
        }

        .game-over-content {
            background: white;
            padding: 50px;
            border-radius: 30px;
            text-align: center;
            max-width: 500px;
        }

        .game-over-content h1 {
            font-size: 48px;
            margin-bottom: 20px;
        }

        .restart-btn {
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            color: white;
            border: none;
            padding: 20px 50px;
            border-radius: 30px;
            font-size: 20px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
            transition: all 0.3s;
        }

        .restart-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.4);
        }

        @media (max-width: 768px) {
            .lily-pads {
                grid-template-columns: 1fr;
                gap: 20px;
            }
            .lily-pad {
                width: 180px;
                height: 180px;
            }
            .question-word {
                font-size: 36px;
            }
        }
    </style>
</head>
<body>
    <div class="game-container">
        <div class="header">
            <h1>🐸 Frog & Treasure Island 🏝️</h1>
            <p>Jump to the correct meaning!</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="lives">❤️❤️❤️</div>
                <div class="stat-label">Lives</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="score">0</div>
                <div class="stat-label">Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="level">1/10</div>
                <div class="stat-label">Level</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="streak">🔥 0</div>
                <div class="stat-label">Streak</div>
            </div>
        </div>

        <div class="island">
            <div class="treasure">💎</div>
        </div>

        <div class="progress-bar">
            <div class="progress-fill" id="progress" style="width: 0%">
                <span id="progress-text">Start!</span>
            </div>
        </div>

        <div class="lake">
            <div class="question-card" id="questionCard">
                <div class="question-word" id="word">Loading...</div>
                <div class="question-prompt">Choose the correct meaning:</div>
                <div class="difficulty" id="difficulty"></div>
            </div>

            <div class="lily-pads" id="lilyPads"></div>
            
            <div class="frog" id="frog" style="bottom: 20px; left: 50%; transform: translateX(-50%);">🐸</div>
        </div>
    </div>

    <script>
        const QUESTIONS = [
            {word: "Ephemeral", meaning: "Short-lived", distractors: ["Eternal", "Permanent", "Long-lasting"], difficulty: 1},
            {word: "Ubiquitous", meaning: "Everywhere", distractors: ["Rare", "Unique", "Absent"], difficulty: 2},
            {word: "Serendipity", meaning: "Lucky discovery", distractors: ["Bad luck", "Planning", "Disaster"], difficulty: 2},
            {word: "Perspicacious", meaning: "Keen insight", distractors: ["Foolish", "Confused", "Ignorant"], difficulty: 3},
            {word: "Ameliorate", meaning: "Make better", distractors: ["Worsen", "Destroy", "Ruin"], difficulty: 2},
            {word: "Cacophony", meaning: "Harsh sounds", distractors: ["Harmony", "Silence", "Melody"], difficulty: 2},
            {word: "Esoteric", meaning: "Specialized", distractors: ["Common", "Popular", "Universal"], difficulty: 3},
            {word: "Loquacious", meaning: "Talkative", distractors: ["Silent", "Brief", "Quiet"], difficulty: 1},
            {word: "Magnanimous", meaning: "Generous", distractors: ["Petty", "Selfish", "Cruel"], difficulty: 2},
            {word: "Perfidious", meaning: "Untrustworthy", distractors: ["Loyal", "Honest", "Faithful"], difficulty: 3},
            {word: "Sanguine", meaning: "Optimistic", distractors: ["Pessimistic", "Gloomy", "Sad"], difficulty: 2},
            {word: "Tenacious", meaning: "Persistent", distractors: ["Weak", "Quitting", "Lazy"], difficulty: 1},
            {word: "Verbose", meaning: "Wordy", distractors: ["Concise", "Brief", "Short"], difficulty: 1},
            {word: "Zealous", meaning: "Enthusiastic", distractors: ["Apathetic", "Indifferent", "Lazy"], difficulty: 2},
            {word: "Benevolent", meaning: "Kind", distractors: ["Cruel", "Mean", "Hostile"], difficulty: 1},
            {word: "Enigmatic", meaning: "Mysterious", distractors: ["Clear", "Obvious", "Plain"], difficulty: 2},
            {word: "Resilient", meaning: "Strong recovery", distractors: ["Fragile", "Weak", "Delicate"], difficulty: 2},
            {word: "Obsequious", meaning: "Overly obedient", distractors: ["Defiant", "Independent", "Proud"], difficulty: 3},
        ];

        let gameState = {
            level: 1,
            lives: 3,
            score: 0,
            streak: 0,
            bestStreak: 0,
            usedQuestions: new Set(),
            currentQuestion: null,
            difficulty_stats: {1: [], 2: [], 3: []},
            recent_performance: []
        };

        function getSkillLevel() {
            if (gameState.recent_performance.length === 0) return 0.5;
            return gameState.recent_performance.reduce((a, b) => a + b, 0) / gameState.recent_performance.length;
        }

        function selectQuestion() {
            const available = QUESTIONS.filter(q => !gameState.usedQuestions.has(q.word));
            if (available.length === 0) {
                gameState.usedQuestions.clear();
                return QUESTIONS[Math.floor(Math.random() * QUESTIONS.length)];
            }

            const skill = getSkillLevel();
            let preferred;
            
            if (skill < 0.4) {
                preferred = available.filter(q => q.difficulty <= 2);
            } else if (skill > 0.7) {
                preferred = available.filter(q => q.difficulty >= 2);
            } else {
                preferred = available;
            }

            if (preferred.length === 0) preferred = available;
            
            return preferred[Math.floor(Math.random() * preferred.length)];
        }

        function setupQuestion() {
            const question = selectQuestion();
            gameState.currentQuestion = question;
            gameState.usedQuestions.add(question.word);
            gameState.startTime = Date.now();

            document.getElementById('word').textContent = question.word;
            document.getElementById('difficulty').textContent = '⭐'.repeat(question.difficulty);

            const options = [question.meaning, ...question.distractors];
            shuffle(options);

            const lilyPads = document.getElementById('lilyPads');
            lilyPads.innerHTML = '';

            options.forEach((option, idx) => {
                const pad = document.createElement('div');
                pad.className = 'lily-pad';
                pad.innerHTML = `<div class="lily-pad-text">${option}</div>`;
                pad.onclick = () => handleAnswer(option);
                lilyPads.appendChild(pad);
            });

            updateUI();
        }

        function handleAnswer(selected) {
            const question = gameState.currentQuestion;
            const isCorrect = selected === question.meaning;
            const responseTime = (Date.now() - gameState.startTime) / 1000;

            gameState.difficulty_stats[question.difficulty].push(isCorrect ? 1 : 0);
            gameState.recent_performance.push(isCorrect ? 1 : 0);
            if (gameState.recent_performance.length > 8) gameState.recent_performance.shift();

            let feedbackHTML = '';
            
            if (isCorrect) {
                gameState.streak++;
                gameState.bestStreak = Math.max(gameState.bestStreak, gameState.streak);
                
                const baseScore = question.difficulty * 10;
                const timeBonus = Math.max(0, Math.floor(baseScore * 0.5 * (1 - Math.min(responseTime / 15, 1))));
                const streakBonus = Math.min(gameState.streak * 2, 20);
                const totalScore = baseScore + timeBonus + streakBonus;
                
                gameState.score += totalScore;
                gameState.level++;

                feedbackHTML = `
                    <div class="feedback correct">
                        <h2>✅ Correct!</h2>
                        <div class="feedback-definition">
                            <strong>${question.word}</strong> = ${question.meaning}
                        </div>
                        <div class="feedback-bonus">
                            +${totalScore} points (Base: ${baseScore} + Speed: ${timeBonus} + Streak: ${streakBonus})
                        </div>
                        <button class="next-btn" onclick="nextQuestion()">Continue →</button>
                    </div>
                `;

                if (gameState.level > 10) {
                    showGameOver(true);
                    return;
                }
            } else {
                gameState.lives--;
                gameState.streak = 0;

                feedbackHTML = `
                    <div class="feedback wrong">
                        <h2>❌ Wrong!</h2>
                        <div class="feedback-definition">
                            <strong>${question.word}</strong> = ${question.meaning}
                        </div>
                        <div class="feedback-bonus">
                            You selected: ${selected}
                        </div>
                        <button class="next-btn" onclick="nextQuestion()">Continue →</button>
                    </div>
                `;

                if (gameState.lives <= 0) {
                    setTimeout(() => showGameOver(false), 1500);
                }
            }

            document.body.insertAdjacentHTML('beforeend', feedbackHTML);
            updateUI();
        }

        function nextQuestion() {
            document.querySelector('.feedback')?.remove();
            if (gameState.lives > 0 && gameState.level <= 10) {
                setupQuestion();
            }
        }

        function updateUI() {
            document.getElementById('lives').textContent = '❤️'.repeat(gameState.lives);
            document.getElementById('score').textContent = gameState.score;
            document.getElementById('level').textContent = `${gameState.level}/10`;
            document.getElementById('streak').textContent = `🔥 ${gameState.streak}`;
            
            const progress = ((gameState.level - 1) / 10) * 100;
            document.getElementById('progress').style.width = progress + '%';
            document.getElementById('progress-text').textContent = `${Math.round(progress)}% to treasure!`;
        }

        function showGameOver(victory) {
            const html = `
                <div class="game-over">
                    <div class="game-over-content">
                        <h1>${victory ? '🎉 Victory! 🎉' : '💀 Game Over'}</h1>
                        <p style="font-size: 24px; margin: 20px 0;">
                            ${victory ? 'You reached the treasure!' : 'The frog didn\'t make it...'}
                        </p>
                        <p style="font-size: 20px;"><strong>Final Score:</strong> ${gameState.score}</p>
                        <p style="font-size: 18px;"><strong>Best Streak:</strong> ${gameState.bestStreak}</p>
                        <button class="restart-btn" onclick="location.reload()">🔄 Play Again</button>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', html);
        }

        function shuffle(array) {
            for (let i = array.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [array[i], array[j]] = [array[j], array[i]];
            }
        }

        // Start game
        setupQuestion();
    </script>
</body>
</html>
