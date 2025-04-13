const likeVideoAjax = (e) => {
    const $form = $(e.target);
    const url = $form.data('like-url');
    const csrf = getCSRFToken();

    $.ajax({
        type: 'POST',
        url: url,
        data: {
            csrfmiddlewaretoken: csrf
        },
        success: function(response) {
            if (response.status === 'success') {
                toggleLikedClass();
            } else {
                console.log(response.message);
            }
        },
        error: function(response) {
            console.log('Video like error', response.responseJSON?.message)
        },
    })
}

let throttledLikeVideoAjax = throttle(likeVideoAjax, 1000)
$(document).on('submit', '#likeVideoForm', (e) => {
    e.preventDefault();
    throttledLikeVideoAjax(e);
})


const likeButton = document.getElementsByClassName('like__button')[0];

function toggleLikedClass() {
    if (!likeButton.classList.contains('liked')) {
        likeButton.classList.add('liked');
        setLikesCount('like');
    } else {
        likeButton.classList.remove('liked');
        setLikesCount('unlike');
    }
}

function setLikesCount(action) {
    const likeCount = document.getElementsByClassName('like__count')[0];
    if (action == 'like') {
        likeCount.textContent = Number(likeCount.textContent) + 1;
    } else {
        likeCount.textContent = Number(likeCount.textContent) - 1;
    }
}