import React from 'react';
// import './style.css';

function Ready(props) {
  const handleReadyClick = () => {
    // call the function passed from parent to notify that the player is ready
    props.onReady();
  };

  if (!props.game_data) {
    return <p>Loading...</p>;
  }

  const planters = props.game_data.players.filter(player => player.team === 'Planter');
  const defusers = props.game_data.players.filter(player => player.team === 'Defuser');

  if(props.game_data.state != "preround") {
    props.onReady();
  }

  return (
    <div className="ready-container">
      <h2>Get Ready!</h2>
      <p>Are you ready to start the game? Hit Start once everyone joins the lobby!</p>
      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <div className="column">
          <h2>Planters</h2>
          <ul>
            {planters.map(player => (
              <li key={player.id}>{player.name}</li>
            ))}
          </ul>
        </div>
        <div className="column">
          <h2>Defusers</h2>
          <ul>
            {defusers.map(player => (
              <li key={player.id}>{player.name}</li>
            ))}
          </ul>
        </div>
      </div>

      <button className='create-player-btn' onClick={handleReadyClick}>Start Game</button>
    </div>
  );
}

export default Ready;
