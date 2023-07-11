import React, { useEffect, useState } from 'react';
import shootButton from "./assets/shoot-button.png";
import shootButtonDisabled from "./assets/shoot-button-disabled.png";
import crosshair from "./assets/crosshair.png"
import shotSound from "./assets/shot.mp3";

const shooting_delay = 1500;
const ch_percentage = 0.05;

function Camera({videoRef, photoRef, PLAYER_DB_ID}) {
  const [canShoot, setCanShoot] = useState(true);
  //to take picture
  const takePicture = () => {
    const audio = new Audio(shotSound);
    audio.play();

    //disable shooting for a short period
    setCanShoot(false);
    setTimeout(() => {
      setCanShoot(true);
    }, shooting_delay);

    //width and height
    let width = videoRef.current.videoWidth;
    let height = videoRef.current.videoHeight;

    //calculate crosshair
    // let x = Math.floor(Math.sqrt(width * height * ch_percentage));
    // const crosshair = document.getElementById("crosshair");
    // crosshair.style.left = Math.floor(width / 2);
    // crosshair.style.top = Math.floor(height / 2); 
    // crosshair.style.width = x;



    let photo = photoRef.current;
    let video = videoRef.current;

    //set photo width and height
    photo.width = width;
    photo.height = height;
    
    //Used to Draw the image in the app
    let context = photo.getContext('2d')
    context.drawImage(video, 0, 0, photo.width, photo.height)

    //Used to get the image URL to backend
    const shot_data = photo.toDataURL("image/png");
    // console.log(shot_data)
    const shot = {
      playerID: PLAYER_DB_ID,
      playerShot: shot_data.toString()
    }
    fetch("http://206.87.112.30:8000/send-shot", {
      method: "POST",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(shot),
    })
      .then((res) => res.json())
      .then(data => console.log(data))
      .catch(error => console.error(error));
  }

  //clear Image from screen
  // const clearImage = () => {
  //   let photo = photoRef.current
  //   let context = photo.getContext('2d')

  //   context.clearRect(0, 0, photo.width, photo.height)
  // }

  useEffect(() => {
    //get access to user's camera
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      const getUserCamera = () => {
        navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: "environment",
          }
        })
        .then((stream) => {
          //attach the stream to the video tag
          let video = videoRef.current;
          video.srcObject = stream;
          video.play();
        })
        .catch((error) => {
          console.error(error);
        })
        

        
      }
      getUserCamera()
    }
  }, [videoRef]);

  useEffect(() => {
    //width and height
    let vidDims = document.querySelector('#video').getBoundingClientRect();
    let width = 100;
    let height = vidDims.height / vidDims.width * 100;

    //calculate crosshair
    let x = Math.floor(Math.sqrt(width * height * ch_percentage));
    const crosshair = document.getElementById("crosshair");
    crosshair.style.width = x.toString() + "%";
  }, [videoRef])

  return (
    <div className='video-container-wrapper'>
      <div className='video-container'>
        <video ref= {videoRef} id="video"></video>
        <button disabled = {!canShoot} onClick= {takePicture} id='shoot-button'>
          {canShoot ? (<img src={shootButton} alt="Shoot"/>) : (<img src={shootButtonDisabled} alt="Can't Shoot"/>)}
        </button>
        <img src={crosshair} alt="" id='crosshair'/>
        <canvas ref= {photoRef} className='vestigial'></canvas>
      </div>
    </div>
  );
}

export default Camera;