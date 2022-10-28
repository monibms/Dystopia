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

// ハンバーガーメニューオープン時の背景固定
$(function () {
  let state = false;
  let scrollpos;
  $("#js-hamburger,#js-overlay").on("click", function () {
    if (state == false) {
      scrollpos = $(window).scrollTop();
      $("body").addClass("fixed").css({ top: -scrollpos });
      state = true;
    } else {
      $("body").removeClass("fixed").css({ top: 0 });
      window.scrollTo(0, scrollpos);
      state = false;
    }
  });
});
