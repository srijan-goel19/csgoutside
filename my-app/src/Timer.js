import { useEffect } from 'react';
import deathIcon from "./assets/death.png";

function Timer({ timeRemaining, setTimeRemaining, end_time, Player }) {
  const end_time_van = end_time - 7*3600
  useEffect(() => {
    const endTime = new Date(end_time_van * 1000);
    const intervalId = setInterval(() => {
      const now = new Date();
    //   now.setUTCHours(now.getUTCHours() + 7);
      const remaining = endTime - now;
      setTimeRemaining(remaining);
    }, 1000);

    return () => clearInterval(intervalId);
  }, [end_time_van, setTimeRemaining]);

  const formatTime = (ms) => {
    const seconds = Math.floor(ms / 1000) % 60;
    const minutes = Math.floor(ms / 1000 / 60) % 60;
    // const hours = Math.floor(ms / 1000 / 60 / 60);

    return `${minutes}:${seconds < 10 ? "0" + seconds.toString() : seconds}`;
  };

  return (
    <div>
      <div className='timer-container'>
        {timeRemaining == null ? (
          <p></p>
        ) : timeRemaining > 0 ? (
          <p>{formatTime(timeRemaining)}</p>
        ) : (
          <p>0:00</p>
          // // <p>{formatTime(timeRemaining)}</p>
        )}
      </div>
      <div className='info-container'>
        <p className='info-column' style={{textAlign: 'left'}}>{Player.team}</p>
        <p className='info-column' style={{textAlign: 'center'}}>{Player.name}</p>
        <p className='info-column' style={{textAlign: 'right'}}>{Player.kills+" "}
          <img src={deathIcon} alt="kills"/>
        </p>
      </div>
    </div>
  );
}

export default Timer;
