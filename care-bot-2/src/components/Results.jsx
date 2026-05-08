import React from 'react';
import { getPHQ9Result } from '../questions';

const Results = ({ responses, totalScore, isPHQ9, onRestart, onTalkToAI }) => {
  const result = isPHQ9 ? getPHQ9Result(totalScore) : null;

  return (
    <div className="card results animate-slide">
      <h1>การประเมินเสร็จสิ้น</h1>
      <div className="score-display">{totalScore}</div>
      <p className="subtitle">คะแนนรวม ({isPHQ9 ? 'PHQ-9' : 'PHQ-2'})</p>
      
      {isPHQ9 ? (
        <>
          <div className="severity-badge">{result.severity}</div>
          <p className="action-text">{result.action}</p>
          
          <button className="talk-ai-btn" onClick={onTalkToAI}>
            ปรึกษา CareBot (AI)
          </button>
        </>
      ) : (
        <div style={{ marginBottom: '1rem' }}>
          <p className="action-text">
            {totalScore >= 3 
              ? 'คะแนนของคุณบ่งชี้ว่าอาจมีความเสี่ยง... กำลังดำเนินการทำแบบทดสอบ PHQ-9 ต่อไป' 
              : 'คะแนนของคุณอยู่ในเกณฑ์ปกติ ไม่พบความเสี่ยงของโรคซึมเศร้าในขณะนี้'}
          </p>
          {totalScore < 3 && (
            <button className="talk-ai-btn" onClick={onTalkToAI}>
              คุยเล่นกับ CareBot
            </button>
          )}
        </div>
      )}

      <div style={{ marginTop: '2rem', textAlign: 'left', fontSize: '1rem', color: 'var(--text-muted)' }}>
        <p><strong>หมายเหตุ:</strong> แบบประเมินนี้เป็นเพียงเครื่องมือคัดกรองเบื้องต้น ไม่ใช่การวินิจฉัยทางการแพทย์ โปรดปรึกษาแพทย์หรือผู้เชี่ยวชาญเพื่อรับการประเมินอย่างละเอียด</p>
      </div>

      <button className="restart-btn" onClick={onRestart} style={{ marginTop: '2rem', background: 'transparent', border: '2px solid var(--glass-border)', color: 'var(--text)' }}>
        ทำแบบประเมินอีกครั้ง
      </button>
    </div>
  );
};

export default Results;
