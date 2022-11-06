function start() {
  let file = document.getElementById("input_file");
  let blockClassLimit = document.getElementById("classrooms").value;
  let minReq = document.getElementById("min_req").value;
  let classCap = document.getElementById("class_cap").value;
  let totalBlocks = document.getElementById("total_blocks").value;

  console.log(file);
}

function summation() {
  var data_1 = document.getElementById("int1").value;
  var data_2 = document.getElementById("int2").value;
  eel.add(data_1, data_2)(call_Back);
}

function call_Back(output){
  document.getElementById("res").value = output;
}

var i = 0;
function move() {
  if (i == 0) {
    i = 1;
    var elem = document.getElementById("myBar");
    var width = 1;
    var id = setInterval(frame, 10);
    function frame() {
      if (width >= 100) {
        clearInterval(id);
        i = 0;
      } else {
        width++;
        elem.style.width = width + "%";
      }
    }
  }
}