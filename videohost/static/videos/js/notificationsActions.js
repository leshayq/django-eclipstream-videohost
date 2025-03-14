const isAuthenticated = document.body.dataset.isAuthenticated === 'true';

if (isAuthenticated) {
    document.addEventListener('DOMContentLoaded', function() {
        fetch('/notifications/')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('notifications__list');

            const unreadNotificationsCount = count_unread_notifications(data);
            setNotificationsBadge(unreadNotificationsCount);

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

document.addEventListener('click', function(event) {
    const notificationsPage = document.getElementById('notifications__page');
    const notificationsBadge = document.getElementsByClassName('notifications__badge')[0];
    const trigger = document.querySelector('.notifications__container a');
    
    if (!notificationsPage.contains(event.target) && !trigger.contains(event.target)) {
        if (notificationsPage.classList.contains('show')) {
            setNotificationsBadge(0);
        }
        notificationsPage.classList.remove('show');
    }


});

function showNotifications() {
    console.log("Открытие окна уведомлений");
    const notificationsPage = document.getElementById('notifications__page');

    notificationsPage.classList.toggle('show');

    if (notificationsPage.classList.contains('show')) {
        console.log("Окно уведомлений открыто, помечаем прочитанными");
        fetchMarkAsReadNotifications();
    }

}

function count_unread_notifications(data) {
    const { unread_notifications_count } = data;
    return Number(unread_notifications_count);
}

function setNotificationsBadge(num) {
    const badge = document.getElementById('notifications__badge');
    console.log("setNotificationsBadge вызван с:", num);
    if (badge) {
        if (typeof num === 'number' && num > 0) {
            badge.classList.add('show');
            badge.textContent = num;
        } else {
            badge.classList.remove('show');
        }
    }
}

function fetchMarkAsReadNotifications() {
    if (isAuthenticated) {
        console.log("Отправка запроса на пометку уведомлений как прочитанные");
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
                setNotificationsBadge(0);
            } else {
                console.error("Error:", data.error);
            }
        })
        .catch(error => console.error("Network error:", error));
    }   
}

function getCSRFToken() {
    const cookieValue = document.cookie.match(/csrftoken=([^;]+)/);
    return cookieValue ? cookieValue[1] : "";
}