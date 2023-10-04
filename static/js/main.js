document.addEventListener("DOMContentLoaded", function() {
    const button = document.getElementsByClassName('custom-tooltip');

    button.addEventListener('mousemove', function(e) {
        let tooltip = document.querySelector('.custom-tooltip');

        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.className = 'custom-tooltip';
            document.body.appendChild(tooltip);
        }

        tooltip.textContent = button.getAttribute('data-tooltip');
        tooltip.style.top = (e.pageY + 10) + 'px';
        tooltip.style.left = (e.pageX + 10) + 'px';
        tooltip.style.display = 'block';

    });

    button.addEventListener('mouseout', function() {
        const tooltip = document.querySelector('.custom-tooltip');
        if (tooltip) {
            tooltip.style.display = 'none';
        }
    });
});
