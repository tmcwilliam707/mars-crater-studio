import React from 'react';
import CraterScene from './CraterScene';
import './CraterScene.css';

const App = () => {
  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      {/* Pass the oid for the clooned-object instead of a filePath */}
      <CraterScene oid="5cf97eb291154c349930081909c455a4" />
    </div>
  );
};

export default App;