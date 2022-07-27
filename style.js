function toggleNav() {
  const body = document.body;
  const hamburger = document.getElementById("js-hamburger");
  const overlay = document.getElementById("js-overlay");
  hamburger.addEventListener("click", function () {
    body.classList.toggle("nav-open");
  });
  overlay.addEventListener("click", function () {
    body.classList.remove("nav-open");
  });
}
toggleNav(); 

const btn = document.getElementById('click');
const nav = document.getElementById('nav');

btn.addEventListener('click' , () => {
  if(nav.classList.contains('open')){
    nav.classList.remove('open');
        // 固定解除
    bodyScrollLock.clearAllBodyScrollLocks();
  } else {
    nav.classList.add('open');
        // 背景固定
    bodyScrollLock.disableBodyScroll(nav);
  }
});
