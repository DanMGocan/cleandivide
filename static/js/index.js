// 
document.addEventListener('DOMContentLoaded', (event) => {
    const customBoxes = document.querySelectorAll('.custom-box');
  
    customBoxes.forEach((box) => {
      box.addEventListener('mouseover', function() {
        this.querySelector('.number').style.opacity = '0';
        this.querySelector('.hidden-text').style.opacity = '1';
      });
  
      box.addEventListener('mouseout', function() {
        this.querySelector('.hidden-text').style.opacity = '0';
        this.querySelector('.number').style.opacity = '1';
      });
    });
  });
  

// Modal
  window.addEventListener('load', function() {
    var betaModal = new bootstrap.Modal(document.getElementById('betaModal'), {
      keyboard: false
    });
    betaModal.show();
  });

