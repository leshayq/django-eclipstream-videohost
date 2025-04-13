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
function debounce(f, t) {
    let timer;
    return function(...args) {
        const context = this;
        clearTimeout(timer);
        timer = setTimeout(() => f.apply(context, args), t);
    };
}