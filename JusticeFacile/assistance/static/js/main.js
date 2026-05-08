/* ════════════════════════════════════════
   JUSTICEFACILE — Script principal
════════════════════════════════════════ */

// ── SIDEBAR MOBILE ──
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

// Fermer sidebar en cliquant dehors
document.addEventListener('click', function(e) {
  const sidebar = document.getElementById('sidebar');
  const btn = document.querySelector('.hamburger-btn');
  if (sidebar && !sidebar.contains(e.target) && btn && !btn.contains(e.target)) {
    sidebar.classList.remove('open');
  }
});

// ── NOTIFICATIONS ──
function toggleNotif() {
  const panel = document.getElementById('notif-panel');
  if (panel) panel.classList.toggle('open');
}

document.addEventListener('click', function(e) {
  const panel = document.getElementById('notif-panel');
  const btn = document.querySelector('.notif-trigger');
  if (panel && btn && !panel.contains(e.target) && !btn.contains(e.target)) {
    panel.classList.remove('open');
  }
});

// ── MODALS ──
function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('open');
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('open');
}

// Fermer modal en cliquant sur l'overlay
document.querySelectorAll('.modal-overlay').forEach(function(overlay) {
  overlay.addEventListener('click', function(e) {
    if (e.target === overlay) overlay.classList.remove('open');
  });
});

// ── MESSAGES CHAT ──
function sendMessage(inputId, containerId, isIA) {
  const input = document.getElementById(inputId);
  const container = document.getElementById(containerId);
  if (!input || !container || !input.value.trim()) return;

  const text = input.value.trim();
  input.value = '';

  // Bulle utilisateur
  const msgEl = document.createElement('div');
  msgEl.className = 'msg me';
  msgEl.innerHTML = `
    <div class="msg-av" style="background:linear-gradient(135deg,var(--or),var(--or-vif));color:var(--nuit)">
      ${isIA ? 'Moi' : 'Moi'}
    </div>
    <div>
      <div class="msg-bubble">${text}</div>
      <div class="msg-time">${getCurrentTime()}</div>
    </div>
  `;
  container.appendChild(msgEl);
  container.scrollTop = container.scrollHeight;

  // Réponse IA simulée
  if (isIA) {
    setTimeout(function() {
      const iaEl = document.createElement('div');
      iaEl.className = 'ia-msg';
      iaEl.innerHTML = `
        <div class="msg-av" style="background:linear-gradient(135deg,var(--or),var(--or-vif));color:var(--nuit);font-size:16px">🤖</div>
        <div>
          <div class="msg-bubble">Je traite votre demande juridique... Voici une réponse basée sur la législation camerounaise applicable.</div>
        </div>
      `;
      container.appendChild(iaEl);
      container.scrollTop = container.scrollHeight;
    }, 900);
  }
}

function getCurrentTime() {
  const now = new Date();
  return now.getHours().toString().padStart(2,'0') + ':' + now.getMinutes().toString().padStart(2,'0');
}

// ── TOUCHE ENTRÉE POUR CHAT ──
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.chat-input-wrap input, .ia-input-wrap input').forEach(function(input) {
    input.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        const wrap = input.closest('.chat-input-wrap, .ia-input-wrap');
        if (wrap) {
          const btn = wrap.querySelector('.send-btn');
          if (btn) btn.click();
        }
      }
    });
  });
});

// ── MESSAGES FLASH DJANGO ──
document.addEventListener('DOMContentLoaded', function() {
  const alerts = document.querySelectorAll('.django-alert');
  alerts.forEach(function(alert) {
    setTimeout(function() {
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      setTimeout(function() { alert.remove(); }, 400);
    }, 4000);
  });
});

// ── ACTIVE NAV ITEM ──
document.addEventListener('DOMContentLoaded', function() {
  const current = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(function(item) {
    const href = item.getAttribute('href');
    if (href && current.startsWith(href) && href !== '/') {
      item.classList.add('active');
    }
  });
});

// ── CONFIRM SUPPRESSION ──
function confirmDelete(message) {
  return confirm(message || 'Êtes-vous sûr de vouloir supprimer cet élément ?');
}

// ── ANIMATIONS PROGRESS BARS ──
document.addEventListener('DOMContentLoaded', function() {
  const bars = document.querySelectorAll('.prog-fill[data-width]');
  setTimeout(function() {
    bars.forEach(function(bar) {
      bar.style.width = bar.getAttribute('data-width') + '%';
    });
  }, 200);
});
