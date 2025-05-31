
const loginForm = document.querySelector('.login-form');

    loginForm.addEventListener('submit', loginFormAuthentication);

    async function loginFormAuthentication(e) {
        e.preventDefault();

        const formData = new FormData(loginForm);
        const csrfToken = loginForm.querySelector('[name=csrfmiddlewaretoken]').value;
        const loginMessage = document.querySelector('.login-message');

        const response = await fetch('/account/login/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            body: formData,
        });

        const result = await response.json();

        if (response.ok) {
            loginMessage.style.display = 'block';
            loginMessage.textContent = result.message;
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else if (response.status === 400) {
            loginMessage.style.display = 'block';
            loginMessage.textContent = result.message;
            setTimeout(() => {
                loginMessage.style.display = 'none';
            }, 2000);
        } else {
            loginMessage.style.display = 'block';
            loginMessage.textContent = result.message;
            setTimeout(() => {
                loginMessage.style.display = 'none';
            }, 2000);
        }
    }