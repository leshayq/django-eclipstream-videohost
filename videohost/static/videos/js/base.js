const isAuthenticated = document.body.dataset.isAuthenticated === 'true';

function getCSRFToken() {
    const cookieValue = document.cookie.match(/csrftoken=([^;]+)/);
    return cookieValue ? cookieValue[1] : "";
}