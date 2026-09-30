from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ColorUsage(BaseModel):
    value: str = Field(description="Color representation, e.g. '#2563eb', 'rgb(...)', 'blue-600'")
    count: int = Field(default=1, description="Occurrences in project")
    sources: List[str] = Field(default_factory=list, description="Files where color is used")


class RadiusUsage(BaseModel):
    value: str = Field(description="Radius representation, e.g. '8px', 'rounded-xl'")
    count: int = Field(default=1, description="Occurrences in project")
    sources: List[str] = Field(default_factory=list, description="Files where radius is used")


class DesignSystem(BaseModel):
    primary_colors: List[str] = Field(default_factory=list, description="Dominant primary colors")
    accent_colors: List[str] = Field(default_factory=list, description="Discovered accent colors")
    all_colors: Dict[str, ColorUsage] = Field(default_factory=dict, description="All extracted colors and frequencies")
    radii: Dict[str, RadiusUsage] = Field(default_factory=dict, description="Border radius tokens and counts")
    font_families: List[str] = Field(default_factory=list, description="Discovered font families")
    font_sizes: List[str] = Field(default_factory=list, description="Discovered typography scale entries")
    shadows: List[str] = Field(default_factory=list, description="Discovered shadow definitions")
    gradients: List[str] = Field(default_factory=list, description="Discovered gradient styles")
    glassmorphism_elements: List[str] = Field(default_factory=list, description="Elements using frosted glass/backdrop-blur")
    total_token_count: int = Field(default=0, description="Total design tokens extracted")
