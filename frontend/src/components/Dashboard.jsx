import React, { useState, useEffect, useContext } from 'react';
import { getDashboardData } from '../services/api';
import SingleLineChart from './charts/SingleLineChart';
import MultiLineChart from './charts/MultiLineChart';
import { RefreshContext } from '../contexts/RefreshContext';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [error, setError] = useState(null);
  const { refreshKey } = useContext(RefreshContext); // Context에서 refreshKey 가져오기

  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('Fetching dashboard data...');
        const response = await getDashboardData();
        setDashboardData(response.data);
      } catch (err) {
        setError('대시보드 데이터를 불러오는 데 실패했습니다.');
        console.error(err);
      }
    };

    fetchData();
  }, [refreshKey]); // refreshKey가 변경될 때마다 useEffect 재실행

  if (error) {
    return <div>{error}</div>;
  }

  if (!dashboardData) {
    return <div>데이터를 불러오는 중...</div>;
  }

  return (
    <div>
      <h2>대시보드</h2>
      <div className="charts-container">
        {dashboardData.inbodyData && <MultiLineChart title="인바디 변화" chartData={dashboardData.inbodyData} />}
        {Object.keys(dashboardData.pushData).map(exercise => (
            <SingleLineChart key={exercise} title={`${exercise} 중량 변화`} chartData={dashboardData.pushData[exercise]} />
        ))}
        {Object.keys(dashboardData.pullData).map(exercise => (
            <SingleLineChart key={exercise} title={`${exercise} 중량 변화`} chartData={dashboardData.pullData[exercise]} />
        ))}
        {Object.keys(dashboardData.legData).map(exercise => (
            <SingleLineChart key={exercise} title={`${exercise} 중량 변화`} chartData={dashboardData.legData[exercise]} />
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
