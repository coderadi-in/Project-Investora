const addStrategy = document.querySelector("#add-strategy");
const strategyCont = document.querySelector(".strategy-container");

addStrategy.addEventListener('click', () => {
    strategyCont.style.display = "flex";
    strategyCont.classList.add('open');

    setTimeout(() => {
        strategyCont.style.opacity = "1";
    }, 100);
})