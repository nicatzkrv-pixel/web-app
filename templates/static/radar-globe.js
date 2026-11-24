// Fintech Radar: the live radar globe in the hero.
// A dotted globe (real coastlines) turning slowly, a radar sweep, and one blip per item at its country.
// Blip colours: saffron = Azerbaijan, coral = nearby markets, ice blue = global.
// No dependencies. 2D canvas. Pauses off-screen, in hidden tabs, on request, and under reduced motion.
import { LAND, LAKES } from "./radar-geo.js";

const DEG = Math.PI / 180;
const REGION_COLOUR = { Azerbaijan: "#ffb23f", Nearby: "#ff7a5c", Global: "#86cdff" };
const BAKU = { lon: 49.87, lat: 40.41 };

function landMask() {
  const w = 720, h = 360, c = document.createElement("canvas");
  c.width = w; c.height = h;
  const x = c.getContext("2d", { willReadFrequently: true });
  const fill = (poly, off) => {
    x.beginPath();
    x.moveTo(((poly[0] + 180 + off) / 360) * w, ((90 - poly[1]) / 180) * h);
    for (let i = 2; i < poly.length; i += 2) x.lineTo(((poly[i] + 180 + off) / 360) * w, ((90 - poly[i + 1]) / 180) * h);
    x.closePath(); x.fill();
  };
  x.fillStyle = "#fff";
  for (const off of [-360, 0, 360]) for (const p of LAND) fill(p, off);
  x.globalCompositeOperation = "destination-out";
  for (const p of LAKES) fill(p, 0);
  const d = x.getImageData(0, 0, w, h).data;
  return (lon, lat) => {
    const u = Math.floor(((lon + 180) / 360) * w) % w, v = Math.min(h - 1, Math.max(0, Math.floor(((90 - lat) / 180) * h)));
    return d[(v * w + ((u + w) % w)) * 4 + 3] > 127;
  };
}

function lattice(n, isLand) {
  // Fibonacci sphere; keep land points and a sparse sea
  const pts = [], golden = Math.PI * (3 - Math.sqrt(5));
  for (let i = 0; i < n; i++) {
    const y = 1 - (i / (n - 1)) * 2, r = Math.sqrt(1 - y * y), t = golden * i;
    const lat = Math.asin(y) / DEG, lon = Math.atan2(Math.sin(t) * r, Math.cos(t) * r) / DEG;
    const land = isLand(lon, lat);
    if (land || i % 7 === 0) pts.push({ lon, lat, land });
  }
  return pts;
}

