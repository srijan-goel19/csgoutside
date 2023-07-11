import { useState, useEffect } from 'react';
import deathIcon from "./assets/death.png";

function Dead({ Player }) {
    
  const [killer, setKiller] = useState(null);  
  useEffect(() => {
    const req = 'http://206.87.112.30:8000/find-user/' + Player.killedby
    fetch(req, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    })
    .then((res) => res.json()) // Parse the response body as JSON
    .then((data) => setKiller(data))
  }, [Player])


  return (
  <div className="dead-container">
      <p></p>
      <p style={{fontSize: '30px'}}>You are dead</p>
      <img src={deathIcon} alt=">-/o"/>
      <p style={{fontSize: '15px'}}>You were killed by {killer ? (killer) : ("")}</p>
  </div>
  );
}

export default Dead;
