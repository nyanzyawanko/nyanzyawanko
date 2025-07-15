import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, Trophy, Clock, Calculator } from 'lucide-react';

const MentalMathApp = () => {
  const [currentOperation, setCurrentOperation] = useState('addition');
  const [currentLevel, setCurrentLevel] = useState('beginner');
  const [gameState, setGameState] = useState('menu'); // menu, playing, paused, finished
  const [problem, setProblem] = useState(null);
  const [userAnswer, setUserAnswer] = useState('');
  const [score, setScore] = useState(0);
  const [totalProblems, setTotalProblems] = useState(0);
  const [timeLeft, setTimeLeft] = useState(0);
  const [streak, setStreak] = useState(0);
  const [bestStreak, setBestStreak] = useState(0);
  const [feedback, setFeedback] = useState('');
  const [isCorrect, setIsCorrect] = useState(null);
  
  const timerRef = useRef(null);
  const inputRef = useRef(null);

  const operations = {
    addition: {
      name: '足し算',
      symbol: '+',
      levels: {
        beginner: { name: '初級 (1桁+1桁)', timeLimit: 5, generate: () => generateAddition(1, 1) },
        intermediate: { name: '中級 (2桁+2桁)', timeLimit: 15, generate: () => generateAddition(2, 2) },
        advanced: { name: '上級 (3桁+3桁)', timeLimit: 25, generate: () => generateAddition(3, 3) }
      }
    },
    subtraction: {
      name: '引き算',
      symbol: '-',
      levels: {
        beginner: { name: '初級 (1桁-1桁)', timeLimit: 5, generate: () => generateSubtraction(1, 1) },
        intermediate: { name: '中級 (2桁-2桁)', timeLimit: 15, generate: () => generateSubtraction(2, 2) },
        advanced: { name: '上級 (3桁-3桁)', timeLimit: 25, generate: () => generateSubtraction(3, 3) }
      }
    },
    multiplication: {
      name: '掛け算',
      symbol: '×',
      levels: {
        beginner: { name: '初級 (1桁×1桁)', timeLimit: 5, generate: () => generateMultiplication(1, 1) },
        intermediate: { name: '中級 (2桁×1桁)', timeLimit: 15, generate: () => generateMultiplication(2, 1) },
        advanced: { name: '上級 (2桁×2桁)', timeLimit: 25, generate: () => generateMultiplication(2, 2) }
      }
    },
    division: {
      name: '割り算',
      symbol: '÷',
      levels: {
        beginner: { name: '初級 (2桁÷1桁)', timeLimit: 10, generate: () => generateDivision(2, 1) },
        intermediate: { name: '中級 (3桁÷1桁)', timeLimit: 20, generate: () => generateDivision(3, 1) },
        advanced: { name: '上級 (3桁÷2桁)', timeLimit: 30, generate: () => generateDivision(3, 2) }
      }
    }
  };

  function generateNumber(digits) {
    const min = Math.pow(10, digits - 1);
    const max = Math.pow(10, digits) - 1;
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  function generateAddition(digits1, digits2) {
    const num1 = digits1 === 1 ? Math.floor(Math.random() * 9) + 1 : generateNumber(digits1);
    const num2 = digits2 === 1 ? Math.floor(Math.random() * 9) + 1 : generateNumber(digits2);
    return { num1, num2, answer: num1 + num2 };
  }

  function generateSubtraction(digits1, digits2) {
    const num1 = digits1 === 1 ? Math.floor(Math.random() * 9) + 1 : generateNumber(digits1);
    const num2 = digits2 === 1 ? Math.floor(Math.random() * Math.min(9, num1)) + 1 : 
                  Math.floor(Math.random() * num1) + 1;
    return { num1, num2, answer: num1 - num2 };
  }

  function generateMultiplication(digits1, digits2) {
    const num1 = digits1 === 1 ? Math.floor(Math.random() * 9) + 1 : generateNumber(digits1);
    const num2 = digits2 === 1 ? Math.floor(Math.random() * 9) + 1 : generateNumber(digits2);
    return { num1, num2, answer: num1 * num2 };
  }

  function generateDivision(dividendDigits, divisorDigits) {
    const divisor = divisorDigits === 1 ? Math.floor(Math.random() * 9) + 1 : generateNumber(divisorDigits);
    const quotient = dividendDigits === 2 ? Math.floor(Math.random() * 9) + 1 : generateNumber(dividendDigits - 1);
    const dividend = divisor * quotient;
    return { num1: dividend, num2: divisor, answer: quotient };
  }

  function generateProblem() {
    const currentConfig = operations[currentOperation].levels[currentLevel];
    const newProblem = currentConfig.generate();
    setProblem(newProblem);
    setTimeLeft(currentConfig.timeLimit);
    setUserAnswer('');
    setFeedback('');
    setIsCorrect(null);
  }

  function startGame() {
    setGameState('playing');
    setScore(0);
    setTotalProblems(0);
    setStreak(0);
    generateProblem();
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }

  function pauseGame() {
    setGameState('paused');
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
  }

  function resumeGame() {
    setGameState('playing');
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }

  function resetGame() {
    setGameState('menu');
    setScore(0);
    setTotalProblems(0);
    setStreak(0);
    setFeedback('');
    setIsCorrect(null);
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
  }

  function submitAnswer() {
    if (!userAnswer.trim()) return;

    const answer = parseInt(userAnswer);
    const correct = answer === problem.answer;
    
    setTotalProblems(prev => prev + 1);
    setIsCorrect(correct);
    
    if (correct) {
      setScore(prev => prev + 1);
      setStreak(prev => {
        const newStreak = prev + 1;
        setBestStreak(current => Math.max(current, newStreak));
        return newStreak;
      });
      setFeedback('正解！');
      
      setTimeout(() => {
        generateProblem();
        if (inputRef.current) {
          inputRef.current.focus();
        }
      }, 500);
    } else {
      setStreak(0);
      setFeedback(`不正解。正解は ${problem.answer} です。`);
      
      setTimeout(() => {
        generateProblem();
        if (inputRef.current) {
          inputRef.current.focus();
        }
      }, 1500);
    }
  }

  function handleKeyPress(e) {
    if (e.key === 'Enter') {
      submitAnswer();
    }
  }

  useEffect(() => {
    if (gameState === 'playing' && timeLeft > 0) {
      timerRef.current = setTimeout(() => {
        setTimeLeft(prev => prev - 1);
      }, 1000);
    } else if (gameState === 'playing' && timeLeft === 0) {
      setStreak(0);
      setTotalProblems(prev => prev + 1);
      setIsCorrect(false);
      setFeedback(`時間切れ！正解は ${problem.answer} です。`);
      
      setTimeout(() => {
        generateProblem();
        if (inputRef.current) {
          inputRef.current.focus();
        }
      }, 1500);
    }

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, [gameState, timeLeft, problem]);

  const currentConfig = operations[currentOperation].levels[currentLevel];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Calculator className="w-8 h-8 text-indigo-600" />
            <h1 className="text-4xl font-bold text-indigo-800">高速暗算アプリ</h1>
          </div>
          <p className="text-gray-600">制限時間内に正確に計算しよう！</p>
        </div>

        {gameState === 'menu' && (
          <div className="bg-white rounded-xl shadow-lg p-8">
            {/* Operation Selection */}
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">演算を選択</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(operations).map(([key, op]) => (
                  <button
                    key={key}
                    onClick={() => setCurrentOperation(key)}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      currentOperation === key
                        ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="text-2xl font-bold mb-2">{op.symbol}</div>
                    <div className="text-sm">{op.name}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Level Selection */}
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">難易度を選択</h2>
              <div className="space-y-3">
                {Object.entries(operations[currentOperation].levels).map(([key, level]) => (
                  <button
                    key={key}
                    onClick={() => setCurrentLevel(key)}
                    className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
                      currentLevel === key
                        ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="font-semibold">{level.name}</div>
                    <div className="text-sm text-gray-600">制限時間: {level.timeLimit}秒</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Start Button */}
            <button
              onClick={startGame}
              className="w-full bg-indigo-600 text-white py-4 rounded-lg font-semibold text-lg hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
            >
              <Play className="w-5 h-5" />
              ゲーム開始
            </button>
          </div>
        )}

        {gameState === 'playing' && (
          <div className="bg-white rounded-xl shadow-lg p-8">
            {/* Game Header */}
            <div className="flex justify-between items-center mb-8">
              <div className="flex items-center gap-4">
                <h2 className="text-xl font-bold text-gray-800">
                  {operations[currentOperation].name} - {currentConfig.name}
                </h2>
                <div className="flex items-center gap-2">
                  <Trophy className="w-5 h-5 text-yellow-500" />
                  <span className="font-semibold">{score}/{totalProblems}</span>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Clock className="w-5 h-5 text-red-500" />
                  <span className={`text-2xl font-bold ${timeLeft <= 3 ? 'text-red-500' : 'text-gray-800'}`}>
                    {timeLeft}
                  </span>
                </div>
                <button
                  onClick={pauseGame}
                  className="bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 transition-colors flex items-center gap-2"
                >
                  <Pause className="w-4 h-4" />
                  一時停止
                </button>
              </div>
            </div>

            {/* Problem Display */}
            {problem && (
              <div className="text-center mb-8">
                <div className="text-6xl font-bold text-gray-800 mb-4">
                  {problem.num1} {operations[currentOperation].symbol} {problem.num2} = ?
                </div>
                <div className="max-w-xs mx-auto">
                  <input
                    ref={inputRef}
                    type="number"
                    value={userAnswer}
                    onChange={(e) => setUserAnswer(e.target.value)}
                    onKeyPress={handleKeyPress}
                    className="w-full text-4xl text-center border-2 border-gray-300 rounded-lg py-4 focus:border-indigo-500 focus:outline-none"
                    placeholder="答え"
                  />
                </div>
                <button
                  onClick={submitAnswer}
                  disabled={!userAnswer.trim()}
                  className="mt-4 bg-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  回答する
                </button>
              </div>
            )}

            {/* Feedback */}
            {feedback && (
              <div className={`text-center text-xl font-semibold mb-4 ${
                isCorrect === true ? 'text-green-600' : 'text-red-600'
              }`}>
                {feedback}
              </div>
            )}

            {/* Stats */}
            <div className="flex justify-center gap-8 text-center">
              <div>
                <div className="text-2xl font-bold text-indigo-600">{streak}</div>
                <div className="text-sm text-gray-600">連続正解</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-purple-600">{bestStreak}</div>
                <div className="text-sm text-gray-600">最高連続</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">
                  {totalProblems > 0 ? Math.round((score / totalProblems) * 100) : 0}%
                </div>
                <div className="text-sm text-gray-600">正解率</div>
              </div>
            </div>
          </div>
        )}

        {gameState === 'paused' && (
          <div className="bg-white rounded-xl shadow-lg p-8 text-center">
            <h2 className="text-3xl font-bold text-gray-800 mb-4">一時停止中</h2>
            <p className="text-gray-600 mb-8">準備ができたら再開してください</p>
            <div className="flex justify-center gap-4">
              <button
                onClick={resumeGame}
                className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors flex items-center gap-2"
              >
                <Play className="w-5 h-5" />
                再開
              </button>
              <button
                onClick={resetGame}
                className="bg-gray-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-600 transition-colors flex items-center gap-2"
              >
                <RotateCcw className="w-5 h-5" />
                メニューに戻る
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MentalMathApp;