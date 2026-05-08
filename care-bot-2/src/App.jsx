import React, { useState, useEffect } from 'react';
import { PHQ2_QUESTIONS, PHQ9_QUESTIONS } from './questions';
import QuestionCard from './components/QuestionCard';
import Results from './components/Results';
import ChatView from './components/ChatView';

function App() {
  const [currentStep, setCurrentStep] = useState('PHQ2'); // 'PHQ2' | 'PHQ9' | 'RESULTS' | 'CHAT'
  const [currentIndex, setCurrentIndex] = useState(0);
  const [responses, setResponses] = useState({});
  const [totalScore, setTotalScore] = useState(0);

  const questions = currentStep === 'PHQ2' ? PHQ2_QUESTIONS : PHQ9_QUESTIONS;

  const handleSelect = (value) => {
    const qId = questions[currentIndex].id;
    const newResponses = { ...responses, [qId]: value };
    setResponses(newResponses);

    const currentScore = Object.values(newResponses).reduce((sum, v) => sum + v, 0);
    setTotalScore(currentScore);

    setTimeout(() => {
      if (currentIndex < questions.length - 1) {
        setCurrentIndex(currentIndex + 1);
      } else {
        handleStepCompletion(currentScore);
      }
    }, 400);
  };

  const handleStepCompletion = (score) => {
    if (currentStep === 'PHQ2') {
      if (score >= 3) {
        setCurrentStep('PHQ9');
        setCurrentIndex(0);
      } else {
        setCurrentStep('RESULTS');
      }
    } else {
      setCurrentStep('RESULTS');
      // Send data to backend
      fetch('http://localhost:8000/save-assessment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'PHQ-9',
          score: score,
          responses: responses
        })
      }).catch(err => console.error('Failed to save assessment:', err));
    }
  };

  const reset = () => {
    setCurrentStep('PHQ2');
    setCurrentIndex(0);
    setResponses({});
    setTotalScore(0);
  };

  const goToChat = () => {
    setCurrentStep('CHAT');
  };

  const backToResults = () => {
    setCurrentStep('RESULTS');
  };

  const getSubtitle = () => {
    if (currentStep === 'RESULTS') return 'ผลการประเมินของคุณ';
    if (currentStep === 'CHAT') return 'ห้องสนทนากับ CareBot';
    return `คำถามที่ ${currentIndex + 1} จาก ${questions.length}`;
  };

  return (
    <div className="container">
      <header>
        <h1>แบบประเมินสุขภาพจิต (CareBot)</h1>
        <p className="subtitle">{getSubtitle()}</p>
      </header>

      {currentStep === 'PHQ2' || currentStep === 'PHQ9' ? (
        <>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
            ></div>
          </div>
          <QuestionCard
            key={`${currentStep}-${currentIndex}`}
            question={questions[currentIndex]}
            onSelect={handleSelect}
            selectedValue={responses[questions[currentIndex].id]}
          />
        </>
      ) : currentStep === 'RESULTS' ? (
        <Results 
          responses={responses} 
          totalScore={totalScore} 
          isPHQ9={Object.keys(responses).length > 2} 
          onRestart={reset}
          onTalkToAI={goToChat}
        />
      ) : (
        <ChatView 
          totalScore={totalScore} 
          isPHQ9={Object.keys(responses).length > 2} 
          onBack={backToResults}
        />
      )}
      
      <footer style={{ marginTop: '2rem', textAlign: 'center', fontSize: '1rem', color: 'var(--text-muted)' }}>
        © {new Date().getFullYear()} CareBot Health. สงวนลิขสิทธิ์
      </footer>
    </div>
  );
}

export default App;
