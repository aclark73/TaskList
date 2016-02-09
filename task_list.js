onload = function() {
  var btns = document.querySelectorAll('.toolbar-actions .btn');
  for (var i=0; i<btns.length; i++) {
    btns[i].addEventListener('click', function() {
      console.log("Button clicked: " + this.id);
    });
  }
};
