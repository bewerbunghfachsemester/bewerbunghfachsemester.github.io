/* bewerbungsrenner.com – Countdown, Heute-Markierung, Uni-Suche, Sprungmarken.
   Alles ist optional: Ohne JavaScript bleiben alle Inhalte sichtbar und nutzbar. */
(function () {
  "use strict";

  const DEADLINES = [
    { month: 12, day: 1, text: "bis zum Bewerbungsstart Sommersemester" },
    { month: 1, day: 15, text: "bis zum Bewerbungsschluss Sommersemester" },
    { month: 6, day: 1, text: "bis zum Bewerbungsstart Wintersemester" },
    { month: 7, day: 15, text: "bis zum Bewerbungsschluss Wintersemester" },
  ];
  const DAY_MS = 864e5;
  const FLIP_LABEL_AT_PERCENT = 88;
  const LABEL_GAP_PX = 14;
  const UMLAUTS = { ä: "ae", ö: "oe", ü: "ue", ß: "ss" };

  const pad = (value) => String(value).padStart(2, "0");

  const yearPercent = (month, day) =>
    ((Date.UTC(2025, month - 1, day) - Date.UTC(2025, 0, 1)) / DAY_MS / 365) *
    100;

  const normalize = (text) =>
    text
      .toLowerCase()
      .replace(/[äöüß]/g, (char) => UMLAUTS[char])
      .trim();

  const startOfToday = () => {
    const now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), now.getDate());
  };

  const nextDeadline = (today) =>
    DEADLINES.map((deadline) => {
      const thisYear = new Date(
        today.getFullYear(),
        deadline.month - 1,
        deadline.day,
      );
      const target =
        thisYear < today
          ? new Date(today.getFullYear() + 1, deadline.month - 1, deadline.day)
          : thisYear;
      return {
        days: Math.round((target - today) / DAY_MS),
        date: `${pad(deadline.day)}.${pad(deadline.month)}.`,
        text: deadline.text,
      };
    }).reduce((best, item) => (item.days < best.days ? item : best));

  const digitColumn = (digit, index) => {
    const column = document.createElement("span");
    const strip = document.createElement("span");
    column.className = "digit";
    strip.style.setProperty("--to", `${-digit * 10}%`);
    strip.style.setProperty("--delay", `${0.3 + index * 0.14}s`);
    for (let value = 0; value <= 9; value += 1) {
      const cell = document.createElement("span");
      cell.textContent = String(value);
      strip.appendChild(cell);
    }
    column.appendChild(strip);
    return column;
  };

  const initCountdown = (element, today) => {
    const deadline = nextDeadline(today);
    const digits = element.querySelector("[data-cd-digits]");
    if (!digits) {
      return;
    }
    String(deadline.days)
      .split("")
      .forEach((digit, index) => {
        digits.appendChild(digitColumn(Number(digit), index));
      });
    element.querySelector("[data-cd-date]").textContent = deadline.date;
    element.querySelector("[data-cd-unit]").textContent =
      deadline.days === 1 ? "Tag" : "Tage";
    element.querySelector("[data-cd-text]").textContent = deadline.text;
    element.querySelector("[data-cd-sr]").textContent =
      `Noch ${deadline.days} ${deadline.days === 1 ? "Tag" : "Tage"} ${deadline.text} am ${deadline.date}`;
    element.classList.add("is-ready");
  };

  const initTodayMarker = (chart, today) => {
    const percent = yearPercent(today.getMonth() + 1, today.getDate());
    const marker = chart.querySelector("[data-today]");
    chart.style.setProperty("--today", `${percent.toFixed(2)}%`);
    if (!marker) {
      return;
    }
    const label = marker.querySelector("[data-today-label]");
    label.textContent = `Heute · ${pad(today.getDate())}.${pad(today.getMonth() + 1)}.`;
    marker.hidden = false;
    const spaceRight = chart.clientWidth * (1 - percent / 100);
    const tooTight = spaceRight < label.offsetWidth + LABEL_GAP_PX;
    marker.classList.toggle(
      "flip",
      percent > FLIP_LABEL_AT_PERCENT || tooTight,
    );
  };

  const initFilter = (input) => {
    const list = document.querySelector(input.dataset.filter);
    const scope = input.closest("section") || document;
    const counter = scope.querySelector("[data-filter-count]");
    const empty = scope.querySelector("[data-filter-empty]");
    if (!list) {
      return;
    }
    const items = Array.from(list.querySelectorAll("[data-search]"));
    const initialCount = counter ? counter.textContent : "";
    input.addEventListener("input", () => {
      const query = normalize(input.value);
      const visible = items.filter((item) => {
        const match = !query || normalize(item.dataset.search).includes(query);
        item.hidden = !match;
        return match;
      });
      if (counter) {
        counter.textContent = query
          ? `${visible.length} von ${items.length} Universitäten`
          : initialCount;
      }
      if (empty) {
        empty.hidden = visible.length > 0;
      }
    });
  };

  const openFromHash = () => {
    const id = decodeURIComponent(window.location.hash.slice(1));
    const target = id ? document.getElementById(id) : null;
    if (target && target.tagName === "DETAILS") {
      target.open = true;
    }
  };

  const sizeRunners = () => {
    document.querySelectorAll(".runner").forEach((runner) => {
      runner.style.setProperty(
        "--track",
        `${runner.parentElement.clientWidth}px`,
      );
    });
  };

  const init = () => {
    const today = startOfToday();
    document
      .querySelectorAll("[data-countdown]")
      .forEach((element) => initCountdown(element, today));
    document
      .querySelectorAll("[data-today-chart]")
      .forEach((chart) => initTodayMarker(chart, today));
    document.querySelectorAll("input[data-filter]").forEach(initFilter);
    openFromHash();
    sizeRunners();
    window.addEventListener("hashchange", openFromHash);
    window.addEventListener("resize", sizeRunners);
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
