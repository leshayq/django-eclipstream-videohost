function showPlaylistActions() {
    document.getElementById("myDropdown").classList.toggle("show");
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
      document.getElementById('editPlaylistModal').style.display = 'block';
  }
  
  function closeEditPlaylistModal() {
      document.getElementById('editPlaylistModal').style.display = 'none';
  }
  
  function showDeletePlaylistModal() {
      document.getElementById('deletePlaylistModal').style.display = 'block';
  }
  
  function closeDeletePlaylistModal() {
      document.getElementById('deletePlaylistModal').style.display = 'none';
  }
  