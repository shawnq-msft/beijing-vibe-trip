/* beijing-vibe-trip · favorites (红心收藏) — drop-in module.
   Adds a heart to every favoritable item; persists selection to BOTH
   localStorage and the URL (?fav=a.b.c) so a shortlist is bookmarkable/shareable.
   Zero deps. Include after the page body:
     <link rel="stylesheet" href="../assets/favorites.css">
     <script src="../assets/favorites.js"></script>
   Optionally set window.FAV_SELECTORS before the script to override targets.

   Grouping: multiple DOM nodes sharing the same label (e.g. a venue's photo
   card AND its summary-table row) are grouped under one id, so favoriting from
   either place highlights both and counts once. */
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
    // summary-table row (restaurant / activity 总表): use data-name + tier/rating
    if (el.tagName === "TR") {
      var dn = el.getAttribute("data-name");
      var nameCell = el.querySelector(".c-name");
      var base = (dn || (nameCell ? nameCell.textContent.trim() : "")).trim();
      if (!base) return "";
      var tierEl = el.querySelector(".c-tier .tg, .c-tier");
      var gEl = el.querySelector(".c-g .gstar, .c-g");
      var extra = [];
      if (tierEl && tierEl.textContent.trim()) extra.push(tierEl.textContent.trim());
      if (gEl && gEl.textContent.trim()) extra.push("★" + gEl.textContent.trim());
      return base + (extra.length ? "（" + extra.join(" ") + "）" : "");
    }
    // activity / restaurant photo card: use its name (strip trailing rating/meta)
    var nm = el.querySelector(".fcard-name, .act-nm, .fcard-title, h3, .name, strong");
    if (nm) {
      // fcard-name may contain child spans (rating badges); take first text node
      var t = nm.firstChild && nm.firstChild.nodeType === 3 ? nm.firstChild.textContent : nm.textContent;
      return t.trim();
    }
    return el.textContent.trim().slice(0, 40);
  }
  // Key used to GROUP nodes of the same venue. For cards+rows we want the bare
  // venue name to match across both, so strip the row's tier/rating suffix.
  function groupKey(el, label) {
    if (el.tagName === "TR" && el.getAttribute("data-name")) return el.getAttribute("data-name").trim();
    // fcard: bare name already; strip any "（...）" suffix a row may have added
    return label.replace(/（[^）]*）\s*$/, "").trim();
  }

  var groups = {};      // id -> { id, label, els: [el, ...] }
  var groupList = [];   // insertion-ordered groups
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
  function makeHeart(group) {
    var b = document.createElement("button");
    b.className = "fav-btn" + (favSet.has(group.id) ? " on" : "");
    b.type = "button";
    b.title = "收藏 / 取消收藏";
    b.setAttribute("aria-label", "收藏 " + group.label);
    b.textContent = favSet.has(group.id) ? "♥" : "♡";
    b.addEventListener("click", function (ev) {
      ev.stopPropagation(); ev.preventDefault();
      toggle(group);
    });
    return b;
  }
  function applyState(group) {
    var on = favSet.has(group.id);
    group.els.forEach(function (el) {
      el.classList.toggle("is-fav", on);
      var b = el.querySelector(".fav-btn");
      if (b) { b.classList.toggle("on", on); b.textContent = on ? "♥" : "♡"; }
    });
  }
  function pulse(group) {
    group.els.forEach(function (el) {
      el.classList.add("fav-pulse");
      setTimeout(function () { el.classList.remove("fav-pulse"); }, 1000);
    });
  }
  function toggle(group) {
    if (favSet.has(group.id)) favSet.delete(group.id);
    else { favSet.add(group.id); pulse(group); }
    applyState(group);
    persist(); renderDock();
    toast(favSet.has(group.id) ? "已收藏 · 已存入浏览器+链接" : "已取消收藏");
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
    var favGroups = groupList.filter(function (g) { return favSet.has(g.id); });
    if (!favGroups.length) { list.innerHTML = '<div class="fav-empty">还没有收藏。点卡片/格子/表格行上的 ♡ 即可收藏。</div>'; return; }
    list.innerHTML = "";
    favGroups.forEach(function (g) {
      var row = document.createElement("div");
      row.className = "fav-row";
      row.innerHTML = '<span class="dot">♥</span><span class="lbl"></span><span class="fav-x" title="移除">✕</span>';
      row.querySelector(".lbl").textContent = g.label;
      row.querySelector(".lbl").addEventListener("click", function () {
        pop.classList.remove("open");
        // scroll to the first VISIBLE node of the group (card may be hidden in a collapsed section)
        var target = g.els.find(function (e) { return e.offsetParent !== null; }) || g.els[0];
        target.scrollIntoView({ behavior: "smooth", block: "center" });
        pulse(g);
      });
      row.querySelector(".fav-x").addEventListener("click", function (e) {
        e.stopPropagation(); favSet.delete(g.id); applyState(g); persist(); renderDock();
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
    groupList.forEach(applyState);
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
    document.querySelectorAll(SELECTORS.join(",")).forEach(function (el) {
      if (el.classList.contains("fav-target")) return; // already wired
      var label = labelFor(el);
      if (!label) return;
      var key = groupKey(el, label);
      var id = hash(key);
      var group = groups[id];
      if (!group) { group = { id: id, label: label, els: [] }; groups[id] = group; groupList.push(group); }
      group.els.push(el);
      el.classList.add("fav-target");
      // <tr> can't host a positioned child button directly; mount into first cell
      if (el.tagName === "TR") {
        var host = el.querySelector("td") || el;
        host.classList.add("fav-cell-host");
        host.appendChild(makeHeart(group));
      } else {
        el.appendChild(makeHeart(group));
      }
    });
    groupList.forEach(applyState);
    buildDock();
    renderDock();
    // prune URL/LS ids that no longer exist on the page
    var valid = new Set(groupList.map(function (g) { return g.id; }));
    Array.from(favSet).forEach(function (id) { if (!valid.has(id)) favSet.delete(id); });
    persist();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
