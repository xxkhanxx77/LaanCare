import React, { useState, useEffect, useRef } from 'react';
import { getPHQ9Result } from '../questions';

const ChatView = ({ totalScore, isPHQ9, onBack }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    const result = isPHQ9 ? getPHQ9Result(totalScore) : null;
    let initialText = 'สวัสดีครับ ผม CareBot ยินดีที่ได้คุยด้วยครับ วันนี้คุณรู้สึกอย่างไรบ้างครับ?';
    
    if (isPHQ9) {
      if (totalScore >= 10) {
        initialText = `ผมเห็นผลคะแนนของคุณอยู่ที่ ${totalScore} คะแนน ซึ่งอยู่ในระดับ${result.severity} ผมอยากให้คุณรู้ว่าผมพร้อมรับฟังคุณเสมอ มีอะไรที่อยากระบายหรือเล่าให้ฟังไหมครับ?`;
      } else {
        initialText = `ดีใจด้วยครับที่คุณมีคะแนนสุขภาพจิตอยู่ในเกณฑ์ดี (${totalScore} คะแนน) มีเคล็ดลับอะไรในการดูแลใจตัวเองมาแชร์กับผมไหมครับ?`;
      }
    }

    setMessages([
      { id: 1, text: initialText, sender: 'ai' }
    ]);
  }, [totalScore, isPHQ9]);

  useEffect(scrollToBottom, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { id: Date.now(), text: input, sender: 'user' };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const result = isPHQ9 ? getPHQ9Result(totalScore) : { severity: 'Normal', action: 'None' };
      
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          history: messages.map(m => ({ role: m.sender, text: m.text })),
          context: {
            severity: result.severity,
            score: totalScore.toString(),
            action: result.action
          }
        })
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to connect to server');

      const aiResponse = {
        id: Date.now() + 1,
        text: data.response,
        sender: 'ai'
      };
      setMessages((prev) => [...prev, aiResponse]);
    } catch (error) {
      console.error('Chat Error:', error);
      const errorResponse = {
        id: Date.now() + 1,
        text: 'ขออภัยครับ ดูเหมือนผมจะมีปัญหาในการเชื่อมต่อ โปรดลองอีกครั้งในภายหลังนะครับ',
        sender: 'ai'
      };
      setMessages((prev) => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="animate-slide">
      <div className="chat-container">
        <div className="chat-messages">
          {messages.map((msg) => (
            <div key={msg.id} className={`message ${msg.sender}`}>
              {msg.text}
            </div>
          ))}
          {isLoading && (
            <div className="message ai" style={{ fontStyle: 'italic', opacity: 0.7 }}>
              CareBot กำลังคิด...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        <form className="chat-input-area" onSubmit={handleSend}>
          <input
            type="text"
            className="chat-input"
            placeholder={isLoading ? "กำลังรอคำตอบ..." : "พิมพ์ข้อความที่นี่..."}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
          />
          <button type="submit" className="send-btn" disabled={isLoading}>
            {isLoading ? '...' : 'ส่ง'}
          </button>
        </form>
      </div>
      
      <button className="restart-btn" onClick={onBack} style={{ marginTop: '1.5rem', background: 'transparent', border: '2px solid var(--glass-border)', color: 'var(--text)' }}>
        กลับไปหน้าผลสรุป
      </button>
    </div>
  );
};

export default ChatView;
