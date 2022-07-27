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

// ハンバーガーメニュー展開時の背景固定
$(function () {
  $(".ham").click(function () {
    // トリガーをクリックした時の条件分岐
    if ($(this).hasClass("is-active")) {
      // ナビを閉じるときの処理
      $("html").removeClass("is-fixed"); // 背景固定解除！
    } else {
      // ナビを開くときの処理
      $("html").addClass("is-fixed"); // 背景固定！
    }
    $(".ham").toggleClass("is-active");
  });
});
        
