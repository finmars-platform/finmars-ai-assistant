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
    const refresh = getCookie('refresh_token');

    if (!access || isExpired(access, 30)) {
        location.reload();  // родитель «обновит» куки через свою SSO-механику
        return false;
    }
    
    if (!refresh) {
        console.error('No refresh token found');
        location.reload();
        return false;
    }
    
    const res = await fetch(serverSrc + "/bootstrap/finmars", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        credentials: "include",
        body: JSON.stringify({
            user_access_token: access,
            finmars_realm: realm,
            finmars_space: space,
            refresh_token: refresh
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
        });
        iframeContainer.appendChild(closeButton);

        document.body.appendChild(iframeContainer);
    },
    loadCSS: function () {
        const style = document.createElement('style');
        style.textContent = `
            #finmars-ai-container {
                position: fixed;
                z-index: 10000;
            }
            
            #circleButton {
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, #ff6b35, #f7931e);
                color: white;
                border: none;
                font-size: 12px;
                font-weight: bold;
                cursor: pointer;
                z-index: 10001;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                transition: transform 0.2s ease;
            }
            
            #circleButton:hover {
                transform: scale(1.1);
            }
            
            #iframeContainer {
                position: fixed;
                top: 50px;
                right: 20px;
                width: 600px;
                height: calc(100vh - 100px);
                background: white;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                z-index: 10000;
                overflow: hidden;
            }
            
            #iframeContainer iframe {
                width: 100%;
                height: 100%;
                border: none;
                border-radius: 12px;
                zoom: 0.7;
            }
            
            .closeButton {
                position: absolute;
                top: 10px;
                right: 10px;
                width: 30px;
                height: 30px;
                border: none;
                background: rgba(0, 0, 0, 0.1);
                color: #666;
                border-radius: 50%;
                cursor: pointer;
                font-size: 18px;
                line-height: 1;
                z-index: 10001;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .closeButton:hover {
                background: rgba(0, 0, 0, 0.2);
            }
        `;
        document.head.appendChild(style);
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
        } else {
            iframeContainer.style.display = 'none';
        }
    }
};

// Initialize the chat extension
window.FinmarsExtension.init();