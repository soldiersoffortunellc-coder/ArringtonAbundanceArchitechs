// StrictMode smoke test for react/DoorIntro.jsx (bundled by build.mjs in this folder).
import React, { StrictMode, useState } from 'react';
import { createRoot } from 'react-dom/client';
import DoorIntro from '../../react/DoorIntro.jsx';

function App() {
  const [mounted, setMounted] = useState(true);
  window.__unmount = () => setMounted(false);
  return (
    <main>
      <h1>React host page</h1>
      <button id="unmount" onClick={() => setMounted(false)}>Unmount intro</button>
      {mounted && (
        <DoorIntro preset="opendoors" imageUrl="/images/door-intro/arrington-founders.jpg" playMode="always" />
      )}
    </main>
  );
}

createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>);
