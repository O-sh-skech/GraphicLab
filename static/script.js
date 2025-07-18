const functionInput = document.getElementById('functionInput');

    document.querySelectorAll('.button-panel button[data-insert]').forEach(button => {
      button.addEventListener('click', () => {
        const insertValue = button.getAttribute('data-insert');
        const cursorPos = functionInput.selectionStart;
        const before = functionInput.value.substring(0, cursorPos);
        const after = functionInput.value.substring(cursorPos);
        functionInput.value = before + insertValue + after;
        functionInput.focus();
        functionInput.selectionStart = functionInput.selectionEnd = cursorPos + insertValue.length;
      });
    });
/*
    document.getElementById('plotBtn').addEventListener('click', () => {
        const inputValue = document.getElementById('functionInput').value;
        if (inputValue.trim() === "") {
            alert("入力が空です！");
            return;
        }
      
        message.textContent = "入力された関数: " + inputValue;
        alert("入力された関数: " + inputValue); // または console.log(inputValue)

    });
*/