document.addEventListener('DOMContentLoaded', function () {
    let selectedCheckboxes = [];

    let active_edits = [];

    document.getElementsByName("edit_token").forEach(function (token_edit){
        token_edit.addEventListener("click",function () {
            var input = document.getElementById(token_edit.id+"_input");
            var btn = document.getElementById(token_edit.id+"_btn");
            if (input.type === "hidden"){
                input.type = "text";
                console.log(document.getElementById(token_edit.id+"_txt").textContent);
                var txt_cont = document.getElementById(token_edit.id+"_txt").textContent

                input.value = txt_cont.slice(0,txt_cont.length-3);
                btn.hidden = null;
                active_edits.push(token_edit);
            }else {
                input.type = "hidden";
                btn.hidden = "hidden";
                setTimeout(() => active_edits = active_edits.filter((el) => el !== token_edit), 10);
            }
        } );
    });
    document.getElementsByName("confirm_edit").forEach(function (confirm_btn){
        confirm_btn.addEventListener("click",function () {
            active_edits.forEach(function (token_edit) {
                var btn = document.getElementById(token_edit.id+"_btn");
                var input = document.getElementById(token_edit.id+"_input");
                fetch(btn.value+input.value);


            });
            location.reload();
        } );

    });


    document.querySelectorAll('.form-check-input').forEach(function (checkbox) {
        checkbox.addEventListener('change', function (event) {
            var chb_id = checkbox.getAttribute("name").split("_");

            console.log("edit_token_"+chb_id[chb_id.length-1]);

            var find_obj = document.getElementById("edit_token_"+chb_id[chb_id.length-1]);

            if (active_edits.find(function (value, index, array) {
                return value === find_obj;
            }) !== undefined) {
                checkbox.checked = ! checkbox.checked;
                event.preventDefault();
                return;
            }

            if (checkbox.checked) {

                if (selectedCheckboxes.length < 2) {
                    selectedCheckboxes.push(checkbox);

                } else {

                    selectedCheckboxes[selectedCheckboxes.length - 1].checked = false;
                    document.getElementsByName("counter_"+selectedCheckboxes[selectedCheckboxes.length - 1].name.split("_")[1])[0].textContent = "";
                    selectedCheckboxes.pop();
                    selectedCheckboxes.push(checkbox);


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
