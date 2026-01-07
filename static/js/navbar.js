// UI-only helper (safe, optional)

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".dropdown-item").forEach(item => {
    item.addEventListener("click", () => {
      const openDropdown = document.querySelector(".dropdown-menu.show");
      if (openDropdown) {
        bootstrap.Dropdown
          .getInstance(openDropdown.previousElementSibling)
          ?.hide();
      }
    });
  });
});

// Navbar UI helpers

document.addEventListener("DOMContentLoaded", () => {
  const greetingEl = document.getElementById("greeting-text");

  if (greetingEl) {
    const hour = new Date().getHours();
    let greeting = "Good Evening";
    let emoji = "🌙";

    if (hour >= 5 && hour < 12) {
      greeting = "Good Morning";
      emoji = "☀️";
    } else if (hour >= 12 && hour < 18) {
      greeting = "Good Afternoon";
      emoji = "🌤️";
    } else if (hour >= 18 && hour < 22) {
      greeting = "Good Evening";
      emoji = "🌙";
    } else {
      greeting = "Good Night";
      emoji = "🌙";
    }

    const fullName = greetingEl.dataset.fullname;
    greetingEl.innerText = `${greeting} ${emoji}, ${fullName}`;
  }

  // Close dropdown after click (mobile UX)
  document.querySelectorAll(".dropdown-item").forEach(item => {
    item.addEventListener("click", () => {
      const openDropdown = document.querySelector(".dropdown-menu.show");
      if (openDropdown) {
        bootstrap.Dropdown
          .getInstance(openDropdown.previousElementSibling)
          ?.hide();
      }
    });
  });
});

/* ===============================
   FOOTER SERVER CLOCK
   =============================== */

(function () {
  const clockEl = document.getElementById("footerClock");
  if (!clockEl) return;

  // Parse server time
  let serverTime = new Date(clockEl.dataset.serverTime.replace(" ", "T"));

  let showColon = true;

  function pad(num) {
    return String(num).padStart(2, "0");
  }

  function updateClock() {
    serverTime.setSeconds(serverTime.getSeconds() + 1);

    showColon = !showColon;
    const colon = showColon ? ":" : " ";

    const hours = pad(serverTime.getHours());
    const minutes = pad(serverTime.getMinutes());
    const seconds = pad(serverTime.getSeconds());

    clockEl.textContent = `${hours}${colon}${minutes}${colon}${seconds}`;
  }

  updateClock();
  setInterval(updateClock, 1000);
})();

