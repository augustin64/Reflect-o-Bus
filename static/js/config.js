var setConfig = function() {
  getJSON('get?content=config',
  function(data) {
    console.log(data)
  });
}