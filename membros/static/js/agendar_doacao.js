document.addEventListener('DOMContentLoaded', function () {

    // ==========================================
    // REFERÊNCIAS
    // ==========================================
    const etapas = document.querySelectorAll('.card-etapa');
    const botoesProximo = document.querySelectorAll('.btn-proximo');
    const botoesVoltar = document.querySelectorAll('.btn-voltar');
    const indicadores = document.querySelectorAll('.etapa');

    // ==========================================
    // NAVEGAÇÃO ENTRE ETAPAS
    // ==========================================
    function mostrarEtapa(numero) {
        // Esconde todas as etapas
        etapas.forEach(etapa => etapa.classList.remove('ativa'));

        // Mostra a etapa certa
        const etapaAtual = document.getElementById('etapa' + numero);
        if (etapaAtual) {
            etapaAtual.classList.add('ativa');
        }

        // Atualiza os indicadores (círculos 1, 2, 3)
        indicadores.forEach((ind, index) => {
            const numIndicador = index + 1;
            ind.classList.remove('ativa', 'concluida');

            if (numIndicador < numero) {
                ind.classList.add('concluida');
            } else if (numIndicador === numero) {
                ind.classList.add('ativa');
            }
        });

        // Se entrou na etapa 3, atualiza o resumo
        if (String(numero) === '3') {
            atualizarResumo();
        }

        // Sobe a página
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // ==========================================
    // BOTÕES "PRÓXIMO"
    // ==========================================
    botoesProximo.forEach(btn => {
        btn.addEventListener('click', function () {
            const proxima = this.getAttribute('data-proxima');

            // Validação da etapa 1
            if (this.closest('#etapa1')) {
                const hemocentroSelecionado = document.querySelector('input[name="hemocentro"]:checked');
                if (!hemocentroSelecionado) {
                    alert('Selecione um hemocentro antes de continuar.');
                    return;
                }
            }

            // Validação da etapa 2
            if (this.closest('#etapa2')) {
                const tipoSelecionado = document.querySelector('input[name="tipo_doacao"]:checked');
                const dataSelecionada = document.querySelector('input[name="data"]').value;
                const horarioSelecionado = document.querySelector('input[name="horario"]:checked');

                if (!tipoSelecionado) {
                    alert('Selecione o tipo de doação.');
                    return;
                }
                if (!dataSelecionada) {
                    alert('Selecione uma data.');
                    return;
                }
                if (!horarioSelecionado) {
                    alert('Selecione um horário.');
                    return;
                }

                // Preenche o resumo
                atualizarResumo();
            }

            mostrarEtapa(proxima);
        });
    });

    // ==========================================
    // BOTÕES "VOLTAR"
    // ==========================================
    botoesVoltar.forEach(btn => {
        btn.addEventListener('click', function () {
            const voltar = this.getAttribute('data-voltar');
            mostrarEtapa(voltar);
        });
    });

    // ==========================================
    // ATUALIZAR RESUMO (ETAPA 3)
    // ==========================================
    function atualizarResumo() {
        // Hemocentro
        const hemocentroSelecionado = document.querySelector('input[name="hemocentro"]:checked');
        if (hemocentroSelecionado) {
            const cardBase = hemocentroSelecionado.closest('.card-base');
            const nomeHemocentro = cardBase.querySelector('h3').textContent;
            document.getElementById('resumo-hemocentro').textContent = nomeHemocentro;
        }

        // Tipo de doação
        const tipoSelecionado = document.querySelector('input[name="tipo_doacao"]:checked');
        if (tipoSelecionado) {
            document.getElementById('resumo-tipo').textContent = tipoSelecionado.value;
        }

        // Data
        const dataSelecionada = document.querySelector('input[name="data"]').value;
        if (dataSelecionada) {
            // Formata de YYYY-MM-DD para DD/MM/YYYY
            const partes = dataSelecionada.split('-');
            const dataFormatada = `${partes[2]}/${partes[1]}/${partes[0]}`;
            document.getElementById('resumo-data').textContent = dataFormatada;
        }

        // Horário
        const horarioSelecionado = document.querySelector('input[name="horario"]:checked');
        if (horarioSelecionado) {
            document.getElementById('resumo-horario').textContent = horarioSelecionado.value;
        }
    }

    // ==========================================
    // DATA MÍNIMA (hoje)
    // ==========================================
    const campoData = document.getElementById('data');
    if (campoData) {
        const hoje = new Date();
        const ano = hoje.getFullYear();
        const mes = String(hoje.getMonth() + 1).padStart(2, '0');
        const dia = String(hoje.getDate()).padStart(2, '0');
        const dataMinima = `${ano}-${mes}-${dia}`;
        campoData.setAttribute('min', dataMinima);
    }

    // ==========================================
    // VALIDAÇÃO GERAL NO SUBMIT
    // ==========================================
    const form = document.getElementById('form-agendamento');
    if (form) {
        form.addEventListener('submit', function (e) {
            // Confere se tudo tá preenchido
            const hemocentro = document.querySelector('input[name="hemocentro"]:checked');
            const tipo = document.querySelector('input[name="tipo_doacao"]:checked');
            const data = document.querySelector('input[name="data"]').value;
            const horario = document.querySelector('input[name="horario"]:checked');

            if (!hemocentro || !tipo || !data || !horario) {
                e.preventDefault();
                alert('Preencha todos os campos antes de confirmar.');
                return false;
            }
        });
    }

});