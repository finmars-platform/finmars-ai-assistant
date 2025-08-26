// import 'css/finmars-extension.css';

window.FinmarsExtension = {
    init: function () {
        this.serverSrc = "https://ya-ce.finmars.io:8881"
        // Load the HTML and CSS
        this.loadHTML();
        this.loadCSS();

    },

    loadHTML: function () {
        const container = document.createElement('div');
        container.id = 'finmars-container';
        document.body.appendChild(container);

        const button = document.createElement('button');
        button.id = 'circleButton';
        button.innerText = 'FinAI';
        button.addEventListener('click', this.toggleChat.bind(this));
        container.appendChild(button);

        const iframeContainer = document.createElement('div');
        iframeContainer.id = 'iframeContainer';

        const iframe = document.createElement('iframe');
        // сразу запускаем OIDC-поток (как будто нажали кнопку SSO)
        iframe.src = this.serverSrc + '/oauth/oidc/login';
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
        // ... existing code ...
    },

    toggleChat: function () {
        const iframeContainer = document.getElementById('iframeContainer');
        const iframe = iframeContainer.querySelector('iframe');

        if (iframeContainer.style.display === 'none' || iframeContainer.style.display === '') {
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
