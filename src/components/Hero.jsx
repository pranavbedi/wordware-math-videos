// Hero.jsx
import React from 'react';
import './Hero.css';

function Hero() {
  return (
    <section className="hero">
      <div className="hero-content">
        {/* Glowy label/pill */}
        <div className="hero-preheading">
          Unlock Your Creative Potential
        </div>

        {/* Main heading with gradient text */}
        <h1>
          Fastest & Easiest Way to Generate Short Educational
          <span className="text-gradient"> Videos</span>
        </h1>

        <p className="hero-subtext">
          Generate unlimited short videos at once with automatic 
          captions, effects, backgrounds, and music.
        </p>

        <div className="hero-buttons">
          <a href="#trial" className="btn hero-btn-primary">Start 7 Days Trial</a>
          <a href="#learn" className="btn hero-btn-secondary">Learn More</a>
        </div>
      </div>
    </section>
  );
}

export default Hero;
