document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('btn-next').addEventListener('click', sendNext);
  document.getElementById('btn-prev').addEventListener('click', sendPrevious);
  document.getElementById('btn-delete').addEventListener('click', sendDelete);
  document.getElementById('btn-accept').addEventListener('click', sendAccept);
  updateImage(); // load image on startup
});

function sendNext(){
    fetch('http://localhost:5000/next', {method: 'POST'}).then(() => updateImage())
}

function sendPrevious(){
    fetch('http://localhost:5000/prev', {method: 'POST'}).then(() => updateImage())
}

function sendDelete(){
    fetch('http://localhost:5000/delete', {method: 'POST'}).then(() => updateImage())
}

function sendAccept(){
    fetch('http://localhost:5000/accept', {method: 'POST'}).then(() => updateImage())
}

function updateImage(){
    const img = document.getElementById('main-image');
    img.src = `http://localhost:5000/image?t=${new Date().getTime()}`;
}