export function mountGlobe(root) {
  const canvas = root.querySelector("canvas");
  const tip = root.querySelector("[data-globe-tip]");
  const pauseBtn = document.querySelector("[data-motion-toggle]");
  const dataEl = document.getElementById("radar-points");
  const points = dataEl ? JSON.parse(dataEl.textContent) : [];
  const ctx = canvas.getContext("2d");
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  const dots = lattice(9000, landMask());

  let size = 0, dpr = 1, cx = 0, cy = 0, R = 0;
  let lon0 = BAKU.lon + 8, targetLon = null, tilt = 24 * DEG;
  let sweep = -Math.PI / 2, last = performance.now(), born = last;
  let running = !reduce.matches, visible = true, userPaused = false;
  let hover = null, focusId = null;
  const flash = new Map(); // id -> time the sweep last crossed it

  function resize() {
    const box = canvas.getBoundingClientRect();
    dpr = Math.min(2, window.devicePixelRatio || 1);
    size = Math.max(10, Math.min(box.width, box.height));
    canvas.width = Math.round(box.width * dpr); canvas.height = Math.round(box.height * dpr);
    cx = box.width / 2; cy = box.height / 2; R = size * 0.42;
    draw(performance.now());
  }

  function project(lon, lat) {
    const l = (lon - lon0) * DEG, p = lat * DEG;
    const cosp = Math.cos(p), sinp = Math.sin(p), cosl = Math.cos(l);
    const x = cosp * Math.sin(l);
    const y = Math.cos(tilt) * sinp - Math.sin(tilt) * cosp * cosl;
    const z = Math.sin(tilt) * sinp + Math.cos(tilt) * cosp * cosl;
    return { x: cx + x * R, y: cy - y * R, z };
  }

  function draw(now) {
    const t = (now - born) / 1000;
    const intro = reduce.matches ? 1 : Math.min(1, t / 1.4);
    const ease = 1 - Math.pow(1 - intro, 4);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // halo and body
    const haloR = Math.min(R * 1.45, size / 2 - 1);
    const halo = ctx.createRadialGradient(cx, cy, R * 0.75, cx, cy, haloR);
    halo.addColorStop(0, "rgba(120,190,255,0.16)"); halo.addColorStop(1, "rgba(120,190,255,0)");
    ctx.fillStyle = halo; ctx.beginPath(); ctx.arc(cx, cy, haloR, 0, Math.PI * 2); ctx.fill();
    const body = ctx.createRadialGradient(cx - R * 0.35, cy - R * 0.4, R * 0.1, cx, cy, R);
    body.addColorStop(0, "#17305e"); body.addColorStop(1, "#081633");
    ctx.globalAlpha = ease; ctx.fillStyle = body; ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.fill();

    // range rings and bezel ticks
    ctx.strokeStyle = "rgba(159,243,230,0.10)"; ctx.lineWidth = 1;
    for (const k of [0.33, 0.66]) { ctx.beginPath(); ctx.arc(cx, cy, R * k, 0, Math.PI * 2); ctx.stroke(); }
    ctx.strokeStyle = "rgba(159,243,230,0.28)";
    ctx.beginPath(); ctx.arc(cx, cy, R * 1.06, 0, Math.PI * 2); ctx.stroke();
    for (let a = 0; a < 360; a += 5) {
      const long = a % 30 === 0, r1 = R * 1.06, r2 = R * (long ? 1.12 : 1.09), ang = a * DEG;
      ctx.globalAlpha = ease * (long ? 0.55 : 0.25);
      ctx.beginPath(); ctx.moveTo(cx + Math.cos(ang) * r1, cy + Math.sin(ang) * r1);
      ctx.lineTo(cx + Math.cos(ang) * r2, cy + Math.sin(ang) * r2); ctx.stroke();
    }
    ctx.globalAlpha = 1;

    // dots
    for (const d of dots) {
      const p = project(d.lon, d.lat);
      if (p.z <= 0) continue;
      const a = (d.land ? 0.2 + 0.75 * p.z : 0.08 * p.z) * ease;
      ctx.fillStyle = d.land ? `rgba(205,226,255,${a.toFixed(3)})` : `rgba(140,180,230,${a.toFixed(3)})`;
      const r = d.land ? 0.55 + 0.75 * p.z : 0.6;
      ctx.fillRect(p.x - r, p.y - r, r * 2, r * 2);
    }

    // sweep wedge
    if (ctx.createConicGradient) {
      const g = ctx.createConicGradient(sweep - 0.9, cx, cy);
      g.addColorStop(0, "rgba(159,243,230,0)");
      g.addColorStop(0.142, "rgba(159,243,230,0.20)");
      g.addColorStop(0.1432, "rgba(159,243,230,0)");
      g.addColorStop(1, "rgba(159,243,230,0)");
      ctx.save(); ctx.globalAlpha = ease; ctx.beginPath(); ctx.arc(cx, cy, R * 1.06, 0, Math.PI * 2); ctx.clip();
      ctx.fillStyle = g; ctx.fillRect(cx - R * 1.1, cy - R * 1.1, R * 2.2, R * 2.2); ctx.restore();
      ctx.strokeStyle = `rgba(159,243,230,${0.55 * ease})`; ctx.lineWidth = 1.2;
      ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + Math.cos(sweep) * R * 1.06, cy + Math.sin(sweep) * R * 1.06); ctx.stroke();
    }

    // Baku
    const b = project(BAKU.lon, BAKU.lat);
    if (b.z > 0) {
      const phase = reduce.matches ? 0.4 : (t % 2.4) / 2.4;
      ctx.strokeStyle = `rgba(255,178,63,${(1 - phase) * 0.7 * ease})`; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.arc(b.x, b.y, 6 + phase * 22, 0, Math.PI * 2); ctx.stroke();
      ctx.font = "600 12px 'Geist Mono', ui-monospace, monospace"; ctx.fillStyle = `rgba(255,214,150,${0.9 * ease})`;
      ctx.fillText("BAKU", b.x + 12, b.y - 12);
    }

    // blips
    const screen = [];
    points.forEach((pt, i) => {
      const p = project(pt.lon, pt.lat);
      if (p.z <= 0.05) return;
      const appear = reduce.matches ? 1 : Math.min(1, Math.max(0, (t - 0.9 - i * 0.06) / 0.35));
      if (appear <= 0) return;
      const ang = Math.atan2(p.y - cy, p.x - cx);
      const diff = ((sweep - ang) % (Math.PI * 2) + Math.PI * 2) % (Math.PI * 2);
      if (diff < 0.05 && running) flash.set(pt.id, now);
      const since = (now - (flash.get(pt.id) || -1e9)) / 1000;
      const col = REGION_COLOUR[pt.region] || REGION_COLOUR.Global;
      const hot = pt.id === hover || pt.id === focusId;
      const pop = appear < 1 ? 1 + Math.sin(appear * Math.PI) * 0.8 : 1;
      const r = (2.6 + (pt.score - 6) * 0.45) * pop * (hot ? 1.5 : 1);
      if (since < 1.6) {
        ctx.strokeStyle = col; ctx.globalAlpha = (1 - since / 1.6) * 0.8; ctx.lineWidth = 1.4;
        ctx.beginPath(); ctx.arc(p.x, p.y, r + since * 16, 0, Math.PI * 2); ctx.stroke();
      }
      if (hot) {
        ctx.strokeStyle = col; ctx.globalAlpha = 0.9; ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.arc(p.x, p.y, r + 6, 0, Math.PI * 2); ctx.stroke();
      }
      ctx.globalAlpha = appear * (0.35 + 0.65 * p.z);
      const glow = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, r * 3.2);
      glow.addColorStop(0, col); glow.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(p.x, p.y, r * 3.2, 0, Math.PI * 2); ctx.fill();
      ctx.globalAlpha = appear; ctx.fillStyle = col; ctx.beginPath(); ctx.arc(p.x, p.y, r, 0, Math.PI * 2); ctx.fill();
      ctx.globalAlpha = 1;
      screen.push({ pt, x: p.x, y: p.y, r });
    });
    draw.screen = screen;
  }

  function tick(now) {
    const dt = Math.min(0.05, (now - last) / 1000); last = now;
    if (running && visible) {
      if (targetLon !== null) {
        let delta = ((targetLon - lon0 + 540) % 360) - 180;
        lon0 += delta * Math.min(1, dt * 3.2);
        if (Math.abs(delta) < 0.2) lon0 = targetLon;
      } else if (now - born > 3200) {
        lon0 += dt * 4.5;
      }
      sweep += dt * 1.15;
      draw(now);
    }
    requestAnimationFrame(tick);
  }

  function nearest(evt) {
    const box = canvas.getBoundingClientRect();
    const x = evt.clientX - box.left, y = evt.clientY - box.top;
    let best = null, bestD = 18;
    for (const s of draw.screen || []) {
      const d = Math.hypot(s.x - x, s.y - y);
      if (d < bestD) { best = s; bestD = d; }
    }
    return best;
  }

  function showTip(s) {
    if (!s) { tip.hidden = true; hover = null; canvas.style.cursor = ""; return; }
    hover = s.pt.id; canvas.style.cursor = "pointer";
    tip.querySelector("[data-tip-where]").textContent = s.pt.place;
    tip.querySelector("[data-tip-score]").textContent = s.pt.score.toFixed(1);
    tip.querySelector("[data-tip-idea]").textContent = s.pt.idea;
    tip.dataset.region = s.pt.region;
    tip.hidden = false;
    const box = root.getBoundingClientRect(), cb = canvas.getBoundingClientRect();
    const left = Math.min(box.width - tip.offsetWidth - 8, Math.max(8, s.x + cb.left - box.left - tip.offsetWidth / 2));
    tip.style.left = left + "px";
    tip.style.top = Math.max(8, s.y + cb.top - box.top - tip.offsetHeight - 16) + "px";
    if (!running) draw(performance.now());
  }

  canvas.addEventListener("pointermove", (e) => showTip(nearest(e)));
  canvas.addEventListener("pointerleave", () => showTip(null));
  canvas.addEventListener("click", (e) => {
    const s = nearest(e);
    if (!s) return;
    const target = document.getElementById(s.pt.anchor);
    if (target) {
      target.scrollIntoView({ behavior: reduce.matches ? "auto" : "smooth", block: "center" });
      target.classList.remove("is-pinged"); void target.offsetWidth; target.classList.add("is-pinged");
    }
  });

  // hovering an item turns the globe to it and lights its blip
  document.querySelectorAll("[data-item][data-blip]").forEach((el) => {
    el.addEventListener("pointerenter", () => {
      const pt = points.find((p) => p.id === el.dataset.blip);
      if (!pt) return;
      focusId = pt.id; targetLon = pt.lon;
      if (!running) { lon0 = pt.lon; draw(performance.now()); }
    });
    el.addEventListener("pointerleave", () => { focusId = null; targetLon = null; if (!running) draw(performance.now()); });
  });

  function setRunning(on) {
    running = on && !reduce.matches;
    document.documentElement.classList.toggle("is-paused", !running);
    if (pauseBtn) {
      pauseBtn.setAttribute("aria-pressed", String(!running));
      pauseBtn.querySelector("[data-motion-label]").textContent = running ? pauseBtn.dataset.pause : pauseBtn.dataset.play;
    }
    last = performance.now();
    draw(last);
  }
  if (pauseBtn) pauseBtn.addEventListener("click", () => { userPaused = !userPaused; setRunning(!userPaused); });
  reduce.addEventListener?.("change", () => setRunning(!userPaused));
  document.addEventListener("visibilitychange", () => { visible = !document.hidden; last = performance.now(); });
  if ("IntersectionObserver" in window) {
    new IntersectionObserver((es) => { visible = es[0].isIntersecting; last = performance.now(); }).observe(root);
  }
  new ResizeObserver(resize).observe(canvas);
  resize();
  setRunning(!userPaused);
  requestAnimationFrame(tick);
}

const root = document.querySelector("[data-globe]");
if (root) mountGlobe(root);
