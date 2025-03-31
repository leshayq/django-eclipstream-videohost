function toggleMenu() {
    const menu = document.getElementById('side-menu');
    menu.classList.toggle('show');
}

document.addEventListener('click', function(event) {
    const menu = document.getElementById('side-menu');
    const trigger = document.getElementsByClassName('burger-menu')[0];
    
    if (!menu.contains(event.target) && !trigger.contains(event.target)) {
        if (menu.classList.contains('show')) {
            menu.classList.remove('show');
        }
    }
});
  