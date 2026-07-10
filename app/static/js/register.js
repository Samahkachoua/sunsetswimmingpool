function selectLevel(element) {
  document.querySelectorAll(".level-card").forEach((card) => {
    card.classList.remove("aqua-border", "bg-surface-bright");
    card.classList.add("border-transparent", "bg-surface-container");
  });
  element.classList.add("aqua-border", "bg-surface-bright");
  element.classList.remove("border-transparent", "bg-surface-container");
  document.getElementById("level").value = element.dataset.level;
}

function selectTime(time, element) {
  document.querySelectorAll(".time-btn").forEach((btn) => {
    btn.classList.remove("bg-primary-container", "text-white");
    btn.classList.add("text-on-surface-variant");
  });
  element.classList.add("bg-primary-container", "text-white");
  element.classList.remove("text-on-surface-variant");
  document.getElementById("time_preferred").value = time;
}
