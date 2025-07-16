const addTrade = document.querySelector("#add-trade");
const addMem = document.querySelector("#add-member");
const addTeam = document.querySelector("#add-team");

const popupContainer = document.querySelectorAll('.popup-container');
const tradeCont = document.querySelector('.trade-container');
const memCont = document.querySelector(".mem-container");
const teamCont = document.querySelector('.team-container');

// & Event listener for popup closing
popupContainer.forEach((elem) => {
    elem.addEventListener('click', (e) => {
        if (!elem.classList.contains('open')) { }
        elem.style.opacity = "0";
        setTimeout(() => {
            elem.style.display = "none";
        }, 100);
    })
})

// | HELPER listener for popup opening/closing
document.querySelectorAll(".popup-content").forEach((elem) => {
    elem.addEventListener('click', (e) => {
        e.stopPropagation();
    })
})

// & Event listener for addTrade popup opening
addTrade.addEventListener('click', () => {
    tradeCont.style.display = "flex";
    tradeCont.classList.add('open');

    setTimeout(() => {
        tradeCont.style.opacity = "1";
    }, 100);
})

// & Event listener for addMem popup opening
addMem.addEventListener('click', () => {
    memCont.style.display = "flex";
    memCont.classList.add('open');

    setTimeout(() => {
        memCont.style.opacity = '1';
    }, 100);
})

// & Event listener for addTeam popup opening
addTeam.addEventListener('click', () => {
    teamCont.style.display = "flex";
    teamCont.classList.add('open');

    setTimeout(() => {
        teamCont.style.opacity = '1';
    }, 100);
})