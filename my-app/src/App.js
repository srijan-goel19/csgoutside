import { useRef, useState, useEffect } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css'
import Camera from './Camera';
import Lobby from './Lobby';
import Ready from './Ready';
import Timer from './Timer';
import HealthBar from './HealthBar';
import Dead from './Dead';
import GameOver from './GameOver';
import './style.css';


function App() {
  let videoRef = useRef(null);
  let photoRef = useRef(null);
  const [isLobby, setIsLobby] = useState(true); // Starts from lobby screen
  const [isReady, setIsReady] = useState(false);
  const [isDead, setIsDead] = useState(false);
  const [isGameOver, setGameOver] = useState(false);
  const [game_data, setGameData] = useState(null); //socket data
  const [PLAYER_DB_ID, setPLAYER_DB_ID] = useState(null);
  const [socket, setSocket] = useState(null);
  const [currentPlayer, setCurrentPlayer] = useState(null);
  const [timeRemaining, setTimeRemaining] = useState(null);



  //let PLAYER_DB_ID;

  // useEffect(() => {
  //   fetch("http://24.86.161.214:8000/api")
  //     .then((res) => res.json())
  //     .then((data0) => setData0(JSON.stringify(data0)));
  //     // setIsLobby(true); // <-- Set loading state to false after data is loaded 
  // }, []);

  //my first socket
  useEffect(() => {
    if(PLAYER_DB_ID && !socket) {
      const newSocket = new WebSocket('ws://206.87.112.30:8000/fe-ws');
      newSocket.onopen = function(event) {
        newSocket.send(JSON.stringify({id: "playerJoin", data: PLAYER_DB_ID}));
      };

      newSocket.onmessage = function(event) {
        console.log('Received message:', event.data);
        const game_data = JSON.parse(event.data);
        setGameData(game_data);
      };

      setSocket(newSocket);
    }
  }, [PLAYER_DB_ID, socket]);

  useEffect(() => {
    const start_game = !isLobby && !isReady;
    if (start_game && socket) {
      socket.send(JSON.stringify({id: "gameStart", data: start_game}))
    }
  }, [isLobby, isReady, socket]);


  useEffect(() => {
    if (game_data) {
      const currentPlayer = game_data.players.find(player => player.id === PLAYER_DB_ID);
      if (currentPlayer) {
        setCurrentPlayer(currentPlayer);
      }
    }
  }, [game_data, PLAYER_DB_ID]);

  useEffect(() => {
    if (currentPlayer && parseInt(currentPlayer.health) <= 0) {
        setIsDead(true);
    }
  }, [currentPlayer]);

  const handleLoadComplete = (newPlayer) => {
    const data = newPlayer
    fetch('http://206.87.112.30:8000/create-user', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
      .then((response) => response.json())
      .then((result) => {
        setPLAYER_DB_ID(result["id"]);
        console.log('New player created:', result);
        setIsLobby(false);
        setIsReady(true);
      })
      .catch((error) => {
        console.error('Error creating new player:', error);
      });
  };

  const handleReady = () => {
    setIsReady(false);
  };

  useEffect(() => {
    if (game_data && game_data.game_over === true) {
      setGameOver(true);
    }

    const body = document.querySelector('body');

    //Set red background if the bomb is planted
    if (game_data && game_data.state === 'planted') {
      body.classList.remove('not-planted');
      body.classList.add('planted');
    } else {
      body.classList.remove('planted');
      body.classList.add('not-planted');
    }

  }, [game_data, isLobby, isReady, isDead, isGameOver]);

  useEffect(() => {
    if (game_data && game_data.state === "preround" && isReady === false) {
      setIsLobby(true);
      setIsReady(false);
      setIsDead(false);
      setGameOver(false);
      setGameData(null);
      setPLAYER_DB_ID(null);
      setSocket(null);
      setCurrentPlayer(null);
      setTimeRemaining(null);

    }
  }, [game_data]);

  useEffect(() => {
    if (timeRemaining && timeRemaining <= 0) {
      setGameOver(true);
    }
  }, [timeRemaining]);

  return (
      <div>
        <h1 className="text-center">CSGOutside</h1>
        {isGameOver ? (
          <GameOver game_data={game_data} Player={currentPlayer} isGameOver={isGameOver}/>
        ) : isLobby && !isReady ? (
          <Lobby onLoadComplete={handleLoadComplete} />
        ) : isReady ? (
          <Ready onReady={handleReady} game_data={game_data} />
        ) : isDead ? (
          <div>
            <Timer timeRemaining={timeRemaining} setTimeRemaining={setTimeRemaining} end_time={game_data.end_time} Player={currentPlayer} />
            <Dead Player={currentPlayer} />
          </div>
        ) : (
          <div className="camera-view" >
            {game_data && (
              <Timer timeRemaining={timeRemaining} setTimeRemaining={setTimeRemaining} end_time={game_data.end_time} Player={currentPlayer} />
            )}
            {game_data && (
              <HealthBar Player={currentPlayer} />
            )}
            <Camera videoRef={videoRef} photoRef={photoRef} PLAYER_DB_ID={PLAYER_DB_ID}/>
          </div>
        )}
      </div>
);
}

export default App;