document.addEventListener('click', function(event) {
    const modal = document.querySelector('.modal.show');
    const trigger = document.querySelector('.media-action__button');

    if (!modal || !trigger) return;

    const modalCloseBtn = modal.querySelector('.modal-close__button');
    const modalTitle = modal.querySelector('h2');
    const modalFormContent = modal.querySelector('form');
    
    if (!trigger.contains(event.target) && !modalCloseBtn.contains(event.target) && !modalTitle.contains(event.target) && !modalFormContent.contains(event.target)) {
        if (modal.classList.contains('show')) {
              modal.classList.remove('show');
              enableBodyScroll();
        }
    }
  });