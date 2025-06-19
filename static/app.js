const formC = document.getElementById('formContainer');
const recC  = document.getElementById('recContainer');
const regForm = document.getElementById('regForm');
const userHeader = document.getElementById('userHeader');
const sentenceP  = document.getElementById('sentence');
const recordBtn  = document.getElementById('recordBtn');
const playBtn    = document.getElementById('playBtn');
const submitBtn  = document.getElementById('submitRecBtn');
const skipBtn    = document.getElementById('skipBtn');
const audioEl    = document.getElementById('audioPlayback');

let mediaRecorder, audioBlob;


// 1️⃣ Handle registration submit
regForm.addEventListener('submit', async e => {
  e.preventDefault();
  const form = new FormData(regForm);
  const payload = Object.fromEntries(form.entries());

  const res = await fetch('/submit', {
    headers: {'Content-Type':'application/json'},
    method: 'POST',
    body: JSON.stringify(payload)
  });
  if(res.ok){

    const data = await res.json();
    
    // show recording view
    formC.style.display = 'none';
    recC.style.display  = 'block';
    userHeader.textContent = 'test';
    sentenceP.textContent = data.next_sentence;
  }
});

// 2️⃣ Recording
recordBtn.addEventListener('click', async () => {
  if (!mediaRecorder) {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    const chunks = [];
    mediaRecorder.ondataavailable = e => chunks.push(e.data);
    mediaRecorder.onstop = () => {
      audioBlob = new Blob(chunks, { type: 'audio/webm' });
      recordBtn.textContent = 'Record';
      const url = URL.createObjectURL(audioBlob);
      audioEl.src = url;
      audioEl.style.display = 'block';
      submitBtn.disabled = false;
    };
  }

  if (mediaRecorder.state === 'inactive') {
    mediaRecorder.start();
    recordBtn.textContent = 'Stop';
  } else {
    await mediaRecorder.stop();
    recordBtn.textContent = 'Record';
  }
});


// 4️⃣ Submit recording & fetch next sentence
submitBtn.addEventListener('click', async () => {
  const fd = new FormData();
  fd.append('audio', audioBlob, 'rec.webm');

  const res = await fetch('/record', {
    method: 'POST',
    body: fd
  });
  const data = await res.json();
  if (data.success) {
    resetRecorder();
    sentenceP.textContent = data.next_sentence || 
      '🎉 You’ve finished all sentences!';
  }
});

// 5️⃣ Skip
skipBtn.addEventListener('click', async () => {
  const res = await fetch('/next-sentence');
  const data = await res.json();
  if (data.success) {
    resetRecorder();
    sentenceP.textContent = data.next_sentence || 
      '🎉 You’ve finished all sentences!';
  }
});

// helper to reset UI between sentences
function resetRecorder() {
  playBtn.disabled = true;
  submitBtn.disabled = true;
  audioEl.style.display = 'none';
  audioEl.src = '';
  audioBlob = null;
}
