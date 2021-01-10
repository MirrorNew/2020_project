$(document).ready(function () {
    window.flag = [-1, -1, -1, -1, -1, -1];
    inputAnimation();
    cometsShow();
    pageToggle();
});

$(window).resize(function () {
    clearInterval(document.cometTimer);
    cometsShow();
});

