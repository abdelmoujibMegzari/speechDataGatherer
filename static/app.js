const formC = document.getElementById("formContainer");
const recC = document.getElementById("recContainer");
const regForm = document.getElementById("regForm");
const userHeader = document.getElementById("userHeader");
const sentenceP = document.getElementById("sentence");
const recordBtn = document.getElementById("recordBtn");
const submitBtn = document.getElementById("submitRecBtn");
const skipBtn = document.getElementById("skipBtn");
const logoutBtn = document.getElementById("logoutBtn");
const audioEl = document.getElementById("audioPlayback");

let mediaRecorder, audioBlob;

// set current sentence if the user is already connected

// 1️⃣ Handle registration submit
regForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(regForm);
  const payload = Object.fromEntries(form.entries());

  const res = await fetch("/submit", {
    headers: { "Content-Type": "application/json" },
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (res.ok) {
    const data = await res.json();

    // show recording view
    formC.style.display = "none";
    recC.style.display = "block";
    userHeader.textContent = "test";
    setCurrentSentence(data.next_sentence);
  }
});

// 2️⃣ Recording
recordBtn.addEventListener("click", async () => {
  if (!mediaRecorder) {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    const chunks = [];
    mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
    mediaRecorder.onstop = () => {
      audioBlob = new Blob(chunks, { type: "audio/webm" });
      recordBtn.textContent = "Record";
      const url = URL.createObjectURL(audioBlob);
      audioEl.src = url;
      audioEl.style.display = "block";
      submitBtn.disabled = false;
    };
  }

  if (mediaRecorder.state === "inactive") {
    mediaRecorder.start();
    recordBtn.textContent = "Stop";
  } else {
    await mediaRecorder.stop();
    recordBtn.textContent = "Record";
  }
});

// 4️⃣ Submit recording & fetch next sentence
submitBtn.addEventListener("click", async () => {
  const fd = new FormData();
  fd.append("audio", audioBlob, "rec.webm");

  const res = await fetch("/record", {
    method: "POST",
    body: fd,
  });
  const data = await res.json();
  if (res.ok) {
    resetRecorder();
    setCurrentSentence(data.next_sentence);
  }
});

// 5️⃣ Skip
skipBtn.addEventListener("click", async () => {
  const res = await fetch("/next-sentence");
  const data = await res.json();
  if (res.ok) {
    resetRecorder();
    setCurrentSentence(data.next_sentence);
  }
});

// logout
logoutBtn.addEventListener("click", async () => {
  const res = await fetch("/logout", { method: "POST" });
  if (res.ok) {
    // show recording view
    formC.style.display = "block";
    recC.style.display = "none";
  }
});

// helper to reset UI between sentences
function resetRecorder() {
  submitBtn.disabled = true;
  audioEl.style.display = "none";
  audioEl.src = "";
  audioBlob = null;
}

function setCurrentSentence(nextSentence) {
  sentenceP.textContent = nextSentence || "🎉 You’ve finished all sentences!";
  recordBtn.style.display = "none";
  submitBtn.style.display = "none";
  skipBtn.style.display = "none";
}
