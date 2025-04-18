function showChannelActions() {
    document.querySelector("div[data-subscription-id]").classList.toggle("show");
  }
  
$(document).on('submit', 'form[method="POST"][data-user-subscribed]', (e) => {
    e.preventDefault();
    let isUserSubscribed = document.querySelector('form[method="POST"][data-user-subscribed]').dataset.userSubscribed === 'true';
    console.log(isUserSubscribed);
    if (!isUserSubscribed) {
        if (isAuthenticated) {
            subscribeToChannelAjax(e);
        } else {
            window.location.href = `/u/login/?next=${encodeURIComponent(window.location.pathname)}`;
        }
    } else {
        showChannelActions();
    }
})
  
function subscribeToChannelAjax(e) {
    const form = document.querySelector('form[method="POST"][data-user-subscribed]');
    const url = form.dataset.subscribeUrl;
    const csrf = getCSRFToken();
  
    $.ajax({
        type: 'POST',
        url: url,
        data: {
            csrfmiddlewaretoken: csrf
        },
        success: function(response) {
        if (response.status === 'success') {
            const subscribeButton = document.getElementsByClassName('subscribe__button')[0];
            if (response.subscription_id) {
                form.dataset.userSubscribed = 'true';
                subscribeButton.classList.add('subscribed', 'dropbtn');
                subscribeButton.innerHTML = `<i class="fa-solid fa-bell" style="color: #ffffff; padding-right: 10px;"></i> Ви підписані ▼`;
                setDropDownSubscriptionData(response.subscription_id);
            } else {
                form.dataset.userSubscribed = 'false';
                subscribeButton.classList.remove('subscribed', 'dropbtn');
                subscribeButton.innerHTML = 'Підписатися';
                setDropDownSubscriptionData(null);
            }
        } else {
            console.error(response.message);
        }
    },
        error: function(response) {
            console.log('Channel subscribe error', response.responseJSON?.message)
        },
    })
}
  
const subscribeButton = document.getElementsByClassName('subscribe__button')[0];
  
function setDropDownSubscriptionData(subscriptionId) {
    const subscriptionDropdown = document.querySelector("div[data-subscription-id]");
    if (subscriptionId) {
        subscriptionDropdown.dataset.subscriptionId = subscriptionId;
    } else {
        subscriptionDropdown.dataset.subscriptionId = null;
    }
}
  
function disableNotifications() {
if (isAuthenticated) {
    const subscriptionId = document.querySelector("div[data-subscription-id]").dataset.subscriptionId;

    if (!subscriptionId) {
        console.error("Subscription ID not found.");
        return;
    }

    fetch(`/notifications/disable-notifications/${subscriptionId}/`, {
        method: 'POST',
        headers: {
            "X-CSRFToken": getCSRFToken(), 
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ subscription_id: subscriptionId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const subscribeButton = document.querySelector('form[method="POST"][data-user-subscribed] button');
            subscribeButton.querySelector('i').classList = 'fa-regular fa-bell';
        } else {
            console.error("Error:", data.error);
        }
    })
    .catch(error => console.error("Network error:", error));
    }   
}
  
function enableNotifications() {
if (isAuthenticated) {
    const subscriptionId = document.querySelector("div[data-subscription-id]").dataset.subscriptionId;

    if (!subscriptionId) {
        console.error("Subscription ID not found.");
        return;
    }

    fetch(`/notifications/enable-notifications/${subscriptionId}/`, {
        method: 'POST',
        headers: {
            "X-CSRFToken": getCSRFToken(), 
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ subscription_id: subscriptionId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const subscribeButton = document.querySelector('form[method="POST"][data-user-subscribed] button');
            subscribeButton.querySelector('i').classList = 'fa-solid fa-bell';
        } else {
            console.error("Error:", data.error);
        }
    })
    .catch(error => console.error("Network error:", error));
    }   
}
  
function unsubscribe(e) {
    subscribeToChannelAjax(e);
}
  
window.onclick = function(event) {
    if (!event.target.matches('.dropbtn')) {
        let dropdown = document.querySelector("div[data-subscription-id]");

        if (!dropdown) return ;
        if (dropdown.classList.contains('show')) {
            dropdown.classList.remove('show');
        }
    }
}