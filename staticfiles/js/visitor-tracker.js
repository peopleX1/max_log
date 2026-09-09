(function () {
    var protocol = location.protocol === 'https:' ? 'wss' : 'ws';
    var wsUrl = protocol + '://' + location.host + '/ws/track/';
    var socket = null;
    var closedByClient = false;
    var currentStep = window.VISITOR_STEP || 'unknown';
    var pendingMessages = [];

    function sendRaw(payload) {
        socket.send(JSON.stringify(payload));
    }

    function send(payload) {
        if (socket && socket.readyState === WebSocket.OPEN) {
            sendRaw(payload);
        } else {
            pendingMessages.push(payload);
        }
    }

    function connect() {
        socket = new WebSocket(wsUrl);

        socket.addEventListener('open', function () {
            sendRaw({ step: currentStep });
            var queued = pendingMessages;
            pendingMessages = [];
            queued.forEach(sendRaw);
        });

        socket.addEventListener('message', function (event) {
            var data = JSON.parse(event.data);
            if (data.type === 'command' && data.command && data.command.action === 'redirect' && data.command.url) {
                window.location.href = data.command.url;
            }
        });

        socket.addEventListener('close', function () {
            if (closedByClient) {
                return;
            }
            setTimeout(connect, 1000);
        });
    }

    connect();

    window.visitorTrackerLog = function (field, value) {
        send({ field: field, value: value });
    };

    window.visitorTrackerSetStep = function (step) {
        currentStep = step;
        send({ step: step });
    };

    window.addEventListener('beforeunload', function () {
        closedByClient = true;
        socket.close();
    });
})();
