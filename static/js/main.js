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
