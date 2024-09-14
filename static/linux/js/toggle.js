// Função para selecionar ou desmarcar todas as checkboxes
function toggleSelectAll(selectAllCheckbox) {
    const checkboxes = document.querySelectorAll('.fileCheckbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
    });
    toggleActionButtons();  // Atualizar os botões de ação com base na seleção
}

// Função para ativar/desativar os botões de ação (Descompactar e Excluir)
function toggleActionButtons() {
    const selectedFiles = [];
    const checkboxes = document.querySelectorAll('.fileCheckbox:checked');

    checkboxes.forEach(checkbox => {
        const filePath = checkbox.getAttribute('data-path');
        selectedFiles.push(filePath);
    });

    const hasZipFile = selectedFiles.some(filePath => filePath.toLowerCase().endsWith('.zip'));
    const deleteButton = document.getElementById('deleteSelected');
    const unzipButton = document.getElementById('unzipSelected');

    deleteButton.style.display = selectedFiles.length > 0 ? 'inline-block' : 'none';
    unzipButton.style.display = hasZipFile ? 'inline-block' : 'none';

    // Usando showConfirm para confirmar a exclusão
    deleteButton.onclick = function() {
        showConfirm('Tem certeza de que deseja excluir os arquivos selecionados?', function() {
            deleteFile(selectedFiles);  // Função de callback quando o usuário confirma
        }, function() {
            showAlert('Exclusão cancelada!', 'info');
        });
    };

    unzipButton.onclick = function() {
        selectedFiles.forEach(filePath => {
            if (filePath.toLowerCase().endsWith('.zip')) {
                unzipFile(filePath);
            }
        });
    };
}

