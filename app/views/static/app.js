(function () {
  const form = document.getElementById("search-form");
  const submitBtn = document.getElementById("submit-btn");

  if (form && submitBtn) {
    form.addEventListener("submit", function () {
      submitBtn.disabled = true;
      submitBtn.textContent = "Searching…";
      form.classList.add("is-loading");
    });

    window.addEventListener("pageshow", function (ev) {
      if (ev.persisted) {
        submitBtn.disabled = false;
        submitBtn.textContent = "Find words";
        form.classList.remove("is-loading");
      }
    });
  }

  function wordsFromTable(tableSelector) {
    const table = document.querySelector(tableSelector);
    if (!table) {
      return [];
    }
    const cells = table.querySelectorAll("tbody .word-cell");
    return Array.from(cells, function (td) {
      return td.textContent.trim();
    }).filter(Boolean);
  }

  function tableAsTsv(tableSelector) {
    const table = document.querySelector(tableSelector);
    if (!table) {
      return "";
    }
    const rows = table.querySelectorAll("tr");
    const lines = [];
    rows.forEach(function (row) {
      const cells = row.querySelectorAll("th, td");
      const parts = Array.from(cells, function (cell) {
        return cell.innerText.replace(/\s+/g, " ").trim();
      });
      lines.push(parts.join("\t"));
    });
    return lines.join("\n");
  }

  async function copyText(text, button) {
    if (!text) {
      return;
    }
    const prev = button.textContent;
    try {
      await navigator.clipboard.writeText(text);
      button.textContent = "Copied";
      setTimeout(function () {
        button.textContent = prev;
      }, 1500);
    } catch {
      button.textContent = "Copy failed";
      setTimeout(function () {
        button.textContent = prev;
      }, 2000);
    }
  }

  document.querySelectorAll(".copy-words-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const sel = btn.getAttribute("data-table");
      if (!sel) {
        return;
      }
      const text = wordsFromTable(sel).join("\n");
      copyText(text, btn);
    });
  });

  document.querySelectorAll(".copy-tsv-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const sel = btn.getAttribute("data-table");
      if (!sel) {
        return;
      }
      copyText(tableAsTsv(sel), btn);
    });
  });
})();
