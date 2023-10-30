document.addEventListener("DOMContentLoaded", function() {
    const tooltipWrappers = document.querySelectorAll('.tooltip-wrapper');

    tooltipWrappers.forEach(wrapper => {
        wrapper.addEventListener('mouseenter', function() {
            const tooltipElem = wrapper.querySelector('.tooltip-text');
            if (!tooltipElem) {
                const tooltipText = wrapper.getAttribute('data-tooltip');
                const newTooltipElem = document.createElement('span');
                newTooltipElem.className = 'tooltip-text';
                newTooltipElem.innerText = tooltipText;
                wrapper.appendChild(newTooltipElem);
            } else {
                tooltipElem.style.display = 'block';
            }
        });

        wrapper.addEventListener('mouseleave', function() {
            const tooltipElem = wrapper.querySelector('.tooltip-text');
            if (tooltipElem) {
                tooltipElem.style.display = 'none';
            }
        });
    });
});
