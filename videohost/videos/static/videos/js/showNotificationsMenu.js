function showNotifications() {
    const notificationsPage = document.getElementById('notifications__page');
    notificationsPage.classList.toggle('show');
}

(() => {
    const isAuthenticated = document.body.dataset.isAuthenticated === 'true';
    if (isAuthenticated) {
        document.addEventListener('click', function(event) {
            const notificationsPage = document.getElementById('notifications__page');
            const trigger = document.querySelector('.notifications__container a');
            
            if (!notificationsPage.contains(event.target) && !trigger.contains(event.target)) {
                notificationsPage.classList.remove('show');
            }
        });
    }
})();