const isAuthenticated = document.body.dataset.isAuthenticated === 'true';
const body = document.body;

function getCSRFToken() {
    const cookieValue = document.cookie.match(/csrftoken=([^;]+)/);
    return cookieValue ? cookieValue[1] : "";
}

function disableBodyScroll() {
    body.classList.add('body-no-scroll');
}

function enableBodyScroll() {
    body.classList.remove('body-no-scroll');
}
