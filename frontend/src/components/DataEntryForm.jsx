import React, { useState, useContext } from 'react';
import { addWorkoutLog, addInbodyRecord } from '../services/api';
import { RefreshContext } from '../contexts/RefreshContext';

const DataEntryForm = () => {
  const [activeTab, setActiveTab] = useState('workout');
  const [message, setMessage] = useState({ type: '', content: '' });
  const { triggerRefresh } = useContext(RefreshContext); // Context에서 새로고침 함수 가져오기

  // Workout Log State
  const [workoutLog, setWorkoutLog] = useState({
    date: new Date().toISOString().split('T')[0],
    exercise_name: '',
    set_type: '본세트',
    set_num: '1',
    weight: 0,
    reps_or_time: 0,
    unit: '회',
  });

  // InBody State
  const [inbodyRecord, setInbodyRecord] = useState({
    date: new Date().toISOString().split('T')[0],
    weight: 0,
    muscle_mass: 0,
    fat_percent: 0,
  });

  const handleWorkoutChange = (e) => {
    const { name, value } = e.target;
    setWorkoutLog({ ...workoutLog, [name]: value });
  };

  const handleInbodyChange = (e) => {
    const { name, value } = e.target;
    setInbodyRecord({ ...inbodyRecord, [name]: value });
  };

  // Generic submit handler to reduce code duplication
  const handleSubmit = async (e, apiFunc, data, successMessage) => {
    e.preventDefault();
    try {
      await apiFunc(data);
      setMessage({ type: 'success', content: successMessage });
      triggerRefresh(); // 데이터 제출 성공 시 새로고침 트리거
    } catch (error) {
      setMessage({ type: 'error', content: `오류: ${error.response?.data?.detail || error.message}` });
    }
  };

  return (
    <div className="data-entry-form">
      <div className="tabs">
        <button onClick={() => setActiveTab('workout')} className={`tab-button ${activeTab === 'workout' ? 'active' : ''}`}>
          운동 기록 추가
        </button>
        <button onClick={() => setActiveTab('inbody')} className={`tab-button ${activeTab === 'inbody' ? 'active' : ''}`}>
          인바디 추가
        </button>
      </div>

      {message.content && (
        <div className={`form-message ${message.type}`}>
          {message.content}
        </div>
      )}

      <div className="form-content">
        {activeTab === 'workout' ? (
          <form onSubmit={(e) => handleSubmit(e, addWorkoutLog, workoutLog, '운동 기록이 성공적으로 추가되었습니다!')}>
            <h3>운동 기록</h3>
            <input type="date" name="date" value={workoutLog.date} onChange={handleWorkoutChange} required />
            <input type="text" name="exercise_name" placeholder="운동 이름 (예: 벤치프레스)" value={workoutLog.exercise_name} onChange={handleWorkoutChange} required />
            <input type="number" name="weight" placeholder="무게(kg)" value={workoutLog.weight} onChange={handleWorkoutChange} />
            <input type="number" name="reps_or_time" placeholder="횟수 또는 시간" value={workoutLog.reps_or_time} onChange={handleWorkoutChange} />
            <select name="unit" value={workoutLog.unit} onChange={handleWorkoutChange}>
              <option value="회">회</option>
              <option value="초">초</option>
              <option value="분">분</option>
            </select>
            <button type="submit" className="workout-btn">저장</button>
          </form>
        ) : (
          <form onSubmit={(e) => handleSubmit(e, addInbodyRecord, inbodyRecord, '인바디 기록이 성공적으로 추가되었습니다!')}>
            <h3>인바디 기록</h3>
            <input type="date" name="date" value={inbodyRecord.date} onChange={handleInbodyChange} required />
            <input type="number" step="0.1" name="weight" placeholder="체중(kg)" value={inbodyRecord.weight} onChange={handleInbodyChange} required />
            <input type="number" step="0.1" name="muscle_mass" placeholder="골격근량(kg)" value={inbodyRecord.muscle_mass} onChange={handleInbodyChange} required />
            <input type="number" step="0.1" name="fat_percent" placeholder="체지방률(%)" value={inbodyRecord.fat_percent} onChange={handleInbodyChange} required />
            <button type="submit" className="inbody-btn">저장</button>
          </form>
        )}
      </div>
    </div>
  );
};

export default DataEntryForm;
