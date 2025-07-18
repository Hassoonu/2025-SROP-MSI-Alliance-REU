


document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM loaded");
    document.getElementById('btn-next').addEventListener('click', () => sendNext());
    document.getElementById('btn-prev').addEventListener('click', () =>sendPrevious());
    document.getElementById('btn-delete').addEventListener('click', () =>sendDelete());
    document.getElementById('btn-accept').addEventListener('click', () =>sendAccept());
    updateImage(); // load image on startup
});

function sendNext(){
    console.log("Next Image...");
    fetch('http://localhost:5000/next', {method: 'POST'})
    .then(res => {
            if (!res.ok) {
                throw new Error('Server returned an error');
            }
            return res;
        })
    .then(() => updateImage())
    .catch(err => console.error("Failed to send POST to /accept:", err));
}

function sendPrevious(){
    console.log("Previous Image...");
    fetch('http://localhost:5000/prev', {method: 'POST'}).then(res => {
            if (!res.ok) {
                throw new Error('Server returned an error');
            }
            return res;
        })
    .then(() => updateImage())
    .catch(err => console.error("Failed to send POST to /accept:", err));
}

function sendDelete(){
    console.log("Deleting Image...");
    fetch('http://localhost:5000/delete', {method: 'POST'}).then(res => {
            if (!res.ok) {
                throw new Error('Server returned an error');
            }
            return res;
        })
    .then(() => updateImage())
    .catch(err => console.error("Failed to send POST to /accept:", err));
}

function sendAccept() {
    console.log("Accepting Image...");
    fetch('http://localhost:5000/accept', { method: 'POST' })
        .then(res => {
            if (!res.ok) {
                throw new Error('Server returned an error');
            }
            return res;
        })
        .then(() => updateImage())
        .catch(err => console.error("Failed to send POST to /accept:", err));
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function updateImage(retries = 3, delay = 5000) {
    console.log("Updating Image...");
    try {
        const response = await fetch("http://localhost:5000/image");
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }

        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);
        document.getElementById("data_image").src = imageUrl;
    } catch (error) {
        console.error("Failed to load image:", error);

        if (retries > 0) {
            console.log(`Retrying in ${delay / 1000}s... (${retries} attempts left)`);
            await sleep(delay);  // ⏸️ This is now a blocking delay
            await updateImage(retries - 1, delay);  // 🔁 Recursively await retries
        } else {
            console.error("All retries failed. Please try again.");
        }
    }
}



async function waitForFlaskReady(timeout = 10000) {
    const start = Date.now();
    while (Date.now() - start < timeout) {
        try {
            const response = await fetch("http://localhost:5000/");
            if (response.ok) return true;
        } catch (_) {
            // Flask isn't ready yet
        }
        await new Promise(res => setTimeout(res, 500));
    }
    throw new Error("Flask server did not become ready in time");
}



async function init() {
    await waitForFlaskReady();
    updateImage();
}

document.addEventListener("DOMContentLoaded", init);