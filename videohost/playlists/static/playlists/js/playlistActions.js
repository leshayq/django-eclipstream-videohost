function showPlaylistActions() {
    document.getElementById("playlistActionsDropdown").classList.toggle("show");
  }
  
  window.onclick = function(event) {
    if (!event.target.matches('.dropbtn')) {
      let dropdown = document.getElementsByClassName("dropdown__content")[0];
      if (dropdown.classList.contains('show')) {
          dropdown.classList.remove('show');
      }
    }
}
  
function showEditPlaylistModal() {
      document.getElementById('editPlaylistModal').classList.add('show');
      disableBodyScroll();
}
  
function closeEditPlaylistModal() {
      document.getElementById('editPlaylistModal').classList.remove('show');
      enableBodyScroll();
}

function showDeletePlaylistModal() {
      document.getElementById('deletePlaylistModal').classList.add('show');
      disableBodyScroll();
}
  
function closeDeletePlaylistModal() {
      document.getElementById('deletePlaylistModal').classList.remove('show');
      enableBodyScroll();
}

document.addEventListener('click', function(event) {
      const modal = document.querySelector('.modal.show');
      const trigger = document.querySelector('.dropdown');

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
  
