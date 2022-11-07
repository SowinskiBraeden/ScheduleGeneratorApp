function start() {
  let file = document.getElementById("input_file").files[0];
  let minReq = document.getElementById("min_req").value;
  let classCap = document.getElementById("class_cap").value;
  let blockClassLimit = document.getElementById("classrooms").value;
  let totalBlocks = document.getElementById("total_blocks").value;
 
  // start animation
  document.getElementById('main').style.display = 'none';
  document.getElementById('processing').style.display = 'block';

  let reader = new FileReader()
  reader.addEventListener("load", () => {
    let raw = reader.result;
    eel.start(raw, minReq, classCap, blockClassLimit, totalBlocks)(start_callback);
  }, false);

  if (file) {
    reader.readAsText(file);
  }
}

function start_callback(error) {
  console.log(error, 'done')
}