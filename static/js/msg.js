let flashMessage = document.querySelector('.flash');

if (flashMessage) {
  setTimeout(() => {
    flashMessage.style.transform = "translateY(-40px)";
    flashMessage.style.opacity = "0";
  }, 3000);
}