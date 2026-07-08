/* beijing-vibe-trip · favorites (红心收藏) — drop-in module.
   Adds a heart to every favoritable item; persists selection to BOTH
   localStorage and the URL (?fav=a.b.c) so a shortlist is bookmarkable/shareable.
   Zero deps. Include after the page body:
     <link rel="stylesheet" href="../assets/favorites.css">
     <script src="../assets/favorites.js"></script>
   Optionally set window.FAV_SELECTORS before the script to override targets. */
(function () {
  "use strict";

  var SELECTORS = window.FAV_SELECTORS || [".act-card", ".mcell", ".fcard", "[data-fav]"];
  var PAGE_KEY = "bvt-fav:" + location.pathname.replace(/^.*\/pages\//, "");
  var URL_PARAM = "fav";

  // --- short stable id from an item's label text ---
  function hash(s) {
    var h = 5381, i = s.length;
    while (i) h = (h * 33) ^ s.charCodeAt(--i);
    return (h >>> 0).toString(36).slice(0, 6);
  }
  function labelFor(el) {
    // explicit override wins
    if (el.getAttribute("data-fav-label")) return el.getAttribute("data-fav-label").trim();
    // matrix cell: use row+col headers for a human label
    if (el.classList.contains("mcell")) {
      var tr = el.closest("tr"), tbl = el.closest("table");
      var rowh = tr && tr.querySelector(".rowh .cap");
      var idx = Array.prototype.indexOf.call(tr.children, el); // includes rowheader at 0
      var colh = tbl && tbl.querySelectorAll("thead .colh")[idx - 1];
      var price = el.querySelector(".price");
      var parts = [];
      if (rowh) parts.push(rowh.textContent.trim());
      if (colh) parts.push(colh.querySelector(".cap") ? colh.querySelector(".cap").textContent.trim() : colh.textContent.trim());
      var lbl = parts.join(" × ");
      if (price) lbl += " · " + price.textContent.trim();
      // section context (甲米线 / 普吉线)
      var sec = el.closest("section"), h2 = sec && sec.querySelector("h2");
      if (h2) lbl = h2.textContent.replace(/^[^\u4e00-\u9fa5A-Za-z]+/, "").trim().split(/[·（(]/)[0].trim() + "：" + lbl;
      return lbl;
    }
    // activity / restaurant card: use its name
    var nm = el.querySelector(".act-nm, .fcard-title, h3, .name, strong");
    return nm ? nm.textContent.trim() : (el.textContent.trim().slice(0, 40));
  }

  var items = [];   // {el, id, label}
  var favSet = new Set();

  // --- storage <-> URL sync ---
  function readInitial() {
    var url = new URL(location.href);
    var fromUrl = (url.searchParams.get(URL_PARAM) || "").split(".").filter(Boolean);
    var fromLS = [];
    try { fromLS = JSON.parse(localStorage.getItem(PAGE_KEY) || "[]"); } catch (e) {}
    // URL wins if present (shared link), else localStorage
    var ids = fromUrl.length ? fromUrl : fromLS;
    ids.forEach(function (id) { favSet.add(id); });
  }
  function persist() {
    var ids = Array.from(favSet);
    try { localStorage.setItem(PAGE_KEY, JSON.stringify(ids)); } catch (e) {}
    var url = new URL(location.href);
    if (ids.length) url.searchParams.set(URL_PARAM, ids.join("."));
    else url.searchParams.delete(URL_PARAM);
    history.replaceState(null, "", url.toString());
  }

  // --- DOM wiring ---
  function makeHeart(item) {
    var b = document.createElement("button");
    b.className = "fav-btn" + (favSet.has(item.id) ? " on" : "");
    b.type = "button";
    b.title = "收藏 / 取消收藏";
    b.setAttribute("aria-label", "收藏 " + item.label);
    b.textContent = favSet.has(item.id) ? "♥" : "♡";
    b.addEventListener("click", function (ev) {
      ev.stopPropagation(); ev.preventDefault();
      toggle(item, b);
    });
    return b;
  }
  function applyState(item) {
    item.el.classList.toggle("is-fav", favSet.has(item.id));
    var b = item.el.querySelector(".fav-btn");
    if (b) { b.classList.toggle("on", favSet.has(item.id)); b.textContent = favSet.has(item.id) ? "♥" : "♡"; }
  }
  function toggle(item, btn) {
    if (favSet.has(item.id)) { favSet.delete(item.id); }
    else { favSet.add(item.id); item.el.classList.add("fav-pulse");
      setTimeout(function () { item.el.classList.remove("fav-pulse"); }, 1000); }
    applyState(item);
    persist(); renderDock();
    toast(favSet.has(item.id) ? "已收藏 · 已存入浏览器+链接" : "已取消收藏");
  }

  // --- floating dock ---
  var dock, pop, cntEl, onlyBtn;
  function buildDock() {
    dock = document.createElement("div");
    dock.className = "fav-dock";
    dock.innerHTML =
      '<button class="fav-dock-btn" type="button">♥ 收藏夹 <span class="cnt">0</span></button>' +
      '<div class="fav-pop">' +
      '  <h4>我的收藏</h4>' +
      '  <p class="sub">已存入浏览器，链接可分享/收藏</p>' +
      '  <div class="fav-list"></div>' +
      '  <div class="fav-acts">' +
      '    <button class="fav-only-btn" type="button">只看收藏</button>' +
      '    <button class="fav-copy-btn" type="button">复制分享链接</button>' +
      '    <button class="fav-clear-btn" type="button">清空</button>' +
      '  </div>' +
      '</div>';
    document.body.appendChild(dock);
    pop = dock.querySelector(".fav-pop");
    cntEl = dock.querySelector(".cnt");
    onlyBtn = dock.querySelector(".fav-only-btn");
    dock.querySelector(".fav-dock-btn").addEventListener("click", function () { pop.classList.toggle("open"); renderDock(); });
    onlyBtn.addEventListener("click", function () {
      document.body.classList.toggle("fav-only");
      onlyBtn.classList.toggle("active", document.body.classList.contains("fav-only"));
    });
    dock.querySelector(".fav-copy-btn").addEventListener("click", copyLink);
    dock.querySelector(".fav-clear-btn").addEventListener("click", clearAll);
    document.addEventListener("click", function (e) { if (!dock.contains(e.target)) pop.classList.remove("open"); });
  }
  function renderDock() {
    cntEl.textContent = favSet.size;
    var list = dock.querySelector(".fav-list");
    var favItems = items.filter(function (it) { return favSet.has(it.id); });
    if (!favItems.length) { list.innerHTML = '<div class="fav-empty">还没有收藏。点卡片/格子右上的 ♡ 即可收藏。</div>'; return; }
    list.innerHTML = "";
    favItems.forEach(function (it) {
      var row = document.createElement("div");
      row.className = "fav-row";
      row.innerHTML = '<span class="dot">♥</span><span class="lbl"></span><span class="fav-x" title="移除">✕</span>';
      row.querySelector(".lbl").textContent = it.label;
      row.querySelector(".lbl").addEventListener("click", function () {
        pop.classList.remove("open");
        it.el.scrollIntoView({ behavior: "smooth", block: "center" });
        it.el.classList.add("fav-pulse");
        setTimeout(function () { it.el.classList.remove("fav-pulse"); }, 1000);
      });
      row.querySelector(".fav-x").addEventListener("click", function (e) {
        e.stopPropagation(); favSet.delete(it.id); applyState(it); persist(); renderDock();
      });
      list.appendChild(row);
    });
  }
  function copyLink() {
    persist();
    var url = location.href;
    var done = function () { toast("分享链接已复制"); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(done, function () { prompt("复制此链接：", url); });
    else prompt("复制此链接：", url);
  }
  function clearAll() {
    favSet.clear();
    items.forEach(applyState);
    persist(); renderDock();
    document.body.classList.remove("fav-only"); onlyBtn.classList.remove("active");
    toast("已清空收藏");
  }
  var toastEl;
  function toast(msg) {
    if (!toastEl) { toastEl = document.createElement("div"); toastEl.className = "fav-toast"; document.body.appendChild(toastEl); }
    toastEl.textContent = msg; toastEl.classList.add("show");
    clearTimeout(toast._t); toast._t = setTimeout(function () { toastEl.classList.remove("show"); }, 1600);
  }

  // --- init ---
  function init() {
    readInitial();
    var seen = {};
    document.querySelectorAll(SELECTORS.join(",")).forEach(function (el) {
      if (el.classList.contains("fav-target")) return; // already wired
      var label = labelFor(el);
      if (!label) return;
      var id = hash(label);
      while (seen[id]) id = hash(label + "#" + (seen[id]++)); // collision guard
      seen[id] = (seen[id] || 0) + 1;
      var item = { el: el, id: id, label: label };
      items.push(item);
      el.classList.add("fav-target");
      el.appendChild(makeHeart(item));
      applyState(item);
    });
    buildDock();
    renderDock();
    // prune URL/LS ids that no longer exist on the page
    var valid = new Set(items.map(function (it) { return it.id; }));
    Array.from(favSet).forEach(function (id) { if (!valid.has(id)) favSet.delete(id); });
    persist();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
