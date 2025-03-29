const usernameField = document.querySelector('.form__field input[type="text"]');

usernameField.addEventListener('keypress', function(e) {
    if(!String.fromCharCode(e.which).match(/[a-z0-9]/g)) {
        e.preventDefault();
    }
}, false);