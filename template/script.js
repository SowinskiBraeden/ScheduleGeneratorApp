function e(n) {return n != undefined && n != null && n != ""}

function start() {
  let file = document.getElementById("input_file").files[0];
  let minReq = document.getElementById("min_req").value;
  let classCap = document.getElementById("class_cap").value;
  let blockClassLimit = document.getElementById("classrooms").value;
  let totalBlocks = document.getElementById("total_blocks").value;

  // ensure data is passed before continuing
  if (!e(file) || !e(minReq) || !e(classCap) || !e(blockClassLimit) || !e(totalBlocks)) return alert('Please ensure all fields aren\'t empty.');

  // start animation
  document.getElementById('main').style.display = 'none';
  document.getElementById('processing').style.display = 'block';

  let reader = new FileReader()
  reader.addEventListener("load", () => {
    let raw = reader.result;
    eel.start(raw, minReq, classCap, blockClassLimit, totalBlocks)(finish_callback);
  }, false);

  if (file) {
    reader.readAsText(file);
  }
}

eel.expose(post_data);
function post_data(msg) {
  let newMessage = document.createElement('li');
  newMessage.innerText = msg;
  newMessage.className = 'nostyle'
  document.getElementById('progress').appendChild(newMessage)
}

function finish_callback(error) {
  if (error) {
    post_data(`Error: ${error.Title}`);
    post_data(error.Description);
  } else {
    document.getElementById('processing-header').innerText = 'Finished Processing!';
    let data = document.getElementById('progress');
    while (data.firstChild) {
      data.removeChild(data.firstChild);
    }
    post_data('Individual student schedules can be found in the \'/output/final/student_schedules/\' folder and the master timetable as well as student with conflicts can be found in the \'/output/final/\' folder.')
  }
  
  document.getElementById('loader').style.display = 'none';
  document.getElementById('retryBtn').style.display = 'block';
}

function retry() {
  // start animation
  document.getElementById('processing').style.display = 'none';
  document.getElementById('main').style.display = 'block';
  document.getElementById('loader').style.display = 'block';
  let data = document.getElementById('progress');
  while (data.firstChild) {
    data.removeChild(data.firstChild);
  }
}
