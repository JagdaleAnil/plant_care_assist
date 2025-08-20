function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    const icon = input.nextElementSibling;

    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('icon-lock');
        icon.classList.add('icon-unlock'); // Assuming you have a different icon for unlocked state
    } else {
        input.type = 'password';
        icon.classList.remove('icon-unlock');
        icon.classList.add('icon-lock');
    }
}
