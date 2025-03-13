const ws = new WebSocket('ws://' + window.location.host + '/ws/notifications/');
ws.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const container = document.getElementById('notifications__list');

    container.insertAdjacentHTML('afterbegin', `
    <div class="notification">
        <div class="notification__content">
            <p class="notification__text">${data.message}</p>
            <p class="notification__timedate">щойно</p>
        </div>
    </div>
    `)
};
