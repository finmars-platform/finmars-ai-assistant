// import 'css/finmars-extension.css';

window.FinmarsExtension = {
    init: function () {
        this.serverSrc = "https://ya-ce.finmars.io:8881"
        // Load the HTML and CSS
        this.loadHTML();
        this.loadCSS();

    },

    loadHTML: function () {
        var optiContainer = document.createElement('div');
        optiContainer.id = 'finmars-container';
        document.body.appendChild(optiContainer)

        var container = document.getElementById('finmars-container');
        if (!container) return;

        var button = document.createElement('button');
        button.id = 'circleButton';
        button.innerText = 'FinAI';
        button.addEventListener('click', this.toggleChat);
        container.appendChild(button);

        var iframeContainer = document.createElement('div');
        iframeContainer.id = 'iframeContainer';
        var iframe = document.createElement('iframe');
        // iframe.src = this.serverSrc + "?pageURL=" + window.location.href;
        iframe.src = this.serverSrc;
        iframeContainer.appendChild(iframe);

        // Create close button and append to iframeContainer
        var closeButton = document.createElement('button');
        closeButton.innerText = '×';
        closeButton.className = 'closeButton';
        closeButton.addEventListener('click', function () {
            iframeContainer.style.display = 'none';
        });
        iframeContainer.appendChild(closeButton);

        document.body.appendChild(iframeContainer);
    },
    loadCSS: function () {
        // ... existing code ...
    },

    toggleChat: function () {
        var iframeContainer = document.getElementById('iframeContainer');
        var iframe = iframeContainer.querySelector('iframe');

        if (iframeContainer.style.display === 'none' || iframeContainer.style.display === '') {
            iframeContainer.style.display = 'block';
            iframe.src = iframe.src; // This line refreshes the iframe content
        } else {
            iframeContainer.style.display = 'none';
        }
    }
};

// Initialize the chat extension
window.FinmarsExtension.init();
