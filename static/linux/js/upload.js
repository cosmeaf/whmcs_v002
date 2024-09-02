document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const fileInput = document.getElementById('formFile');
    const file = fileInput.files[0];

    if (file) {
        const formData = new FormData();
        formData.append('file', file);

        fetch(uploadProjectUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showAlert('Arquivo carregado com sucesso!', 'success');
                $('#uploadModal').modal('hide');
                window.location.reload();  // Recarregar a página para atualizar a lista de projetos
            } else {
                showAlert('Erro ao carregar o arquivo: ' + data.message, 'danger');
            }
        })
        .catch(error => {
            showAlert('Erro no upload: ' + error, 'danger');
        });
    } else {
        showAlert('Por favor, selecione um arquivo.', 'warning');
    }
});
