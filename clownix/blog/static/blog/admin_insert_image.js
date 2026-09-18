(function () {
  "use strict";

  function getBodyField() {
    var byId = document.getElementById("id_body");
    if (byId) return byId;
    var els = document.getElementsByName("body");
    return els.length ? els[0] : null;
  }

  function insertAtCursor(textarea, text) {
    var start = textarea.selectionStart;
    var end = textarea.selectionEnd;
    var before = textarea.value.slice(0, start);
    var after = textarea.value.slice(end);
    var sep = "";
    if (before.length && !before.endsWith("\n")) sep = "\n";
    if (after.length && !after.startsWith("\n")) after = "\n" + after;
    var insert = sep + text + after;
    textarea.value = before + insert;
    var pos = before.length + sep.length + text.length;
    textarea.selectionStart = textarea.selectionEnd = pos;
    textarea.focus();
    textarea.dispatchEvent(new Event("input", { bubbles: true }));
    textarea.dispatchEvent(new Event("change", { bubbles: true }));
  }

  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".insert-img-btn");
    if (!btn) return;
    e.preventDefault();
    var placeholder = btn.getAttribute("data-placeholder");
    if (!placeholder) return;
    var ta = getBodyField();
    if (!ta) {
      window.alert("Не найдено поле «Текст статьи» (id_body).");
      return;
    }
    insertAtCursor(ta, placeholder);
  });
})();
