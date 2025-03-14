function showNotifications() {
    const notificationsPage = document.getElementById('notifications__page');
    const notificationsBadge = document.getElementsByClassName('notifications__badge')[0];

    notificationsPage.classList.toggle('show');
    notificationsBadge.classList.toggle('show');

    markAsReadNotifications();
}

function markAsReadNotifications() {
    fetch('/notifications/mark-read/', {
        method: 'POST',
        headers: {
            "X-CSRFToken": getCSRFToken(), 
            "Content-Type": "application/json"
        }

    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            //pass
        } else {
            console.error("Ошибка:", data.error);
        }
    })
    .catch(error => console.error("Ошибка сети:", error));
}

function getCSRFToken() {
    const cookieValue = document.cookie.match(/csrftoken=([^;]+)/);
    return cookieValue ? cookieValue[1] : "";
}

(() => {
    const isAuthenticated = document.body.dataset.isAuthenticated === 'true';
    if (isAuthenticated) {
        document.addEventListener('click', function(event) {
            const notificationsPage = document.getElementById('notifications__page');
            const notificationsBadge = document.getElementsByClassName('notifications__badge')[0];
            const trigger = document.querySelector('.notifications__container a');
            
            if (!notificationsPage.contains(event.target) && !trigger.contains(event.target)) {
                notificationsPage.classList.remove('show');
            }
        });
    }
})();