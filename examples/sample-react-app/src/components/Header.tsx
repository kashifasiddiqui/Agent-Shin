import React, { useState } from 'react';
import { Button } from './Button';

export const Header: React.FC = () => {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="border-b border-gray-200 bg-white px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <img src="/src/assets/logo.svg" alt="App Logo" className="w-8 h-8" />
        <span className="font-bold text-lg text-gray-900">FAgent Showcase</span>
      </div>
      <nav className="flex items-center gap-4">
        <a href="/" className="text-gray-600 hover:text-blue-600">Home</a>
        <a href="/projects" className="text-gray-600 hover:text-blue-600">Projects</a>
        <Button label="Sign In" variant="secondary" onClick={() => setMenuOpen(!menuOpen)} />
      </nav>
    </header>
  );
};
