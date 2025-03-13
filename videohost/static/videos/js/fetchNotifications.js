(() => {
    const isAuthenticated = document.body.dataset.isAuthenticated === 'true';
    if (isAuthenticated) {
        document.addEventListener('DOMContentLoaded', function() {
            fetch('/notifications/')
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('notifications__list');
                data.notifications.forEach(notification => {
                    container.insertAdjacentHTML('beforeend', `
                        <div class="notification">
                            <div class="notification__content">
                                <p class="notification__text">${notification.message}</p>
                                <p class="notification__timedate">${notification.timesince}</p>
                            </div>
                        </div>
                    `);
                });
            });
        });
    }
})();