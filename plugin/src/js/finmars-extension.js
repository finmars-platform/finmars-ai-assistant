// import 'css/finmars-extension.css';

function getCookie(name) {
    const m = document.cookie.match(new RegExp('(?:^|; )' + name.replace(/([.$?*|{}()[\\]\/+^])/g, '\\$1') + '=([^;]*)'));
    return m ? decodeURIComponent(m[1]) : null;
}

function parseJwt(t) {
    try {
        const p = t.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
        return JSON.parse(atob(p))
    } catch {
        return null
    }
}

function isExpired(t, skew = 30) {
    const c = parseJwt(t);
    if (!c || !c.exp) return true;
    return c.exp <= Math.floor(Date.now() / 1000) + skew;
}

async function bootstrapViaCookiesOrReload(serverSrc) {
    const realm = (location.pathname.match(/\/(realm[^/]+)/i) || [])[1] || 'finmars';
    const space = (location.pathname.match(/\/realm[^/]+\/(space[^/]+)/i) || [])[1] || 'default';
    const access = getCookie('access_token');

    if (!access || isExpired(access, 30)) {
        location.reload();  // родитель «обновит» куки через свою SSO-механику
        return false;
    }
    const res = await fetch(serverSrc + "/bootstrap/finmars", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        credentials: "include",
        body: JSON.stringify({
            user_access_token: access,
            finmars_realm: realm,
            finmars_space: space
        })
    });
    if (!res.ok) {
        location.reload();
        return false;
    }
    return true;
}

window.FinmarsExtension = {
    init: function () {
        this.serverSrc = "https://ya-ce.finmars.io:8881";
        this.bootstrapTimer = null;
        // Load the HTML and CSS
        this.loadHTML();
        this.loadCSS();

    },

    loadHTML: function () {
        const container = document.createElement('div');
        container.id = 'finmars-ai-container';
        document.body.appendChild(container);

        const button = document.createElement('button');
        button.id = 'circleButton';
        button.innerText = 'FinAI';
        button.addEventListener('click', this.toggleChat.bind(this));
        container.appendChild(button);

        const iframeContainer = document.createElement('div');
        iframeContainer.id = 'iframeContainer';
        iframeContainer.style.display = 'none';

        const iframe = document.createElement('iframe');
        // src is set on toggle
        iframeContainer.appendChild(iframe);

        const closeButton = document.createElement('button');
        closeButton.innerText = '×';
        closeButton.className = 'closeButton';
        closeButton.addEventListener('click', () => {
            iframeContainer.style.display = 'none';
            if (window.FinmarsExtension.bootstrapTimer) {
                clearInterval(window.FinmarsExtension.bootstrapTimer);
                window.FinmarsExtension.bootstrapTimer = null;
            }
        });
        iframeContainer.appendChild(closeButton);

        document.body.appendChild(iframeContainer);
    },
    loadCSS: function () {
        // ... existing code ...
    },

    toggleChat: async function () {
        const iframeContainer = document.getElementById('iframeContainer');
        const iframe = iframeContainer.querySelector('iframe');

        if (iframeContainer.style.display === 'none' || iframeContainer.style.display === '') {
            const ok = await bootstrapViaCookiesOrReload(this.serverSrc);
            if (!ok) return;
            iframeContainer.style.display = 'block';
            // перезапуск потока на всякий случай (и кэш-байпас)
            iframe.src = this.serverSrc + '/oauth/oidc/login?ts=' + Date.now();

            // Start periodic check
            if (this.bootstrapTimer) clearInterval(this.bootstrapTimer);
            this.bootstrapTimer = setInterval(() => {
                bootstrapViaCookiesOrReload(this.serverSrc);
            }, 60000);

        } else {
            iframeContainer.style.display = 'none';
            // Stop periodic check
            if (this.bootstrapTimer) {
                clearInterval(this.bootstrapTimer);
                this.bootstrapTimer = null;
            }
        }
    }
};

// Initialize the chat extension
window.FinmarsExtension.init();