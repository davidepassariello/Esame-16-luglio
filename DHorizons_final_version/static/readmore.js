document.addEventListener("DOMContentLoaded", function () {
  const buttons = document.querySelectorAll(".toggle-btn");

  buttons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      const card = btn.closest(".toggle-container");
      const dots = card.querySelector(".dots");
      const more = card.querySelector(".more-text");

      if (dots.style.display === "none") {
        dots.style.display = "inline";
        more.style.display = "none";
        btn.innerHTML = "Leggi di più";
      } else {
        dots.style.display = "none";
        more.style.display = "inline";
        btn.innerHTML = "Leggi meno";
      }
    });
  });
});
