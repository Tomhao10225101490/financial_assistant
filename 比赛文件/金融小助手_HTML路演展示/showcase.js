const slides = Array.from(document.querySelectorAll(".slide"));
const slideCount = document.querySelector("#slideCount");
const canvas = document.querySelector("#sceneCanvas");
const ctx = canvas.getContext("2d", { alpha: true });

let current = 0;
let width = 0;
let height = 0;
let dpr = 1;
let raf = 0;
let points = [];
let reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function pad(value) {
  return String(value).padStart(2, "0");
}

function setSlide(index) {
  current = (index + slides.length) % slides.length;
  slides.forEach((slide, i) => slide.classList.toggle("is-active", i === current));
  slideCount.textContent = `${pad(current + 1)} / ${pad(slides.length)}`;
  slideCount.classList.remove("is-changing");
  void slideCount.offsetWidth;
  slideCount.classList.add("is-changing");
}

function getInitialSlide() {
  const slideNumber = Number.parseInt(new URLSearchParams(window.location.search).get("slide") || "1", 10);
  if (!Number.isFinite(slideNumber)) return 0;
  return Math.min(Math.max(slideNumber - 1, 0), slides.length - 1);
}

function next() {
  setSlide(current + 1);
}

function prev() {
  setSlide(current - 1);
}

window.addEventListener("keydown", (event) => {
  if (event.key === "ArrowRight" || event.key === " " || event.key === "PageDown") {
    event.preventDefault();
    next();
  }
  if (event.key === "ArrowLeft" || event.key === "PageUp") {
    event.preventDefault();
    prev();
  }
  if (event.key.toLowerCase() === "f") {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen?.();
    } else {
      document.exitFullscreen?.();
    }
  }
});

let touchStartX = 0;
window.addEventListener("touchstart", (event) => {
  touchStartX = event.touches[0]?.clientX ?? 0;
}, { passive: true });

window.addEventListener("touchend", (event) => {
  const endX = event.changedTouches[0]?.clientX ?? touchStartX;
  const delta = endX - touchStartX;
  if (Math.abs(delta) > 60) {
    delta < 0 ? next() : prev();
  }
}, { passive: true });

function resize() {
  dpr = Math.min(window.devicePixelRatio || 1, 2);
  width = window.innerWidth;
  height = window.innerHeight;
  canvas.width = Math.floor(width * dpr);
  canvas.height = Math.floor(height * dpr);
  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  const count = Math.max(50, Math.min(130, Math.floor((width * height) / 14000)));
  points = Array.from({ length: count }, () => ({
    x: Math.random() * width,
    y: Math.random() * height,
    vx: (Math.random() - 0.5) * 0.22,
    vy: (Math.random() - 0.5) * 0.22,
    r: Math.random() * 1.8 + 0.4,
    a: Math.random() * 0.6 + 0.16,
  }));
}

function drawBackdrop(time = 0) {
  ctx.clearRect(0, 0, width, height);
  const t = time * 0.00018;

  const gradient = ctx.createRadialGradient(width * 0.52, height * 0.38, 40, width * 0.5, height * 0.45, Math.max(width, height) * 0.75);
  gradient.addColorStop(0, "rgba(81, 241, 208, 0.11)");
  gradient.addColorStop(0.45, "rgba(58, 116, 160, 0.05)");
  gradient.addColorStop(1, "rgba(0, 0, 0, 0)");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, width, height);

  for (const point of points) {
    if (!reducedMotion) {
      point.x += point.vx + Math.cos(t + point.y * 0.002) * 0.04;
      point.y += point.vy + Math.sin(t + point.x * 0.002) * 0.04;
    }
    if (point.x < -20) point.x = width + 20;
    if (point.x > width + 20) point.x = -20;
    if (point.y < -20) point.y = height + 20;
    if (point.y > height + 20) point.y = -20;
    ctx.beginPath();
    ctx.fillStyle = `rgba(148, 255, 235, ${point.a})`;
    ctx.arc(point.x, point.y, point.r, 0, Math.PI * 2);
    ctx.fill();
  }

  for (let i = 0; i < points.length; i += 1) {
    const a = points[i];
    for (let j = i + 1; j < points.length; j += 7) {
      const b = points[j];
      const dx = a.x - b.x;
      const dy = a.y - b.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 145) {
        ctx.strokeStyle = `rgba(94, 231, 211, ${0.08 * (1 - dist / 145)})`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.stroke();
      }
    }
  }

  if (!reducedMotion) {
    raf = requestAnimationFrame(drawBackdrop);
  }
}

document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    cancelAnimationFrame(raf);
  } else if (!reducedMotion) {
    raf = requestAnimationFrame(drawBackdrop);
  }
});

window.addEventListener("resize", resize);
resize();
setSlide(getInitialSlide());
drawBackdrop();
if (!reducedMotion) {
  raf = requestAnimationFrame(drawBackdrop);
}
