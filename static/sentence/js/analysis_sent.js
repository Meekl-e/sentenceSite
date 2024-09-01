document.addEventListener('DOMContentLoaded', function () {


    document.querySelector('form').addEventListener('submit', function (e) {

    let width = document.getElementById("width-frame");
    width.value =  document.getElementById("main-container" ).clientWidth;

});

});
