import React from 'react';

const QuestionCard = ({ question, onSelect, selectedValue }) => {
  return (
    <div className="card animate-slide">
      <h2 className="question-text">{question.text}</h2>
      <div className="options-grid">
        {question.options.map((option) => (
          <button
            key={option.value}
            className={`option-btn ${selectedValue === option.value ? 'selected' : ''}`}
            onClick={() => onSelect(option.value)}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuestionCard;
