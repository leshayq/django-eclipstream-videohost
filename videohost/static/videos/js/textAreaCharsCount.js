const descriptionTextArea = document.querySelector('textarea');
const charsCounterOutput = document.getElementsByClassName('chars__counter')[0];

descriptionTextArea.addEventListener('input', (e) => {
    const charsCount = e.target.value.length;

    charsCounterOutput.innerText = `${charsCount}/${descriptionTextArea.maxLength}`;
})