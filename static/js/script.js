const video = document.createElement('video');
const canvas = document.getElementById('canvas');
const takePhotoBtn = document.getElementById('take-photo-btn');

navigator.mediaDevices.getUserMedia({ video: true })
  .then((stream) => {
    video.srcObject = stream;
    video.play();
  })
  .catch((error) => console.error(error));

takePhotoBtn.addEventListener('click', () => {
  console.log(document.getElementsByName('csrfmiddlewaretoken'));
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
  const imageData = canvas.toDataURL();
  const csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;
  const xhr = new XMLHttpRequest();
  xhr.open('POST', '/tasks/take-photo/');
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xhr.setRequestHeader('X-CSRFToken', csrfToken);
  xhr.onreadystatechange = () => {
    if (xhr.readyState === 4 && xhr.status === 200) {
      console.log(xhr.responseText);
    }
  };
  xhr.send(`image_data=${encodeURIComponent(imageData)}`);
});