// Toggling awards 
document.addEventListener("DOMContentLoaded", function() {
    const awardBoxes = document.querySelectorAll(".award-box");
    
    awardBoxes.forEach(box => {
        let tooltip;
        box.addEventListener('mouseenter', function() {
            // Create tooltip
            tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.innerHTML = box.getAttribute('data-tooltip');
            document.body.appendChild(tooltip);

            // Position tooltip
            const rect = box.getBoundingClientRect();
            tooltip.style.left = (rect.left + (box.offsetWidth / 2) - (tooltip.offsetWidth / 2)) + 'px';
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';

            // Show tooltip
            tooltip.classList.add('show');
        });

        box.addEventListener('mouseleave', function() {
            if (tooltip) {
                tooltip.classList.remove('show');
                document.body.removeChild(tooltip);
                tooltip = null;
            }
        });
    });
});

// Delete everything button tooltip
document.addEventListener('DOMContentLoaded', function() {
    const awardBoxes = document.querySelectorAll('.award-box-active, .award-box-inactive');
    const tooltip = document.createElement('div');
    tooltip.classList.add('tooltip');

    document.body.appendChild(tooltip);

    awardBoxes.forEach(box => {
        box.addEventListener('mouseover', function(event) {
            // Set tooltip content and position
            tooltip.textContent = event.currentTarget.dataset.tooltip;
            tooltip.style.top = (event.currentTarget.getBoundingClientRect().bottom + window.scrollY + 10) + 'px';
            tooltip.style.left = (event.currentTarget.getBoundingClientRect().left + window.scrollX) + 'px';

            // Show the tooltip
            tooltip.classList.add('show');
        });

        box.addEventListener('mouseout', function() {
            // Hide the tooltip
            tooltip.classList.remove('show');
        });
    });
});