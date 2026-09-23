/* =========================================================
   TalentSphere Elevate — Auth logic
   Handles: role tabs, validation, captcha, slide-verify,
   password strength, elevation meter. On submit, once every
   client-side check passes, the form is posted for real to
   the Django backend (accounts/views.py).
========================================================= */

(function () {
  "use strict";

  /* ---------- Role tabs (Candidate / Recruiter) ---------- */
  const roleTabs = document.querySelectorAll(".role-tab");
  const roleInput = document.getElementById("role");
  let currentRole = roleInput ? roleInput.value : "candidate";

  roleTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      roleTabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      currentRole = tab.dataset.role;
      if (roleInput) roleInput.value = currentRole;
      updateElevation();
    });
  });

  /* ---------- Helpers ---------- */
  const $ = (id) => document.getElementById(id);

  function setFieldState(input, hintEl, ok, message) {
    if (!input) return;
    input.classList.toggle("valid", ok === true);
    input.classList.toggle("invalid", ok === false);
    if (hintEl) {
      hintEl.textContent = message || "";
      hintEl.className = "hint" + (ok === false ? " error" : ok === true ? " ok" : "");
    }
  }

  /* ---------- Field validators (reused across pages) ---------- */

  function validateUsername() {
    const el = $("username");
    if (!el) return true;
    const val = el.value.trim();
    const ok = /^[a-zA-Z0-9_.]{4,20}$/.test(val);
    setFieldState(el, $("usernameHint"), val.length === 0 ? null : ok,
      ok ? "Username looks good." : "4–20 characters: letters, numbers, . or _ only.");
    return ok;
  }

  function validateEmail() {
    const el = $("email");
    if (!el) return true;
    const val = el.value.trim();
    const ok = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(val);
    setFieldState(el, $("emailHint"), val.length === 0 ? null : ok,
      ok ? "Email verified format." : "Enter a valid email address.");
    return ok;
  }

  /* ---------- THE FIX: exactly 10 digits, not 7–12 ---------- */
  function validatePhone() {
    const el = $("phone");
    if (!el) return true;
    const digits = el.value.replace(/\D/g, "");
    const ok = digits.length === 10;
    setFieldState(el, $("phoneHint"), el.value.length === 0 ? null : ok,
      ok ? "Phone number accepted." : "Enter exactly 10 digits, no letters.");
    return ok;
  }

  function scorePassword(pw) {
    let score = 0;
    if (pw.length >= 8) score++;
    if (pw.length >= 12) score++;
    if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score++;
    if (/\d/.test(pw)) score++;
    if (/[^A-Za-z0-9]/.test(pw)) score++;
    return score; // 0-5
  }

  function validatePassword() {
    const el = $("password");
    if (!el) return true;
    const pw = el.value;
    const score = scorePassword(pw);
    const fill = $("strengthFill");
    if (fill) {
      const pct = (score / 5) * 100;
      fill.style.width = pct + "%";
      fill.style.background =
        score <= 1 ? "#E5697A" : score <= 3 ? "#E4C355" : "#58C99A";
    }
    const ok = pw.length === 0 ? null : score >= 3 && pw.length >= 8;
    setFieldState(el, $("passwordHint"), ok,
      pw.length === 0 ? "" :
      ok ? "Strong password." : "Use 8+ chars, mixed case, a number and a symbol.");
    validateConfirm();
    return ok === true;
  }

  function validateConfirm() {
    const el = $("confirmPassword");
    if (!el) return true;
    const pw = $("password") ? $("password").value : "";
    const val = el.value;
    const ok = val.length === 0 ? null : val === pw && val.length > 0;
    setFieldState(el, $("confirmHint"), ok,
      val.length === 0 ? "" : ok ? "Passwords match." : "Passwords do not match.");
    return ok === true;
  }

  /* ---------- Math captcha (front-end UX gate) ---------- */
  let captchaAnswer = null;

  function newCaptcha() {
    const a = Math.floor(Math.random() * 9) + 1;
    const b = Math.floor(Math.random() * 9) + 1;
    const ops = ["+", "−"];
    const op = a >= b ? ops[Math.floor(Math.random() * 2)] : "+";
    captchaAnswer = op === "+" ? a + b : a - b;
    const eq = $("captchaEquation");
    if (eq) eq.textContent = `${a} ${op} ${b} = ?`;
    const input = $("captchaInput");
    if (input) {
      input.value = "";
      setFieldState(input, $("captchaHint"), null, "");
    }
  }

  function validateCaptcha() {
    const el = $("captchaInput");
    if (!el) return true;
    if (el.value.trim() === "") {
      setFieldState(el, $("captchaHint"), null, "");
      return false;
    }
    const ok = parseInt(el.value.trim(), 10) === captchaAnswer;
    setFieldState(el, $("captchaHint"), ok, ok ? "Correct." : "That's not quite right.");
    return ok;
  }

  const refreshBtn = $("captchaRefresh");
  if (refreshBtn) {
    refreshBtn.addEventListener("click", () => {
      refreshBtn.classList.add("spin");
      newCaptcha();
      updateElevation();
      setTimeout(() => refreshBtn.classList.remove("spin"), 300);
    });
  }

  /* ---------- Slide-to-verify (human check) ---------- */
  let humanVerified = false;

  function initSlideVerify() {
    const wrap = $("slideVerify");
    if (!wrap) return;
    const handle = $("slideHandle");
    const label = $("slideLabel");
    const fill = $("slideFill");
    const maxX = wrap.clientWidth - handle.clientWidth;
    let dragging = false;
    let startX = 0;
    let currentX = 0;

    function pointerX(e) {
      return (e.touches ? e.touches[0].clientX : e.clientX);
    }

    function onDown(e) {
      if (humanVerified) return;
      dragging = true;
      startX = pointerX(e) - currentX;
    }

    function onMove(e) {
      if (!dragging) return;
      let x = pointerX(e) - startX;
      x = Math.max(0, Math.min(x, maxX));
      currentX = x;
      handle.style.left = x + "px";
      fill.style.width = (x + handle.clientWidth) + "px";
      if (x >= maxX - 2) {
        dragging = false;
        humanVerified = true;
        wrap.classList.add("verified");
        label.textContent = "Verified — you're human";
        updateElevation();
      }
    }

    function onUp() {
      dragging = false;
      if (!humanVerified) {
        currentX = 0;
        handle.style.left = "0px";
        fill.style.width = handle.clientWidth + "px";
      }
    }

    handle.addEventListener("mousedown", onDown);
    handle.addEventListener("touchstart", onDown, { passive: true });
    window.addEventListener("mousemove", onMove);
    window.addEventListener("touchmove", onMove, { passive: true });
    window.addEventListener("mouseup", onUp);
    window.addEventListener("touchend", onUp);
  }

  /* ---------- Elevation meter (signature element) ----------
     Rises as real verification steps are satisfied. On signup
     it tracks username/email/phone/password/captcha/human.
     On login it tracks identifier/password/captcha only. */

  function updateElevation() {
    const meterFill = $("meterFill");
    if (!meterFill) return;

    const page = document.body.dataset.page;
    let total = 0;
    let done = 0;

    if (page === "signup") {
      const checks = [
        validateUsername(),
        validateEmail(),
        validatePhone(),
        (function () {
          const pw = $("password") ? $("password").value : "";
          return scorePassword(pw) >= 3 && pw.length >= 8;
        })(),
        validateConfirm(),
        validateCaptcha(),
        humanVerified,
      ];
      total = checks.length;
      done = checks.filter(Boolean).length;
    } else if (page === "login") {
      const idEl = $("identifier");
      const pwEl = $("loginPassword");
      const checks = [
        idEl ? idEl.value.trim().length > 2 : false,
        pwEl ? pwEl.value.length >= 6 : false,
        validateCaptcha(),
      ];
      total = checks.length;
      done = checks.filter(Boolean).length;
    }

    const pct = total ? Math.max(4, (done / total) * 100) : 4;
    meterFill.style.height = pct + "%";

    const submitBtn = $("submitBtn");
    if (submitBtn) submitBtn.disabled = done < total;
  }

  /* ---------- Wire up live validation ---------- */
  ["username", "email", "phone", "password", "confirmPassword", "captchaInput"]
    .forEach((id) => {
      const el = $(id);
      if (!el) return;
      el.addEventListener("input", () => {
        if (id === "password") validatePassword();
        else if (id === "confirmPassword") validateConfirm();
        else if (id === "username") validateUsername();
        else if (id === "email") validateEmail();
        else if (id === "phone") validatePhone();
        else if (id === "captchaInput") validateCaptcha();
        updateElevation();
      });
    });

  ["identifier", "loginPassword"].forEach((id) => {
    const el = $(id);
    if (!el) return;
    el.addEventListener("input", updateElevation);
  });

  /* Password visibility toggles */
  document.querySelectorAll(".toggle-visibility").forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = $(btn.dataset.target);
      if (!target) return;
      const isPw = target.type === "password";
      target.type = isPw ? "text" : "password";
      btn.textContent = isPw ? "HIDE" : "SHOW";
    });
  });

  /* ---------- Form submit — real POST to Django ---------- */
  const form = document.getElementById("authForm");
  if (form) {
    form.addEventListener("submit", (e) => {
      updateElevation();
      const submitBtn = $("submitBtn");
      if (submitBtn && submitBtn.disabled) {
        e.preventDefault();
        return;
      }
      // All client checks passed — let the browser submit the form
      // normally (POST to the Django view). No preventDefault here.
      submitBtn.textContent = document.body.dataset.page === "signup" ? "Creating account…" : "Signing in…";
      submitBtn.disabled = true;
      // Re-enable slightly later in case Django redisplays the form with errors.
      setTimeout(() => { submitBtn.disabled = false; }, 4000);
    });
  }

  function showToast(message) {
    const toast = $("toast");
    if (!toast) return;
    toast.textContent = "";
    toast.appendChild(document.createTextNode(message));
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 3600);
  }
  window.showToast = showToast;

  /* ---------- Init ---------- */
  newCaptcha();
  initSlideVerify();
  updateElevation();
})();
