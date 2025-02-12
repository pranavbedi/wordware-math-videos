import React from 'react';
import './Navbar.css';
import logo from '../assets/logo.png';

function Navbar() {
  return (
    <nav className="navbar">
      {/* Left side: logo + links */}
      <div className="navbar-left">
        <div className="navbar-logo">
          <img src={logo} alt="Company Logo" className="navbar-logo-img" />
        </div>
        <ul className="navbar-links">
          <li><a href="#pricing">Pricing</a></li>
          <li><a href="#insights">Insights</a></li>
          <li><a href="#affiliates">Affiliates</a></li>
          <li><a href="#guide">Guide</a></li>
        </ul>
      </div>
      
      {/* Right side: "Learn More" button */}
      <div className="navbar-right">
        <a href="#learn-more" className="navbar-learnMore">Learn More</a>
      </div>
    </nav>
  );
}

export default Navbar;
