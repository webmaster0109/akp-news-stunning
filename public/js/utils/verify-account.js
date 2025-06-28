const verifyAccount = document.querySelector('.verify-account-akp');

  verifyAccount.addEventListener('submit', verifyAccountFormAuthentication);

  async function verifyAccountFormAuthentication(event){
    event.preventDefault();

    const formData = new FormData(verifyAccount);
    const csrfToken = verifyAccount.querySelector('[name=csrfmiddlewaretoken]').value;
    const url = event.target.action;
    const verifyMessage = document.querySelector('.verify-account-message');


    console.log()
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
      },
      body: formData,
    });

    const result = await response.json();

    if (response.ok) {
      // alert(result.message);
      verifyMessage.style.display = "block";
      verifyMessage.style.color = 'green';
      verifyMessage.textContent = result.message;
      setTimeout(() => {
        window.location.reload();
      }, 2000)
    } else if (response.status === 400) {
      verifyMessage.style.display = "block";
      verifyAccount.style.color = 'red';
      verifyMessage.textContent = result.message;
      setTimeout(() => {
        verifyMessage.style.display = "none";
      }, 1000)
    } else {
      alert(result.message);
    }

  }