import { useEffect } from 'react';
import deathIcon from "./assets/death.png";

function GameOver({ game_data, Player, isGameOver }) {

  useEffect(() => {
    const body = document.querySelector('body');

    //Set red background if the bomb is planted
    if (isGameOver && game_data && Player) {    
      if (game_data.winners === Player.team) {
        body.classList.remove('winner');
        body.classList.add('loser');
      } else {
        body.classList.remove('winner');
        body.classList.add('loser');
      }
    }

  }, [game_data, isGameOver, Player]);

  const planters = game_data.players.filter(player => player.team === 'Planter');
  const defusers = game_data.players.filter(player => player.team === 'Defuser');

  function restartGame() {
    fetch('http://206.87.112.30:8000/resetDB', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    })
    .then((res) => res.json())
  }

  return (
  <div className="game-over-container">
    <h2>Game Over</h2>
    <p>{game_data.winners} win!</p>
    <div style={{ display: 'flex', justifyContent: 'center' }}>
      <div className="column">
        <h2>Planters</h2>
        <ul>
          {planters.map(player => (
            <li key={player.id}>{player.name}: {player.kills+" "}
            <img src={deathIcon} alt="kills"/>
          </li>
          ))}
        </ul>
      </div>
      <div className="column">
        <h2>Defusers</h2>
        <ul>
          {defusers.map(player => (
            <li key={player.id}>{player.name}: {player.kills+" "}
            <img src={deathIcon} alt="kills"/>
          </li>
          ))}
        </ul>
      </div>
    </div>

    <button className='create-player-btn' onClick={restartGame}>Restart Game</button>
  </div>
  );
}

export default GameOver;
