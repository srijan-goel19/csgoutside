import React, { useState } from 'react';
import './style.css';

function Lobby(props) {
  const [playerInfo, setPlayerInfo] = useState({ name: '', team: '' });
  const [picture, setPicture] = useState(null);

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setPlayerInfo((prevPlayerInfo) => ({ ...prevPlayerInfo, [name]: value }));
  };

  const handlePictureChange = (event) => {
    setPicture(event.target.files[0]);
  };
  
  
  const handleNextClick = () => {
    const reader = new FileReader();
    reader.readAsDataURL(picture);
    reader.onloadend = () => {
        const dataUrl = reader.result;
        const newPlayer = {
          name: playerInfo.name.trim(),
          team: playerInfo.team,
          health: "100",
          shirt: dataUrl,
          killedby: "",
          kills: "0"
        };
        props.onLoadComplete(newPlayer);
    };
  };

  const isFormValid = playerInfo.name && playerInfo.team && picture;

  return (
    <div className="lobby-container">
      <div className="player-info">
        <input type="text" id="name" name="name" placeholder={playerInfo.name ? "" : "Name"} value={playerInfo.name} onChange={handleInputChange} required />
      </div>
      <div className="team-selection">
        <select id="team" name="team" value={playerInfo.team} onChange={handleInputChange} required>
          <option value="" disabled>Select a team</option>
          <option value="Planter">Planter</option>
          <option value="Defuser">Defuser</option>
        </select>
      </div>
      <p>Upload a picture of your shirt</p>
      <div className="picture-upload">
        <input type="file" id="picture" name="picture" style={{display: "none"}} accept="image/*" onChange={handlePictureChange} required />
        <label className={!picture ? 'upload-player-btn' : 'upload-player-btn-uploaded'} htmlFor="picture">{!picture ? "Select picture" : "Reupload picture"}</label><br></br>
      </div>
      <button className={isFormValid ? 'create-player-btn' : 'create-player-btn-disabled'} onClick={handleNextClick} disabled={!isFormValid}>Create Player</button>
    </div>
  );
}

export default Lobby;
