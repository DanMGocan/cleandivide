// Making sure the input for frequency is of the correct type
document.getElementById('frequency').addEventListener('change', function () {
  var options = document.querySelectorAll('#frequencies option');
  var value = this.value;
  var valid = Array.from(options).some(function (option) {
    return option.value === value;
  });
  if (!valid) {
    alert('Invalid value');
    this.value = ''; // Clear the input
  }
});