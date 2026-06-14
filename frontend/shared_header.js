// FORGE Agent — Shared Header & Session Manager
// Include this script on every page: <script src="/static/shared_header.js"></script>
// Call initForgeSession() after DOM is ready

const FORGE_SESSION = {
    getUserId:    () => localStorage.getItem('forge_user_id'),
    getUserName:  () => localStorage.getItem('forge_user_name'),
    getApiKey:    () => localStorage.getItem('forge_api_key'),
    isAdmin:      () => localStorage.getItem('forge_is_admin')  === '1',
    isSeller:     () => localStorage.getItem('forge_is_seller') === '1',
    isBuyer:      () => localStorage.getItem('forge_is_buyer')  === '1',
    getBuyerId:   () => localStorage.getItem('forge_buyer_id'),
    getBuyerName: () => localStorage.getItem('forge_buyer_name'),

    setSession: function(data) {
        if (data.user_id)   localStorage.setItem('forge_user_id',   data.user_id);
        if (data.full_name) localStorage.setItem('forge_user_name', data.full_name);
        if (data.api_key)   localStorage.setItem('forge_api_key',   data.api_key);
        localStorage.setItem('forge_is_admin',  data.is_admin  ? '1' : '0');
        localStorage.setItem('forge_is_seller', data.is_seller ? '1' : '0');
        localStorage.setItem('forge_is_buyer',  data.is_buyer  ? '1' : '0');
    },

    clear: function() {
        ['forge_user_id','forge_user_name','forge_api_key',
         'forge_is_admin','forge_is_seller','forge_is_buyer',
         'forge_buyer_id','forge_buyer_name'].forEach(k => localStorage.removeItem(k));
    }
};

function injectRoleBadge() {
    const userName = FORGE_SESSION.getUserName();
    if (!userName) return;

    const isAdmin  = FORGE_SESSION.isAdmin();
    const isSeller = FORGE_SESSION.isSeller();
    const isBuyer  = FORGE_SESSION.isBuyer();

    // Build role badges
    let badges = '';
    if (isAdmin)  badges += '<span style="background:#e05555; color:#fff; font-size:0.65rem; padding:2px 7px; border-radius:10px; font-weight:700; letter-spacing:0.5px;">ADMIN</span> ';
    if (isSeller) badges += '<span style="background:#c9a84c; color:#000; font-size:0.65rem; padding:2px 7px; border-radius:10px; font-weight:700; letter-spacing:0.5px;">SELLER</span> ';
    if (isBuyer)  badges += '<span style="background:#4a9eda; color:#fff; font-size:0.65rem; padding:2px 7px; border-radius:10px; font-weight:700; letter-spacing:0.5px;">BUYER</span> ';

    const userBadge = document.createElement('div');
    userBadge.id = 'forge-user-badge';
    userBadge.style.cssText = `
        display: flex; align-items: center; gap: 8px;
        background: ${isAdmin ? '#2a1a1a' : '#1a1d27'};
        border: 1px solid ${isAdmin ? '#e05555' : '#2a2d3a'};
        border-radius: 4px; padding: 5px 12px; font-size: 0.8rem;
    `;
    userBadge.innerHTML = `
        <span style="color:#888; font-size:0.75rem;">${userName}</span>
        ${badges}
        <button onclick="forgeLogout()" style="background:none; border:none; color:#555; cursor:pointer; font-size:0.75rem; padding:0 0 0 4px;" title="Sign out">✕</button>
    `;

    // Inject into header nav-links div
    const navLinks = document.querySelector('.nav-links');
    if (navLinks) navLinks.prepend(userBadge);

    // If admin, add Admin link to nav and red border to header
    if (isAdmin) {
        const header = document.querySelector('header');
        if (header) {
            header.style.borderBottomColor = '#e05555';
            header.style.borderBottomWidth = '2px';
        }

        // Add Admin nav link if not already on admin page
        if (!window.location.pathname.endsWith('admin.html')) {
            const adminLink = document.createElement('a');
            adminLink.href = '/static/admin.html';
            adminLink.textContent = '🔐 Admin';
            adminLink.style.cssText = `
                color: #e05555; text-decoration: none; font-size: 0.9rem;
                border: 1px solid #e05555; padding: 6px 16px; border-radius: 4px;
            `;
            adminLink.onmouseover = () => { adminLink.style.background = '#e05555'; adminLink.style.color = '#fff'; };
            adminLink.onmouseout  = () => { adminLink.style.background = 'none';    adminLink.style.color = '#e05555'; };
            if (navLinks) navLinks.appendChild(adminLink);
        }
    }
}

function forgeLogout() {
    FORGE_SESSION.clear();
    window.location.href = '/static/login.html';
}

function initForgeSession() {
    injectRoleBadge();
}
