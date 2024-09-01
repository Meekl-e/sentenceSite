document.addEventListener('DOMContentLoaded', function () {
    let selectedCheckboxes = [];


    document.querySelectorAll('.form-check-input').forEach(function (checkbox) {
        checkbox.addEventListener('change', function () {
            if (checkbox.checked) {

                if (selectedCheckboxes.length < 2) {
                    selectedCheckboxes.push(checkbox);

                } else {

                    selectedCheckboxes[selectedCheckboxes.length - 1].checked = false;
                    document.getElementsByName("counter_"+selectedCheckboxes[selectedCheckboxes.length - 1].name.split("_")[1])[0].textContent = "";
                    selectedCheckboxes.pop();
                    selectedCheckboxes.push(checkbox);
                    console.log(selectedCheckboxes);

                }


            } else {
                selectedCheckboxes = selectedCheckboxes.filter(function (item) {
                    return item !== checkbox;
                });
                document.getElementsByName("counter_"+checkbox.name.split("_")[1])[0].textContent = "";

            }
            for (let i = 0; i <selectedCheckboxes.length; i++){
                    let txt;
                    if (i === 0) {
                        txt = "от";}
                    else {
                        txt = "к"
                    }

                    document.getElementsByName("counter_"+selectedCheckboxes[i].name.split("_")[1])[0].textContent = txt;
                }

        });

    });
    document.getElementById("form-relation").addEventListener('submit', function (e) {
    let hiddenInput = document.getElementById('selected_order');
    let tokens = document.getElementById('tokens');
    let width = document.getElementById("width");
    let all_tokens = document.getElementsByName("token");

    if (selectedCheckboxes.length !== 2){

        document.getElementById("form-error").textContent = "Необходимо выбрать два слова. Сейчас выбрано "+selectedCheckboxes.length+".";
        e.preventDefault();
    }


    hiddenInput.value = selectedCheckboxes.map(cb => cb.value-1).join('-');
     var string_v = "";
     all_tokens.forEach(function (element){
         string_v += " "+element.textContent;
     });

    tokens.value = string_v;
    width.value =  document.getElementById("main-container" ).clientWidth;

});

    document.getElementById("form-send").addEventListener('submit', function (e) {
    let lines = document.querySelectorAll("select");
    let line_elem = document.getElementById("lines-send-hidden");

    var lines_list = "";
     lines.forEach(function (element){
         lines_list += " "+element.value;
     });
     line_elem.value = lines_list;


});
   var idx = 0;
    document.getElementsByName("form-remove").forEach(function (form) {
        let inputs = form.getElementsByTagName("input")[1];
        inputs.value = idx;
        idx+=1;
    });

});
