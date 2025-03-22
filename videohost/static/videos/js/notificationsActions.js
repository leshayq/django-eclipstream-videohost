if (isAuthenticated) {
    document.addEventListener('DOMContentLoaded', function() {
        fetch('/notifications/')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('notifications__list');
            const noItemsText = document.getElementById('notifications__no-items');
            const unreadNotificationsCount = count_unread_notifications(data);

            setNotificationsBadge(unreadNotificationsCount);
            
            if (data.notifications.length > 0) {
                noItemsText.style.display = 'none';
            }

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

function throttle(f, t) {
    return function (args) {
      let previousCall = this.lastCall;
      this.lastCall = Date.now();
      if (previousCall === undefined 
          || (this.lastCall - previousCall) > t) {
        f(args);
      }
    }
  }

const fetchMarkAsReadNotifications = () => {
    if (isAuthenticated) {
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
 
let throttledFetchMarkAsReadNotifications = throttle(fetchMarkAsReadNotifications, 3000); 

function showNotifications() {
    const notificationsPage = document.getElementById('notifications__page');

    notificationsPage.classList.toggle('show');

    if (notificationsPage.classList.contains('show')) {
        throttledFetchMarkAsReadNotifications();
    }

}

function count_unread_notifications(data) {
    const { unread_notifications_count } = data;
    return Number(unread_notifications_count);
}

function setNotificationsBadge(num) {
    const badge = document.getElementById('notifications__badge');
    if (badge) {
        if (typeof num === 'number' && num > 0) {
            badge.classList.add('show');
            badge.textContent = num;
        } else {
            badge.classList.remove('show');
        }
    }
}
