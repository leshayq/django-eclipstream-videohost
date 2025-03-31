function showChannelActions() {
  document.querySelector("div[data-subscription-id]").classList.toggle("show");
}

function subscribeFormSubmit(event) {
  const isUserSubscribed = document.querySelector('form[method="POST"][data-user-subscribed]').dataset.userSubscribed === 'true';
  console.log(isUserSubscribed);
  if (!isUserSubscribed) {
      const subscribeForm = document.querySelector('form[method="POST"][data-user-subscribed]');;
      subscribeForm.submit();
  } else {
      event.preventDefault();
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

function unsubscribe() {
  if (isAuthenticated) {
      const subscribeForm = document.querySelector('form[method="POST"][data-user-subscribed]');;
      subscribeForm.submit();
  }
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