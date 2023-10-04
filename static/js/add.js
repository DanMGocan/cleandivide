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

  // Function to validate email address
  function isValidEmail(email) {
    const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return re.test(String(email).toLowerCase());
  }

  // Add an event listener to the form to trigger validation on submit
  document.getElementById('emailForm').addEventListener('submit', function(event) {
    const email = document.getElementById('email').value;

    if (!isValidEmail(email)) {
      event.preventDefault(); // Prevent the form from submitting if email is invalid
      alert("Invalid email address");
    } else {
      console.log("Email is valid. Proceeding with form submission.");
      // The form will submit normally
    }
  });

// Alert before generating a new schedule 
document.addEventListener("DOMContentLoaded", function() { 
  // Your code here.
  var generateButton = document.getElementById("generate-button");
  if (generateButton) {
      generateButton.addEventListener("click", function(event) {
          event.preventDefault();
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
  }
});

// Making the switch between Add Flatmate and Add Tasks sections
document.addEventListener('DOMContentLoaded', function() {
  // The switchSections function is the same as you provided
  function switchSections(hideSectionId, showSectionId) {
    let hideSection = document.getElementById(hideSectionId);
    let showSection = document.getElementById(showSectionId);

    hideSection.classList.add('hidden');
    hideSection.classList.remove('custom-fade');

    showSection.classList.remove('hidden');
    showSection.classList.add('custom-fade');
  }

  // Add event listener to "Add Tasks" button
  document.getElementById('btnAddTasks').addEventListener('click', function() {
    switchSections("sectionFlatmates", "sectionTasks");
  });

  // Add event listener to "Invite Flatmates" button
  document.getElementById('btnInviteFlatmates').addEventListener('click', function() {
    switchSections("sectionTasks", "sectionFlatmates");
  });

});