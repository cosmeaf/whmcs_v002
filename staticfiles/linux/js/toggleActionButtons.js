// static/linux/js/toggleActionButtons.js

function toggleActionButtons() {
  const deleteButton = document.getElementById('deleteSelected');
  const unzipButton = document.getElementById('unzipSelected');
  const checkboxes = document.querySelectorAll('.fileCheckbox:checked');

  // Log para verificar se os checkboxes estão sendo selecionados corretamente
  console.log("Checkboxes selecionados:", checkboxes.length > 0 ? true : false);
  checkboxes.forEach(checkbox => {
      console.log("Checkbox selecionado:", checkbox.getAttribute('data-path'));
  });

  const hasZipFile = Array.from(checkboxes).some(checkbox => checkbox.getAttribute('data-path').endsWith('.zip'));

  deleteButton.style.display = checkboxes.length > 0 ? 'inline-block' : 'none';
  unzipButton.style.display = hasZipFile ? 'inline-block' : 'none';
}
