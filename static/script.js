let main = document.querySelector('main');
main.addEventListener('click', (e) => {
  const todoId = e.target.dataset.id;

  if (e.target.classList.contains('btn-danger')) {
    if (confirm('Are you sure you want to delete this element?')) {
      // Realiza una solicitud de eliminación al servidor Flask
      fetch(`/delete_todo/${todoId}`, {
        method: 'DELETE',
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            location.reload();
          }
        })
        .catch((error) => {
          console.error('Error when delete the element', error);
        });
    }
  } else if (
    e.target.classList.contains('btn-success') ||
    e.target.classList.contains('btn-secondary')
  ) {
    fetch(`/update_todo/${todoId}`, {
      method: 'PUT',
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          const cardContainer = document.querySelector(
            `.card-container[data-id="${todoId}"]`
          );
          const header = document.querySelector(
            `.card-header[data-id="${todoId}"]`
          );
          const title = document.querySelector(
            `.card-title[data-id="${todoId}"]`
          );
          const text = document.querySelector(
            `.card-text[data-id="${todoId}"]`
          );
          const button = document.querySelector(`.btn[data-id="${todoId}"]`);
          if (cardContainer) {
            cardContainer.classList.toggle('opacity-25');
            button.classList.toggle('btn-success');
            button.classList.toggle('btn-secondary');
            header.classList.toggle('line-through');
            title.classList.toggle('line-through');
            text.classList.toggle('line-through');
          }
        }
      })
      .catch((error) => {
        console.error('Error when change the state', error);
      });
  }
  e.stopPropagation();
});

setTimeout(function () {
  const flashMessages = document.querySelector('#flash-message');
  if (flashMessages) {
    flashMessages.style.display = 'none';
  }
}, 5000);

function makeEditable(element, todoId) {
  originText = element.innerHTML;
  element.contentEditable = true;
  element.focus();
  element.addEventListener('blur', function () {
    const editedText = element.innerHTML
      .replace(/<div><br><\/div>/g, '<br>')
      .replace(/<div>/g, '')
      .replace(/<\/div>/g, '\n');
    element.contentEditable = false;
    updateTodoText(todoId, editedText,element,originText);
  });
}

function updateTodoText(todoId, newText, element,originText) {
  if (confirm('You want to update this element?')) {
    fetch(`/update_text/${todoId}`, {
      method: 'PUT',
      body: JSON.stringify({ newText: newText }),
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then((response) => {
        if (response.status === 200) {
          console.log('Element updated successfully');
          location.reload();
        }
      })
      .catch((error) => {
        console.error('Error when update the element', error);
      });
  }else{
    element.innerHTML = originText;
  }
}
