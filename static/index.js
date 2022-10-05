let ear_thresh = document.getElementById("ear_thresh");
let wait_time = document.getElementById("wait_time");

let ear = document.getElementById("ear");
let time = document.getElementById("time");

let video = document.querySelector("#videoElement");

ear.innerHTML = ear_thresh.value; 
time.innerHTML = wait_time.value; 

// Update the current slider value (each time you drag the slider handle)
ear_thresh.oninput = function() {
  ear.innerHTML = this.value;
}

wait_time.oninput = function() {
  time.innerHTML = this.value;
}


// if (navigator.mediaDevices.getUserMedia) {
//   navigator.mediaDevices.getUserMedia({ video: true })
//     .then(function (stream) {
//       video.srcObject = stream;
//     })
//     .catch(function (err0r) {
//       console.log("Something went wrong!");
//     });
// }