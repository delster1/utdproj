document.querySelectorAll('.employee-item').forEach(item => {
    item.addEventListener('click', () => {
        document.querySelectorAll('.employee-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        console.log(`Selected: ${item.textContent}`);
    });
});