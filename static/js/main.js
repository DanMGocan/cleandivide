document.addEventListener("DOMContentLoaded", function() {
    const buttons = document.getElementsByClassName('tooltip-button');

    for(let i = 0; i < buttons.length; i++) {
        let button = buttons[i];

        button.addEventListener('mousemove', function(e) {
            console.log("Mouse over detected");
            let tooltip = document.querySelector('.tooltip-content');

            if (!tooltip) {
                tooltip = document.createElement('div');
                tooltip.className = 'tooltip-content';
                document.body.appendChild(tooltip);
            }

            tooltip.textContent = e.currentTarget.getAttribute('data-tooltip');
            tooltip.style.top = (e.pageY + 10) + 'px';
            tooltip.style.left = (e.pageX + 10) + 'px';
            tooltip.style.display = 'block';
        });

        button.addEventListener('mouseout', function() {
            const tooltip = document.querySelector('.tooltip-content');
            if (tooltip) {
                tooltip.style.display = 'none';
            }
        });
    }
});

// // Activating the tooltips
// var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
// var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
//   return new bootstrap.Tooltip(tooltipTriggerEl)
// })

// Script the remove the #_=_ from the redirect URL 
if (window.location.hash && window.location.hash == '#_=_') {
    if (window.history && history.pushState) {
        window.history.pushState("", document.title, window.location.pathname);
    } else {
        // Prevent scrolling by storing the page's current scroll offset
        var scroll = {
            top: document.body.scrollTop,
            left: document.body.scrollLeft
        };
        window.location.hash = '';
        // Restore the scroll offset, should be flicker free
        document.body.scrollTop = scroll.top;
        document.body.scrollLeft = scroll.left;
    }
}

// Gradient change on scroll
window.addEventListener('scroll', handleScroll);

function handleScroll() {
  const scrollTop = window.scrollY;
  const scrollPercent = scrollTop / (document.body.scrollHeight - window.innerHeight);
  const offset = scrollPercent * 7;  // 5% max offset

  document.body.style.setProperty('--stop1', `${5 + offset}%`);
  document.body.style.setProperty('--stop2', `${10 + offset}%`);
  document.body.style.setProperty('--stop3', `${90 - offset}%`);
  document.body.style.setProperty('--stop4', `${95 - offset}%`);
}

// Initial call to set the gradient on page load
handleScroll();

// Making the flash message disappear after a while
document.addEventListener('DOMContentLoaded', (event) => {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(flashMessage => {
        // Set a timeout to remove the flash message after 3 seconds
        setTimeout(() => {
            flashMessage.remove();
        }, 3600);  // 3000 milliseconds = 3 seconds
    });
});




  
