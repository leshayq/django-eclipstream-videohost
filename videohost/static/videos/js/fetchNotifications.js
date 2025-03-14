(() => {
    const isAuthenticated = document.body.dataset.isAuthenticated === 'true';
    if (isAuthenticated) {
        document.addEventListener('DOMContentLoaded', function() {
            fetch('/notifications/')
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('notifications__list');

                changeNotificationsBadge(data);

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

        function changeNotificationsBadge(data) {
            const { unread_notifications_count } = data;
        
            const badge = document.getElementById('notifications__badge');
        
            if (badge) {
                if (unread_notifications_count > 0) {
                    badge.classList.toggle('show');
                    badge.textContent = unread_notifications_count;
                }
            }
        }
    }
})();