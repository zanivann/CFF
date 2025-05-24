document.addEventListener('DOMContentLoaded', () => {
    console.log("O JavaScript foi carregado! A buscar dados...");
    let currentTransactions = []; // Para guardar as transações atuais

    // Referências aos elementos do DOM (a nossa "ponte" para o HTML)
    const form = document.getElementById('transaction-form');
    const transactionIdInput = document.getElementById('transaction-id');
    const descricaoInput = document.getElementById('descricao');
    const valorInput = document.getElementById('valor');
    const dataInput = document.getElementById('data');
    const tipoInput = document.getElementById('tipo');
    const categoriaSelect = document.getElementById('categoria');
    const contaSelect = document.getElementById('conta');
    const transactionsTableBody = document.getElementById('transactions-body');
    const saldoSpan = document.getElementById('saldo-total');
    const btnSave = document.getElementById('btn-save');
    const btnClear = document.getElementById('btn-clear');

    // URL base da nossa API (como o JS é servido pelo mesmo Flask, podemos usar caminhos relativos)
    const API_URL = '/api';

    // --- Funções para Buscar Dados ---

    // Função genérica para buscar dados da API
    async function fetchData(endpoint) {
        try {
            const response = await fetch(`${API_URL}/${endpoint}`);
            if (!response.ok) {
                throw new Error(`Erro ao buscar ${endpoint}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Falha ao buscar dados de ${endpoint}:`, error);
            alert(`Não foi possível carregar os dados de ${endpoint}. Verifica a consola.`);
            return []; // Retorna um array vazio em caso de erro
        }
    }

    // Busca e preenche as categorias
    async function loadCategorias() {
        const categorias = await fetchData('categorias');
        renderDropdown(categoriaSelect, categorias, 'Selecione uma Categoria');
    }

    // Busca e preenche as contas
    async function loadContas() {
        const contas = await fetchData('contas');
        renderDropdown(contaSelect, contas, 'Selecione uma Conta');
    }

    // Busca e preenche as transações
    async function loadTransacoes() {
        const transacoes = await fetchData('transacoes');
        renderTransacoes(transacoes);
        updateSaldo(transacoes);
    }

    // --- Funções para Renderizar (Mostrar na Tela) ---

    // Preenche um dropdown (select) com opções
    function renderDropdown(selectElement, items, defaultOptionText) {
        selectElement.innerHTML = ''; // Limpa opções existentes
        // Adiciona a opção padrão (placeholder)
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = defaultOptionText;
        defaultOption.disabled = true; // Não pode ser selecionada
        defaultOption.selected = true; // Aparece por defeito
        selectElement.appendChild(defaultOption);

        // Adiciona os itens recebidos da API
        items.forEach(item => {
            const option = document.createElement('option');
            option.value = item.id;
            option.textContent = item.nome;
            selectElement.appendChild(option);
        });
         // Adiciona uma opção 'Nenhuma' para ser opcional
        const nenhumaOption = document.createElement('option');
        nenhumaOption.value = ''; // Valor vazio para representar 'Nenhuma'
        nenhumaOption.textContent = 'Nenhuma';
        selectElement.appendChild(nenhumaOption);
    }

    // Preenche a tabela com as transações
     function renderTransacoes(transacoes) {
        currentTransactions = transacoes; // <-- ADICIONA ESTA LINHA
        transactionsTableBody.innerHTML = ''; // Limpa a tabela

        if (transacoes.length === 0) {
            transactionsTableBody.innerHTML = '<tr><td colspan="7" style="text-align:center;">Nenhuma transação encontrada.</td></tr>';
            return;
        }

        transacoes.forEach(t => {
            const tr = document.createElement('tr');

            const valorFormatado = parseFloat(t.valor).toFixed(2);
            const dataFormatada = new Date(t.data + 'T00:00:00').toLocaleDateString('pt-BR'); // Ajusta para evitar problemas de fuso

            // Define a cor e o sinal com base no tipo
            let valorHtml;
            if (t.tipo === 'receita') {
                valorHtml = `<td class="receita">+ R$ ${valorFormatado}</td>`;
            } else {
                valorHtml = `<td class="despesa">- R$ ${valorFormatado}</td>`;
            }

            tr.innerHTML = `
                <td>${dataFormatada}</td>
                <td>${t.descricao}</td>
                ${valorHtml}
                <td>${t.tipo.charAt(0).toUpperCase() + t.tipo.slice(1)}</td>
                <td>${t.categoria_nome || 'N/A'}</td>
                <td>${t.conta_nome || 'N/A'}</td>
                <td>
                    <button class="btn-edit" data-id="${t.id}">✏️</button>
                    <button class="btn-delete" data-id="${t.id}">🗑️</button>
                </td>
            `;
            transactionsTableBody.appendChild(tr);
        });
    }

    // Calcula e atualiza o saldo total
    function updateSaldo(transacoes) {
        const total = transacoes.reduce((acc, t) => {
            return t.tipo === 'receita' ? acc + t.valor : acc - t.valor;
        }, 0); // Começa com 0

        saldoSpan.textContent = `R$ ${total.toFixed(2)}`;
        saldoSpan.style.color = total >= 0 ? 'green' : 'red';
    }


    // --- Carregamento Inicial ---

    // Função para carregar tudo quando a página abre
    async function loadInitialData() {
        await loadCategorias();
        await loadContas();
        await loadTransacoes();
        // Configura a data de hoje no formulário
        dataInput.valueAsDate = new Date();
    }

    // Chama a função de carregamento inicial
    loadInitialData();

    // --- Funções para Enviar Dados (POST/PUT/DELETE) ---

    // Função genérica para enviar dados (POST/PUT)
    async function postData(endpoint, data, method = 'POST', id = null) {
        const url = id ? `${API_URL}/${endpoint}/${id}` : `${API_URL}/${endpoint}`;
        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.erro || `Erro ao ${method === 'POST' ? 'adicionar' : 'atualizar'} ${endpoint}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Falha ao enviar dados para ${endpoint}:`, error);
            alert(`Erro: ${error.message}`);
            return null;
        }
    }

    // Função para adicionar nova categoria ou conta
    async function addNewOption(tipo) {
        const nome = prompt(`Digite o nome da nova ${tipo}:`);
        if (nome && nome.trim() !== '') {
            const endpoint = tipo === 'categoria' ? 'categorias' : 'contas';
            const result = await postData(endpoint, { nome: nome.trim() });
            if (result) {
                alert(`${tipo.charAt(0).toUpperCase() + tipo.slice(1)} adicionada com sucesso!`);
                if (tipo === 'categoria') {
                    await loadCategorias();
                    categoriaSelect.value = result.id; // Seleciona a nova opção
                } else {
                    await loadContas();
                    contaSelect.value = result.id; // Seleciona a nova opção
                }
            }
        }
    }

    // --- Funções do Formulário ---

    // Limpa o formulário e volta ao estado inicial
    function clearForm() {
        form.reset();
        transactionIdInput.value = '';
        dataInput.valueAsDate = new Date();
        tipoInput.value = 'despesa';
        categoriaSelect.value = '';
        contaSelect.value = '';
        btnSave.textContent = 'Salvar'; // Garante que volta a 'Salvar'
        document.querySelector('.form-container h2').textContent = 'Nova Transação / Editar Transação'; // Restaura título
    }
    // Lida com o 'submit' do formulário (Salvar)
    async function handleSaveTransaction(event) {
        event.preventDefault();

        const transactionData = {
            descricao: descricaoInput.value.trim(),
            valor: parseFloat(valorInput.value),
            data: dataInput.value,
            tipo: tipoInput.value,
            categoria_id: categoriaSelect.value ? parseInt(categoriaSelect.value) : null,
            conta_id: contaSelect.value ? parseInt(contaSelect.value) : null,
        };

        if (!transactionData.descricao || isNaN(transactionData.valor) || !transactionData.data) {
            alert('Por favor, preencha a Descrição, Valor e Data.');
            return;
        }

        const id = transactionIdInput.value;
        let result;

        if (id) {
            // Se tem ID, é uma atualização (PUT)
            result = await postData('transacoes', transactionData, 'PUT', parseInt(id)); // <-- MODIFICADO
        } else {
            // Se não tem ID, é uma adição (POST)
            result = await postData('transacoes', transactionData, 'POST');
        }

        if (result) {
            alert(`Transação ${id ? 'atualizada' : 'adicionada'} com sucesso!`); // <-- MODIFICADO
            clearForm();
            await loadTransacoes();
        }
    }

    // --- Funções para Enviar Dados (POST/PUT/DELETE) ---
    // (A função postData já existe)

    // Função genérica para enviar DELETE
    async function deleteData(endpoint, id) {
        const url = `${API_URL}/${endpoint}/${id}`;
        try {
            const response = await fetch(url, {
                method: 'DELETE',
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.erro || `Erro ao apagar ${endpoint}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Falha ao apagar dados de ${endpoint}:`, error);
            alert(`Erro: ${error.message}`);
            return null;
        }
    }

    // --- Funções da Tabela (Editar/Apagar) ---

    // Preenche o formulário com dados para edição
    function populateFormForEdit(id) {
        // Procura a transação na nossa lista guardada
        const transaction = currentTransactions.find(t => t.id === id);
        if (!transaction) {
            alert('Transação não encontrada!');
            return;
        }

        // Preenche os campos do formulário
        transactionIdInput.value = transaction.id;
        descricaoInput.value = transaction.descricao;
        valorInput.value = transaction.valor;
        dataInput.value = transaction.data; // O formato YYYY-MM-DD já deve estar correto
        tipoInput.value = transaction.tipo;
        // Se a categoria_id/conta_id for null, seleciona '', senão seleciona o ID
        categoriaSelect.value = transaction.categoria_id === null ? '' : transaction.categoria_id;
        contaSelect.value = transaction.conta_id === null ? '' : transaction.conta_id;

        // Atualiza a interface para o modo de edição
        btnSave.textContent = 'Atualizar';
        document.querySelector('.form-container h2').textContent = 'Editar Transação';
        window.scrollTo(0, 0); // Rola a página para o topo (onde está o form)
        descricaoInput.focus(); // Coloca o foco no primeiro campo
    }

    // Lida com o clique para apagar
    async function handleDeleteTransaction(id) {
        if (confirm('Tem a certeza que deseja apagar esta transação?')) {
            const result = await deleteData('transacoes', id);
            if (result) {
                alert('Transação apagada com sucesso!');
                await loadTransacoes(); // Recarrega a tabela e o saldo
                clearForm(); // Limpa o formulário caso estivesse a editar este item
            }
        }
    }

    // Lida com cliques na tabela (delegação de eventos)
    function handleTableClick(event) {
        const target = event.target; // Onde o clique ocorreu

        // Verifica se foi no botão de apagar
        if (target.classList.contains('btn-delete')) {
            const id = parseInt(target.dataset.id); // Pega o ID do 'data-id'
            handleDeleteTransaction(id);
        }
        // Verifica se foi no botão de editar
        else if (target.classList.contains('btn-edit')) {
            const id = parseInt(target.dataset.id); // Pega o ID
            populateFormForEdit(id);
        }
    }

    // --- Configuração dos Event Listeners ---

    // Listener para o formulário (quando clica em 'Salvar')
    form.addEventListener('submit', handleSaveTransaction);
    // Listener para cliques na tabela (para botões de Editar e Apagar)
    transactionsTableBody.addEventListener('click', handleTableClick);

    // Listener para o botão 'Limpar'
    btnClear.addEventListener('click', clearForm);

    // Listeners para os botões '+' de Categoria e Conta
    document.querySelectorAll('.btn-add').forEach(button => {
        button.addEventListener('click', (event) => {
            const tipo = event.target.dataset.tipo; // Pega 'categoria' ou 'conta' do data-attribute
            addNewOption(tipo);
        });
    });

    // TODO: Adicionar Event Listeners para botões de editar e apagar na tabela.

    // TODO: Adicionar Event Listeners para formulário, botões de adicionar, editar e apagar.

}); // Fim do 'DOMContentLoaded'