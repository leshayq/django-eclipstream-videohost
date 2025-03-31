function newPlaylistModal() {
    document.getElementById('newPlaylistModal').classList.add('show');
    disableBodyScroll();
}

function closeNewPlaylistModal() {
    document.getElementById('newPlaylistModal').classList.remove('show');
    enableBodyScroll();
}
