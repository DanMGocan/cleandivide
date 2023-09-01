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

// Alert before generating a new schedule 
document.getElementById("generate-button").addEventListener("click", function() {
  var r = confirm("Are you sure you want to generate a new table? This will delete the old one.");
  if (r == true) {
      // User clicked 'OK'
      // Proceed to generate the table
      window.location.href = generateURL;
  } else {
      // User clicked 'Cancel'
      // Do nothing
  }
});