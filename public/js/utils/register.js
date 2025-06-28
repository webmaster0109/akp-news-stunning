const registerForm = document.querySelector('.register-form');

    registerForm.addEventListener('submit', registerFormAuthentication);

    async function registerFormAuthentication(e) {
        e.preventDefault();

        const formData = new FormData(registerForm);
        const csrfToken = registerForm.querySelector('[name=csrfmiddlewaretoken]').value;

        const registerMessage = document.querySelector('.register-message');

        const response = await fetch('/account/register/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            body: formData,
        });

        const result = await response.json();

        if (response.ok) {
            registerMessage.style.display = 'block';
            registerMessage.textContent = result.message;
            // setTimeout(() => {
            //     window.location.reload();
            // }, 2000);
        } else if (response.status === 400) {
            registerMessage.style.display = 'block';
            registerMessage.textContent = result.message;
        } else {
            registerMessage.style.display = 'block';
            registerMessage.textContent = result.message;
        }
    }