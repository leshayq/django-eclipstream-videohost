const randomVideoForm = document.getElementById('randomVideoForm');
const formAction = randomVideoForm.action;
const csrf = getCSRFToken();

randomVideoForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const container = document.getElementById('random-video__container');

    container.classList.add('fade-out');

    setTimeout(() => {
        fetch(formAction, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrf,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'Success') {
                container.innerHTML = data.html;

                container.classList.remove('fade-out');
                container.classList.add('fade-in');

                setTimeout(() => {
                    container.classList.remove('fade-in');
                }, 300);
            } else {
                console.error('Error:', data.message);
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
        });
    }, 300); 
});