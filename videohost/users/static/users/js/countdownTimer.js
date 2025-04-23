let timeSecond = 5;
const timeH = document.querySelector(".success__countdown-timer p");

displayTime(timeSecond);

const countDown = setInterval(() => {
  timeSecond--;
  displayTime(timeSecond);
  if (timeSecond == 0 || timeSecond < 1) {
    endCount();
    clearInterval(countDown);
  }
}, 1000);

function displayTime(second) {
  const sec = second;
  timeH.innerHTML = `
  ${sec}
  `;
}

function endCount() {
    window.location.href = '/'
}
