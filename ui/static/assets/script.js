// ===============================
// 🌟 Generate animated stars
// ===============================
const stars = document.getElementById("stars");
const STAR_COUNT = 120;

if (stars) {
    for (let i = 0; i < STAR_COUNT; i++) {
        const star = document.createElement("div");
        const size = Math.random() * 2 + 1;
        star.className = "star";
        Object.assign(star.style, {
            position: "absolute",
            width: `${size}px`,
            height: `${size}px`,
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 70}%`,
            background: "white",
            borderRadius: "50%",
            opacity: Math.random() * 0.8 + 0.2,
            transition: "opacity 0.5s ease"
        });
        stars.appendChild(star);
    }
}

// ===============================
// 🏙️ Create parallax city buildings
// ===============================
function createCity() {
    const back = document.getElementById("city-back");
    const front = document.getElementById("city-front");
    if (!back || !front) return;

    back.innerHTML = front.innerHTML = "";

    for (let i = 0; i < 15; i++) {
        const b = document.createElement("div");
        Object.assign(b.style, {
            width: `${5 + Math.random() * 5}%`,
            height: `${20 + Math.random() * 25}vh`,
            background: "#64748b",
            marginLeft: `${Math.random() * 2}%`,
            borderRadius: "4px 4px 0 0",
            boxShadow: "0 0 10px rgba(255,255,255,0.05)"
        });
        back.appendChild(b);
    }

    for (let i = 0; i < 10; i++) {
        const b = document.createElement("div");
        Object.assign(b.style, {
            width: `${8 + Math.random() * 6}%`,
            height: `${10 + Math.random() * 15}vh`,
            background: "#475569",
            marginLeft: `${Math.random() * 2}%`,
            borderRadius: "4px 4px 0 0",
            boxShadow: "0 0 15px rgba(0,0,0,0.3)"
        });
        front.appendChild(b);
    }
}
createCity();

// ===============================
// 🌄 Dynamic sky & stars
// ===============================
window.addEventListener("scroll", () => {
    const sky = document.getElementById("sky");
    if (!sky || !stars) return;

    const scroll = window.scrollY / (document.body.scrollHeight - window.innerHeight);
    const isNight = scroll > 0.4;

    sky.style.transition = "background 1s ease-in-out";
    sky.style.background = isNight ?
        "linear-gradient(to bottom, #0f172a, #1e1b4b, #312e81)" :
        "linear-gradient(to bottom, #93c5fd, #3b82f6, #2563eb)";

    stars.style.opacity = Math.max(0, (scroll - 0.3) * 2);
});

// ===============================
// 👀 Fade-in animations
// ===============================
const observer = new IntersectionObserver(
    entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
                entry.target.style.transition = "opacity 1s ease, transform 1s ease";
            }
        });
    }, { threshold: 0.1 }
);

document.querySelectorAll(".fade-in").forEach(el => {
    el.style.opacity = "0";
    el.style.transform = "translateY(20px)";
    observer.observe(el);
});

// ===============================
// 📩 Load & Render Messages
// ===============================
async function loadMessages(filter = null) {
    let url = "/get_messages";
    if (filter) url += `?label=${filter}`;

    try {
        const res = await fetch(url, { credentials: "include" });
        const data = await res.json();

        // Update stats
        document.getElementById("totalMessages").textContent = data.stats.total;
        document.getElementById("suspiciousMessages").textContent = data.stats.suspicious;
        document.getElementById("safeMessages").textContent = data.stats.safe;

        const messagesList = document.getElementById("messagesList");
        if (!messagesList) return;

        if (!data.messages.length) {
            messagesList.innerHTML =
                "<div class='text-center text-blue-200'>No messages</div>";
            return;
        }

        messagesList.innerHTML = data.messages.map(msg => `
            <div class="glass rounded-xl p-4 ${
                msg.label === "suspicious"
                    ? "border-l-4 border-red-500"
                    : "border-l-4 border-green-500"
            }">
                <p class="text-white mb-2">${msg.text}</p>
                <p class="text-blue-200 text-sm">From: ${msg.sender}</p>
            </div>
        `).join("");
    } catch (err) {
        console.error("Message load error:", err);
    }
}

// ===============================
// 🖱️ Card Click Handlers
// ===============================
document.addEventListener("DOMContentLoaded", () => {
    const suspiciousCard = document.getElementById("card-suspicious");
    const safeCard = document.getElementById("card-safe");
    const totalCard = document.getElementById("card-total");

    if (suspiciousCard)
        suspiciousCard.onclick = () => loadMessages("suspicious");

    if (safeCard)
        safeCard.onclick = () => loadMessages("safe");

    if (totalCard)
        totalCard.onclick = () => loadMessages();

    // Initial load
    loadMessages();
});