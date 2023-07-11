import { useState, useEffect } from 'react';

function HealthBar({ Player }) {
  const maxGreen = 128;
  const maxHealth = 100;

  useEffect(() => {
    const healthBar = document.querySelector(".health-value");
    const hue = Player.health <= 20 ? 0 : Math.floor(Player.health * maxGreen / maxHealth)
    const color = "hsl("+ hue.toString() + ", 100%, 50%)";
    healthBar.style.backgroundColor = color;
    healthBar.style.width = (Player.health.toString() / maxHealth * 100).toString() + "%";
  }, [Player]);
  
  
  return (
    <div className="health-bar-container">
      <div className='health-bar'>
        <div className="health-value"></div>
        <div className="health-text-overlay">
          <p>{Player.health}</p>
        </div>
      </div>
    </div>
  );
}

export default HealthBar;
