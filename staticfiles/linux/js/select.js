function toggleSelectAll(selectAllCheckbox) {
  const checkboxes = document.querySelectorAll('.fileCheckbox');
  checkboxes.forEach(checkbox => {
      checkbox.checked = selectAllCheckbox.checked;
  });
  toggleDeleteButton();
}

function toggleDeleteButton() {
  const deleteButton = document.getElementById('deleteSelected');
  const checkboxes = document.querySelectorAll('.fileCheckbox:checked');
  deleteButton.style.display = checkboxes.length > 0 ? 'inline-block' : 'none';
}
