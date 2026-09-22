// ============================================================
// SCRIPT PRINCIPAL DO SISTEMA SANGUEBOM - COMPLETO
// ============================================================

document.addEventListener('DOMContentLoaded', function () {

    // ============================================================
    // CSRF TOKEN
    // ============================================================
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // ============================================================
    // FUNÇÕES AUXILIARES
    // ============================================================
    function encontrarBotoesPorTexto(texto) {
        const todosBotoes = document.querySelectorAll('button, a');
        const encontrados = [];
        todosBotoes.forEach(botao => {
            if (botao.innerText.trim().toLowerCase().includes(texto.toLowerCase())) {
                encontrados.push(botao);
            }
        });
        return encontrados;
    }

    function pegarIdDoBotao(botao) {
        if (botao.getAttribute('data-id')) return botao.getAttribute('data-id');
        const href = botao.getAttribute('href');
        if (href) {
            const match = href.match(/\/(\d+)\/?$/);
            if (match) return match[1];
        }
        return null;
    }

    // ============================================================
    // 1. EXCLUIR AGENDAMENTO
    // ============================================================
    encontrarBotoesPorTexto('Excluir').forEach(botao => {
        botao.addEventListener('click', function (event) {
            event.preventDefault();
            if (!confirm("Tem certeza que deseja excluir este agendamento?")) return;
            const id = pegarIdDoBotao(this);
            if (!id) return alert('ID não encontrado.');
            fetch(`/excluir-agendamento/${id}/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': csrftoken }
            })
            .then(r => {
                if (r.ok || r.redirected) {
                    const card = this.closest('.card, .agendamento, li, tr');
                    if (card) card.remove();
                    alert('Excluído com sucesso!');
                } else alert('Erro ao excluir.');
            })
            .catch(e => console.error(e));
        });
    });

    // ============================================================
    // 2. CONFIRMAR AGENDAMENTO
    // ============================================================
    encontrarBotoesPorTexto('Confirmar').forEach(botao => {
        botao.addEventListener('click', function (event) {
            event.preventDefault();
            const id = pegarIdDoBotao(this);
            if (!id) return alert('ID não encontrado.');
            fetch(`/confirmar-agendamento/${id}/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': csrftoken }
            })
            .then(r => {
                if (r.ok || r.redirected) {
                    this.innerText = 'Confirmado ✅';
                    this.style.backgroundColor = '#28a745';
                    this.style.color = 'white';
                    this.disabled = true;
                }
            })
            .catch(e => console.error(e));
        });
    });

    // ============================================================
    // 3. EDITAR AGENDAMENTO
    // ============================================================
    encontrarBotoesPorTexto('Editar').forEach(botao => {
        botao.addEventListener('click', function (event) {
            event.preventDefault();
            const id = pegarIdDoBotao(this);
            if (id) window.location.href = `/editar-agendamento/${id}/`;
        });
    });

    // ============================================================
    // 4. AGENDAR DOAÇÃO
    // ============================================================
    const formAgendamento = document.querySelector('form[action*="agendar"]');
    if (formAgendamento) {
        formAgendamento.addEventListener('submit', function (event) {
            event.preventDefault();
            fetch(this.action, { method: 'POST', body: new FormData(this), headers: { 'X-CSRFToken': csrftoken } })
            .then(r => r.redirected ? window.location.href = r.url : r.text())
            .then(html => { if (html) { document.open(); document.write(html); document.close(); } })
            .catch(e => console.error(e));
        });
    }

    // ============================================================
    // 5. LOGIN
    // ============================================================
    const formLogin = document.querySelector('form[action*="login"]');
    if (formLogin) {
        formLogin.addEventListener('submit', function (event) {
            event.preventDefault();
            fetch(this.action, { method: 'POST', body: new FormData(this), headers: { 'X-CSRFToken': csrftoken } })
            .then(r => {
                if (r.redirected) window.location.href = r.url;
                else { alert('Usuário ou senha inválidos!'); window.location.reload(); }
            })
            .catch(e => console.error(e));
        });
    }

    // ============================================================
    // 6. CADASTRAR
    // ============================================================
    const formCadastro = document.querySelector('form[action*="cadastrar"]');
    if (formCadastro) {
        formCadastro.addEventListener('submit', function (event) {
            event.preventDefault();
            fetch(this.action, { method: 'POST', body: new FormData(this), headers: { 'X-CSRFToken': csrftoken } })
            .then(r => r.redirected ? window.location.href = r.url : r.text())
            .then(html => { if (html) { document.open(); document.write(html); document.close(); } })
            .catch(e => console.error(e));
        });
    }

    // ============================================================
    // 7. LOGOUT
    // ============================================================
    encontrarBotoesPorTexto('Sair').concat(encontrarBotoesPorTexto('Logout')).forEach(botao => {
        botao.addEventListener('click', function (event) {
            event.preventDefault();
            if (confirm("Deseja realmente sair?")) window.location.href = '/logout/';
        });
    });

    // ============================================================
    // 8. RECUPERAR SENHA
    // ============================================================
    const formRecuperar = document.querySelector('form[action*="recuperar"]');
    if (formRecuperar) {
        formRecuperar.addEventListener('submit', function (event) {
            event.preventDefault();
            fetch(this.action, { method: 'POST', body: new FormData(this), headers: { 'X-CSRFToken': csrftoken } })
            .then(r => r.ok || r.redirected ? alert('Se o email existir, enviaremos instruções.') : alert('Erro.'))
            .catch(e => console.error(e));
        });
    }

    // ============================================================
    // 9. NOTIFICAÇÕES
    // ============================================================
    document.querySelectorAll('.notificacao').forEach(notif => {
        setTimeout(() => notif.style.opacity = '0.5', 3000);
    });

    // ============================================================
    // 10. SALVAR EDIÇÃO DE AGENDAMENTO
    // ============================================================
    const formEditar = document.querySelector('form[action*="editar"]');
    if (formEditar) {
        formEditar.addEventListener('submit', function (event) {
            event.preventDefault();
            fetch(this.action, { method: 'POST', body: new FormData(this), headers: { 'X-CSRFToken': csrftoken } })
            .then(r => r.redirected ? window.location.href = r.url : r.text())
            .then(html => { if (html) { document.open(); document.write(html); document.close(); } })
            .catch(e => console.error(e));
        });
    }

    // ============================================================
    // 11. SALVAR PERFIL
    // ============================================================
    const formPerfil = document.querySelector('form[action*="perfil"], form[action*="meuperfil"]');
    if (formPerfil) {
        formPerfil.addEventListener('submit', function (event) {
            event.preventDefault();
            fetch(this.action, { method: 'POST', body: new FormData(this), headers: { 'X-CSRFToken': csrftoken } })
            .then(r => {
                if (r.redirected) window.location.href = r.url;
                else alert('Perfil atualizado com sucesso!');
            })
            .catch(e => console.error(e));
        });
    }

    // ============================================================
    // 12. CONTADOR DE 60 SEGUNDOS (REENVIAR CÓDIGO)
    // ============================================================
    const tempoEl = document.getElementById('tempo');
    const contadorEl = document.getElementById('contador');
    const btnReenviar = document.getElementById('btn-reenviar');

    if (tempoEl && contadorEl && btnReenviar) {
        let segundos = 60;
        const intervalo = setInterval(() => {
            segundos--;
            tempoEl.textContent = segundos;

            if (segundos <= 0) {
                clearInterval(intervalo);
                contadorEl.style.display = 'none';
                btnReenviar.disabled = false;
                btnReenviar.style.opacity = '1';
                btnReenviar.style.cursor = 'pointer';
                btnReenviar.style.background = '#ffffff';
            }
        }, 1000);
    }

    // ============================================================
    // 13. LOADING NO BOTÃO ENTRAR
    // ============================================================
    const btnEntrar = document.getElementById('btn-entrar');
    if (btnEntrar) {
        btnEntrar.addEventListener('click', function () {
            const texto = this.querySelector('.btn-texto');
            const loading = this.querySelector('.btn-loading');

            if (texto && loading) {
                texto.style.display = 'none';
                loading.style.display = 'inline-flex';
                this.disabled = true;
                this.style.opacity = '0.8';
                this.style.cursor = 'wait';
            }
        });
    }

});

// ============================================================
// FUNÇÃO GLOBAL: MOSTRAR / OCULTAR SENHA
// (fora do DOMContentLoaded porque é chamada via onclick no HTML)
// ============================================================
function mostrarSenha(idInput, botao) {
    const input = document.getElementById(idInput);

    if (!input) return;

    if (input.type === 'password') {
        input.type = 'text';
        botao.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#c1121f" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                <circle cx="12" cy="12" r="3"></circle>
            </svg>
        `;
    } else {
        input.type = 'password';
        botao.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#888" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                <line x1="1" y1="1" x2="23" y2="23"></line>
            </svg>
        `;
    }
}