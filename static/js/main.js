/* ============================================================
   MindCare — main.js
   Global UI logic: sidebar, notifications, nav active state
   ============================================================ */

// ── Notifications data ──────────────────────────────────────
let notifications = [
    { id: 1, type: 'info',    title: 'Welcome to MindCare', message: 'Your wellness platform is ready.', time: '5m ago', read: false },
    { id: 2, type: 'success', title: 'Session Confirmed',   message: 'Your session is set for tomorrow at 2 PM.', time: '1h ago', read: false },
    { id: 3, type: 'warning', title: 'Check-in Reminder',   message: "Don't forget your daily mood check-in.", time: '3h ago', read: false },
];

// ── DOM Ready ────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
    initSidebar();
    initNotifications();
    initUserCard();
    initMobileMenu();
    setActiveNavLink();
});

// ── Sidebar ──────────────────────────────────────────────────
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (!sidebar) return;
    sidebar.classList.toggle('open');
    if (overlay) overlay.classList.toggle('active');
}

function initSidebar() {
    // On desktop, sidebar is always visible (no toggle needed)
}

function initMobileMenu() {
    const btn = document.getElementById('mobileMenuBtn');
    if (btn) {
        // Show mobile menu button on small screens
        const mq = window.matchMedia('(max-width: 768px)');
        const update = (e) => { btn.style.display = e.matches ? 'flex' : 'none'; };
        mq.addEventListener('change', update);
        update(mq);
    }
}

// ── Active Nav Link ──────────────────────────────────────────
function setActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link[data-path]');

    navLinks.forEach(link => {
        const linkPath = link.getAttribute('data-path');
        if (linkPath && currentPath.startsWith(linkPath)) {
            link.classList.add('active');
        }
    });
}

// ── User Card ────────────────────────────────────────────────
function initUserCard() {
    try {
        const userData = localStorage.getItem('user');
        const nameEl   = document.getElementById('userDisplayName');
        const roleEl   = document.getElementById('userDisplayRole');
        const initEl   = document.getElementById('userAvatarInitials');

        if (userData) {
            const user = JSON.parse(userData);
            const displayName = user.username || user.email || 'User';
            const role        = user.role || 'student';

            if (nameEl) nameEl.textContent = displayName;
            if (roleEl) roleEl.textContent = capitalize(role);
            if (initEl) initEl.textContent = displayName.charAt(0).toUpperCase();

            // Show admin items
            if (['admin', 'staff', 'faculty'].includes(role)) {
                document.querySelectorAll('.admin-only').forEach(el => el.style.display = 'block');
            }
        } else {
            if (nameEl) nameEl.textContent = 'Guest';
            if (roleEl) roleEl.textContent = 'Student';
            if (initEl) initEl.textContent = 'G';
        }
    } catch (e) {
        console.error('Error loading user data:', e);
    }
}

function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

// ── Logout ───────────────────────────────────────────────────
async function handleLogout() {
    try {
        const response = await fetch('/api/logout/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
        });
        localStorage.removeItem('user');
        window.location.href = '/login/';
    } catch (e) {
        localStorage.removeItem('user');
        window.location.href = '/login/';
    }
}

// ── Notifications ────────────────────────────────────────────
function initNotifications() {
    renderNotifications();
    updateNotifDot();
}

function toggleNotifications() {
    const dropdown = document.getElementById('notificationDropdown');
    if (!dropdown) return;
    dropdown.classList.toggle('show');

    // Close on outside click
    if (dropdown.classList.contains('show')) {
        setTimeout(() => {
            document.addEventListener('click', closeNotificationsOnOutside, { once: true });
        }, 0);
    }
}

function closeNotificationsOnOutside(e) {
    const dropdown = document.getElementById('notificationDropdown');
    const btn = document.getElementById('notifBtn');
    if (dropdown && !dropdown.contains(e.target) && btn && !btn.contains(e.target)) {
        dropdown.classList.remove('show');
    }
}

function renderNotifications() {
    const list = document.getElementById('notificationList');
    if (!list) return;

    if (notifications.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 16a2 2 0 0 0 2-2H6a2 2 0 0 0 2 2zM8 1.918l-.797.161A4.002 4.002 0 0 0 4 6c0 .628-.134 2.197-.459 3.742-.16.767-.376 1.566-.663 2.258h10.244c-.287-.692-.502-1.49-.663-2.258C12.134 8.197 12 6.628 12 6a4.002 4.002 0 0 0-3.203-3.92L8 1.917z"/></svg>
                <p>No new notifications</p>
            </div>`;
        return;
    }

    list.innerHTML = notifications.map(n => `
        <div class="notification-item ${n.read ? 'read' : ''}" onclick="markRead(${n.id})">
            <div class="notification-icon ${n.type}">
                ${getNotifIcon(n.type)}
            </div>
            <div class="notification-content">
                <div class="notification-title">${escapeHtml(n.title)}</div>
                <div class="notification-message">${escapeHtml(n.message)}</div>
                <div class="notification-time">${n.time}</div>
            </div>
            ${!n.read ? '<div class="notification-dot"></div>' : ''}
        </div>
    `).join('');
}

function getNotifIcon(type) {
    const icons = {
        info:    `<svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/><path d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/></svg>`,
        success: `<svg viewBox="0 0 16 16" fill="currentColor"><path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"/></svg>`,
        warning: `<svg viewBox="0 0 16 16" fill="currentColor"><path d="M7.938 2.016A.13.13 0 0 1 8.002 2a.13.13 0 0 1 .063.016.146.146 0 0 1 .054.057l6.857 11.667c.036.06.035.124.002.183a.163.163 0 0 1-.054.06.116.116 0 0 1-.066.017H1.146a.115.115 0 0 1-.066-.017.163.163 0 0 1-.054-.06.176.176 0 0 1 .002-.183L7.884 2.073a.147.147 0 0 1 .054-.057zm1.044-.45a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566z"/><path d="M7.002 12a1 1 0 1 1 2 0 1 1 0 0 1-2 0zM7.1 5.995a.905.905 0 1 1 1.8 0l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995z"/></svg>`,
    };
    return icons[type] || icons.info;
}

function markRead(id) {
    const n = notifications.find(n => n.id === id);
    if (n) n.read = true;
    renderNotifications();
    updateNotifDot();
}

function clearAllNotifications() {
    notifications = [];
    renderNotifications();
    updateNotifDot();
}

function updateNotifDot() {
    const dot = document.getElementById('notifDot');
    if (!dot) return;
    const unread = notifications.filter(n => !n.read).length;
    dot.style.display = unread > 0 ? 'block' : 'none';
}

// ── Utilities ────────────────────────────────────────────────
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(text || ''));
    return div.innerHTML;
}