document.addEventListener("DOMContentLoaded", function () {

    const camposSenha = document.querySelectorAll('input[type="password"]');

    camposSenha.forEach(function (campo) {

        const botao = document.createElement("button");

        botao.type = "button";
        botao.textContent = "Mostrar";
        botao.classList.add("botao-mostrar-senha");

        campo.parentElement.appendChild(botao);

        botao.addEventListener("click", function () {

            if (campo.type === "password") {
                campo.type = "text";
                botao.textContent = "Ocultar";
            } else {
                campo.type = "password";
                botao.textContent = "Mostrar";
            }

        });

    });

});

