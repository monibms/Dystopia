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
.toggle_title {
	font-weight: bold;
	line-height: 42px;
	margin: 0;
	padding: 0 0 0 10px;
	position: relative;
	cursor: pointer;
	transition: 0.3s;
}
.toggle_title:hover {
	color: #fd7e00;
}
.toggle_title:after {
	content: "";
	display: inline-block;
	width: 28px;
	height: 28px;
	background:url(btn_arrow.png) no-repeat right top;
	position:absolute;
	top: 50%;
	right: 7px;
	transform: translateY(-50%);
	transition: 0.2s;
}
.toggle_title.selected:after {
	transform: translateY(-50%) rotate(180deg);
	transition: 0.2s;
}
.toggle_txt {
	display: none;
}
