(function () {
  "use strict";

  var data = JSON.parse(document.getElementById("shop-data").textContent);
  var t = data.t;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function formatTenge(n) {
    return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, " ") + " ₸";
  }

  function totalPrice(q) {
    return Math.floor(q / 2) * data.priceTwo + (q % 2) * data.priceOne;
  }

  /* Reveal on scroll */
  var revealed = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add("is-in");
          io.unobserve(e.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
    revealed.forEach(function (el) { io.observe(el); });
  } else {
    revealed.forEach(function (el) { el.classList.add("is-in"); });
  }

  /* Nav border + mobile buy bar */
  var nav = document.getElementById("nav");
  var buybar = document.getElementById("buybar");
  var hero = document.querySelector(".hero");
  function onScroll() {
    var y = window.scrollY;
    nav.classList.toggle("is-scrolled", y > 8);
    buybar.classList.toggle("is-visible", y > hero.offsetHeight * 0.7);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* Hero color swatches */
  var selectedColor = document.querySelector(".swatch").dataset.color;
  document.querySelectorAll(".swatch").forEach(function (sw) {
    sw.addEventListener("click", function () {
      selectedColor = sw.dataset.color;
      document.querySelectorAll(".swatch").forEach(function (s) {
        s.setAttribute("aria-checked", s === sw ? "true" : "false");
      });
      hero.style.setProperty("--holder", sw.style.getPropertyValue("--c"));
      hero.classList.remove("is-swapping");
      void hero.offsetWidth;
      hero.classList.add("is-swapping");
    });
  });

  /* Order sheet */
  var dialog = document.getElementById("order");
  var form = document.getElementById("order-form");
  var errorBox = document.getElementById("form-error");
  var payBtn = document.getElementById("pay-btn");
  var picks = Array.prototype.slice.call(dialog.querySelectorAll(".pick"));
  var counts = {};
  picks.forEach(function (p) { counts[p.dataset.color] = 0; });

  function quantity() {
    return Object.keys(counts).reduce(function (sum, k) { return sum + counts[k]; }, 0);
  }

  function render() {
    picks.forEach(function (p) {
      var c = counts[p.dataset.color];
      var out = p.querySelector("output");
      if (out.textContent !== String(c)) {
        out.textContent = c;
        out.classList.remove("bump");
        void out.offsetWidth;
        out.classList.add("bump");
      }
      p.classList.toggle("is-active", c > 0);
      p.querySelector('[data-step="-1"]').disabled = c === 0;
    });
    var q = quantity();
    document.getElementById("total-qty").textContent = q;
    document.getElementById("total-sum").textContent = formatTenge(totalPrice(q));
    dialog.querySelectorAll('[data-step="1"]').forEach(function (b) { b.disabled = q >= data.maxQuantity; });
  }

  picks.forEach(function (p) {
    p.querySelectorAll("[data-step]").forEach(function (b) {
      b.addEventListener("click", function () {
        var next = counts[p.dataset.color] + Number(b.dataset.step);
        if (next < 0 || (Number(b.dataset.step) > 0 && quantity() >= data.maxQuantity)) return;
        counts[p.dataset.color] = next;
        hideError();
        render();
      });
    });
  });

  function openSheet(qty) {
    if (qty || quantity() === 0) {
      Object.keys(counts).forEach(function (k) { counts[k] = 0; });
      counts[selectedColor] = qty || 1;
    }
    render();
    dialog.classList.remove("is-closing");
    dialog.showModal();
    document.body.style.overflow = "hidden";
  }

  function closeSheet() {
    if (!dialog.open) return;
    if (reduceMotion) { dialog.close(); return; }
    dialog.classList.add("is-closing");
    setTimeout(function () { dialog.classList.remove("is-closing"); dialog.close(); }, 280);
  }

  dialog.addEventListener("close", function () { document.body.style.overflow = ""; });
  dialog.addEventListener("cancel", function (e) { e.preventDefault(); closeSheet(); });
  dialog.addEventListener("click", function (e) { if (e.target === dialog) closeSheet(); });
  dialog.querySelector("[data-close]").addEventListener("click", closeSheet);
  document.querySelectorAll("[data-buy]").forEach(function (b) {
    b.addEventListener("click", function () { openSheet(Number(b.dataset.qty) || 0); });
  });

  /* Phone mask: +7 7XX XXX XX XX */
  var phone = form.elements.phone;
  phone.addEventListener("focus", function () { if (!phone.value) phone.value = "+7 "; });
  phone.addEventListener("input", function () {
    var d = phone.value.replace(/\D/g, "");
    if (/^\s*\+7/.test(phone.value)) d = d.slice(1);
    if (d.length === 11 && /^[78]/.test(d)) d = d.slice(1);
    if (d.charAt(0) === "8") d = d.slice(1);  // trunk prefix typed after +7
    d = d.slice(0, 10);
    var parts = [d.slice(0, 3), d.slice(3, 6), d.slice(6, 8), d.slice(8, 10)].filter(Boolean);
    phone.value = "+7 " + parts.join(" ");
  });

  function showError(msg) {
    errorBox.textContent = msg;
    errorBox.hidden = false;
    var foot = form.querySelector(".sheet-foot");
    foot.classList.remove("shake");
    void foot.offsetWidth;
    foot.classList.add("shake");
  }
  function hideError() { errorBox.hidden = true; }

  form.addEventListener("input", function (e) {
    var field = e.target.closest(".field");
    if (field) field.classList.remove("is-invalid");
    hideError();
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (quantity() === 0) return showError(t.err_items);

    var missing = false;
    ["name", "phone", "city", "address"].forEach(function (name) {
      var input = form.elements[name];
      var empty = !input.value.trim() || (name === "phone" && input.value.replace(/\D/g, "").length < 11);
      input.closest(".field").classList.toggle("is-invalid", empty);
      missing = missing || empty;
    });
    if (missing) {
      var digits = phone.value.replace(/\D/g, "");
      return showError(digits.length > 1 && digits.length < 11 ? t.err_phone : t.err_fields);
    }

    var items = {};
    Object.keys(counts).forEach(function (k) { if (counts[k] > 0) items[k] = counts[k]; });
    payBtn.disabled = true;
    payBtn.textContent = t.paying;

    fetch("/api/order", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        lang: data.lang,
        items: items,
        name: form.elements.name.value,
        phone: phone.value,
        city: form.elements.city.value,
        address: form.elements.address.value
      })
    })
      .then(function (r) {
        return r.json().catch(function () { return {}; });
      })
      .then(function (body) {
        if (!body.order_url) throw { message: body.error || t.err_payment };
        window.location.href = body.order_url + "?pay=1";
      })
      .catch(function (err) {
        showError(err instanceof Error ? t.err_payment : err.message);
        payBtn.disabled = false;
        payBtn.textContent = t.pay;
      });
  });
})();
