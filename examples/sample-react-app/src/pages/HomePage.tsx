import React from 'react';
import { Header } from '../components/Header';
import { Button } from '../components/Button';

export const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 max-w-5xl mx-auto px-6 py-12 text-center">
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">
          Accelerate Frontend Quality with Autonomous Verification
        </h1>
        <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
          FAgent audits components, detects responsive flaws, validates design tokens, and guarantees frontend engineering rigor.
        </p>
        <div className="mt-8 flex justify-center gap-4">
          <Button label="Explore Projects" variant="primary" />
          <Button label="Read Docs" variant="secondary" />
        </div>
      </main>
    </div>
  );
};
