const commentTextArea = document.querySelector('.comment__form textarea');
const cancelButton = document.querySelector('.cancel__button');
const submitButton = document.querySelector('.comment__form .comment__button');

commentTextArea.addEventListener('focus', (event) => {
    event.target.style.height = '100px';
    cancelButton.style.opacity = '100';
    submitButton.style.opacity = '100';
    cancelButton.style.cursor = 'pointer';
    submitButton.style.cursor = 'pointer';
    cancelButton.disabled = false;
    submitButton.disabled = false;
})

cancelButton.addEventListener('click', (event) => { 
    cleanCommentForm();
})

function toggleReplyForm(commentId) {
    let form = document.getElementById('reply-form-' + commentId);
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
    
    try {
        let parentComment = document.querySelector(`#reply-${commentId}`);
        const parentCommentOwner = parentComment.querySelector('.comment__header h4').textContent;
        
        const formTextArea = form.querySelector('textarea');

        if (formTextArea.value.slice(0, parentCommentOwner.length) != parentCommentOwner) {
            formTextArea.value += parentCommentOwner;
        }
    } catch {
        // pass
    }

}

function cleanCommentForm() {
    commentTextArea.style.height = '45px';
    commentTextArea.value = '';
    cancelButton.style.opacity = '0';
    submitButton.style.opacity = '0';
    cancelButton.style.cursor = 'default';
    submitButton.style.cursor = 'default';
    cancelButton.disabled = true;
    submitButton.disabled = true;
}

function cleanReplyForm(commentId) {
    let form = document.getElementById('reply-form-' + commentId);
    let replyFormTextArea = form.querySelector('textarea');

    form.style.display = form.style.display === 'none' ? 'block' : 'none';
    replyFormTextArea.value = '';
}

function cleanForm(form) {
    const replyFormTextArea = form.querySelector('textarea');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
    replyFormTextArea.value = '';
}

function toggleReplies(commentId) {
    let replies = document.getElementById('replies-' + commentId);
    let button = document.querySelector(`#comment-${commentId} .toggle-replies__button`);
    
    if (replies.style.display === 'none') {
        replies.style.display = 'block';
        button.textContent = `Приховати відповіді (${replies.children.length})`;
    } else {
        replies.style.display = 'none';
        button.textContent = `Показати відповіді (${replies.children.length})`;
    }
}

function insertCreatedComment(user, text) {
    const commentsContainer = document.querySelector('.comments_container');
    commentsContainer.insertAdjacentHTML('afterbegin',
        `
        <div class="comment">
            <div class="comment__body">
                <div class="comment__header">
                    <a>
                        <h4>@${user}</h4>
                    </a>

                    <span class="comment__datetime">тільки що</span>
                </div>
                <p>${text}</p>
            </div>
        </div>`
            
    )
}

function insertCreatedReply(user, text, parent_id, position="afterbegin") {
    const repliesContainer = document.getElementById(`replies-${parent_id}`);

    repliesContainer.insertAdjacentHTML(position, 
        `
        <div class="reply">
            <div class="comment__header">
                <a>
                    <h4>@${user}</h4>
                </a>

                <span class="comment__datetime">тільки що</span>
            </div>
            <p>${text}</p>
        </div>
        `
    )

    repliesContainer.style.display = 'block';
}

$(document).on('submit', '.comment__form', (e) => {
    e.preventDefault();
    commentVideoAjax(e, null);
})

$(document).on('submit', '.reply__form', (e) => {
    e.preventDefault();
    replyToCommentAjax(e);
})

function commentVideoAjax(e) {
    const form = document.querySelector('.comment__form');
    const url = form.dataset.commentUrl;

    const csrf = getCSRFToken();
    const text = form.querySelector('textarea');


    $.ajax({
        type: 'POST',
        url: url,
        data: {
            csrfmiddlewaretoken: csrf,
            comment_text: text.value
        },
        success: function(response) {
        if (response.status === 'success') {
            if (!response.parent_id) {
                insertCreatedComment(response.user, text.value);
                cleanCommentForm();
            } else {
                insertCreatedReply(response.user, text.value, response.parent_id);
            }
        } else {
            console.error(response.message);
        }
    },
        error: function(response) {
            console.log('Video comment error', response.responseJSON?.message)
        },
    })
}

function replyToCommentAjax(e) {
    const form = e.target;
    const url = form.dataset.replyUrl;
    const parentId = form.dataset.parentId;

    const csrf = getCSRFToken();
    const text = form.querySelector('textarea');


    $.ajax({
        type: 'POST',
        url: url,
        data: {
            csrfmiddlewaretoken: csrf,
            reply_text: text.value,
            parent_id: parentId
        },
        success: function(response) {
        if (response.status === 'success') {
            if (response.root_id == parentId) {
                insertCreatedReply(response.user, text.value, response.root_id);
            } else {
                insertCreatedReply(response.user, text.value, response.root_id, 'beforeend');
            }

            cleanForm(form);
        } else {
            console.error(response.message);
        }
    },
        error: function(response) {
            console.log('Video comment error', response.responseJSON?.message)
        },
    })
}
