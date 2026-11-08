import React from 'react'; import { createRoot } from 'react-dom/client'; import App from './App.jsx'; import rows from './rows.json';
createRoot(document.getElementById('root')).render(<App data={[{ data: rows }]} />);
