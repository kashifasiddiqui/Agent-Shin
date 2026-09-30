import React, { useState, useEffect } from 'react';
import { Button } from './Button';

interface ProjectCardProps {
  title: string;
  description: string;
  category: string;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({ title, description, category }) => {
  const [likes, setLikes] = useState(0);

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow">
      <span className="text-xs font-semibold px-2 py-1 bg-blue-50 text-blue-700 rounded-full">
        {category}
      </span>
      <h3 className="text-lg font-bold text-gray-900 mt-3">{title}</h3>
      <p className="text-sm text-gray-600 mt-1">{description}</p>
      <div className="mt-2">
        <a href="https://github.com" target="_blank" className="text-xs text-blue-500 hover:underline">
          View Repository
        </a>
      </div>
      <div className="mt-4 flex items-center justify-between">
        <Button label={`Like (${likes})`} variant="secondary" onClick={() => setLikes(likes + 1)} />
        <Button label="View Details" variant="primary" />
      </div>
    </div>
  );
};

