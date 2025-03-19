(() => {
    const isAuthenticated = document.body.dataset.isAuthenticated === 'true';
    if (isAuthenticated) {
        const ws = new WebSocket('ws://' + window.location.host + '/ws/notifications/');
        ws.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const container = document.getElementById('notifications__list');
        const noItemsText = document.getElementById('notifications__no-items');

        updateNotificationsBadge();
        noItemsText.style.display = 'none';
        
        container.insertAdjacentHTML('afterbegin', `
        <div class="notification">
            <div class="notification__content">
                <p class="notification__text">${data.message}</p>
                <p class="notification__timedate">щойно</p>
            </div>
        </div>
        `)
        };
    }
})();

function updateNotificationsBadge() {
    const notificationsBadge = document.getElementById('notifications__badge');

    const notifications_count = Number(notificationsBadge.textContent);
    if (notifications_count == 0 || notifications_count == NaN || notifications_count == '') {
        notificationsBadge.classList.toggle('show');
        notificationsBadge.textContent = 1;
    } else {
        notificationsBadge.textContent = notifications_count + 1;
    }
}
