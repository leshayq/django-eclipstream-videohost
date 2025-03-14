export function changeNotificationsBadge(data) {
    const { unread_notifications_count } = data;

    const badge = document.getElementById('notifications__badge');

    if (badge) {
        if (unread_notifications_count > 0) {
            badge.classList.toggle('show');
            badge.textContent = unread_notifications_count;
        }
    }
}