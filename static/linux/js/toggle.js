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
        console.log("Checkbox selecionado:", filePath);
    });

    console.log("Arquivos atualmente selecionados:", selectedFiles);

    const hasZipFile = selectedFiles.some(filePath => filePath.endsWith('.zip'));
    const deleteButton = document.getElementById('deleteSelected');
    const unzipButton = document.getElementById('unzipSelected');

    deleteButton.style.display = selectedFiles.length > 0 ? 'inline-block' : 'none';
    unzipButton.style.display = hasZipFile ? 'inline-block' : 'none';

    // Certifique-se de que a função 'deleteFiles' é usada corretamente aqui
    deleteButton.onclick = function() {
        deleteFiles(selectedFiles);  // O nome correto da função é 'deleteFiles'
    };

    unzipButton.onclick = function() {
        selectedFiles.forEach(filePath => {
            if (filePath.endsWith('.zip')) {
                unzipFile(filePath);
            }
        });
    };
}
