import React from 'react';
import DataEntryForm from './components/DataEntryForm';
import Dashboard from './components/Dashboard';
import { RefreshProvider } from './contexts/RefreshContext';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>AI 피트니스 대시보드</h1>
      </header>
      <RefreshProvider>
        <main>
          <div className="form-container">
            <DataEntryForm />
          </div>
          <div className="dashboard-container">
            <Dashboard />
          </div>
        </main>
      </RefreshProvider>
    </div>
  );
}

export default App;
