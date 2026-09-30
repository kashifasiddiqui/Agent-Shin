import React, { useState } from 'react';
import { Header } from '../components/Header';
import { ProjectCard } from '../components/ProjectCard';

export const ProjectsPage: React.FC = () => {
  const [filter, setFilter] = useState('All');

  const projects = [
    { title: 'Bookstore UI', description: 'Modern e-commerce bookstore interface with cart and checkout.', category: 'E-commerce' },
    { title: 'Analytics Dashboard', description: 'Real-time telemetry and component audit metrics view.', category: 'Enterprise' },
    { title: 'Portfolio Showcase', description: 'Clean developer showcase with responsive grid layout.', category: 'Personal' },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <div className="max-w-6xl mx-auto px-6 py-10 w-full">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Featured Projects</h2>
          <div className="flex gap-2">
            {['All', 'E-commerce', 'Enterprise'].map((cat) => (
              <button
                key={cat}
                onClick={() => setFilter(cat)}
                className={`px-3 py-1 text-sm rounded-md ${
                  filter === cat ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {projects.map((p) => (
            <ProjectCard {...p} />
          ))}
        </div>

      </div>
    </div>
  );
};
