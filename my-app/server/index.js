const express = require("express");
const bodyParser = require("body-parser");
const PORT = process.env.PORT || 3001;
const app = express();
const fs = require('fs');
// app.use(bodyParser.json());

// Increase the limit to 10MB
app.use(bodyParser.json({ limit: '10mb' }));
app.use(bodyParser.urlencoded({ limit: '10mb', extended: true }));

app.get("/api", (req, res) => {
  res.json({ message: "Hello from server!" });
});

shots = []
app.post('/send_shot', function(req, res) {
  const newShot = {
    PlayerID: req.body.playerID,
    Data: req.body.data,
  };
  shots.push(newShot);
  // console.log(shots);
  image = newShot.Data;
  const path = 'C:/All/Homework/Year_3_2021-2023/Term_2/CPEN_391/l2a-08-bitsonebyte/my-app/server/shot.png'; // the path where you want to save the image
  const data = image.replace(/^data:image\/\w+;base64,/, ''); // strip off the data:image/png;base64 part

  // Write the image file to disk
  fs.writeFile(path, data, 'base64', (err) => {
    if (err) throw err;
    console.log('Image saved successfully!');
  });
  res.json({ message: "shot received" });
});

app.listen(PORT, () => {
  console.log(`Server listening on ${PORT}`);
});