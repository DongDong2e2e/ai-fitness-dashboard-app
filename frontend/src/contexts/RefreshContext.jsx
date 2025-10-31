import React, { createContext, useState, useCallback } from 'react';

// Context 생성: 초기값으로 refreshKey와 이를 변경할 함수를 정의합니다.
export const RefreshContext = createContext({
  refreshKey: 0,
  triggerRefresh: () => {},
});

// Provider 컴포넌트: 하위 컴포넌트들에게 실제 상태와 함수를 제공합니다.
export const RefreshProvider = ({ children }) => {
  const [refreshKey, setRefreshKey] = useState(0);

  // triggerRefresh 함수가 호출될 때마다 refreshKey 값을 1씩 증가시켜
  // 이 key를 구독하는 컴포넌트들의 리렌더링을 유발합니다.
  const triggerRefresh = useCallback(() => {
    setRefreshKey(prevKey => prevKey + 1);
    console.log('Dashboard refresh triggered!');
  }, []);

  return (
    <RefreshContext.Provider value={{ refreshKey, triggerRefresh }}>
      {children}
    </RefreshContext.Provider>
  );
};
