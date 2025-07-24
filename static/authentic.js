 // ︙メニューの開閉処理
  const moreBtn = document.getElementById('moreBtn');
  const dropdown = document.getElementById('dropdownMenu');

  moreBtn.addEventListener('click', () => {
    dropdown.style.display = (dropdown.style.display === 'block') ? 'none' : 'block';
  });

  // メニュー外をクリックしたら閉じる
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.menu-dropdown')) {
      dropdown.style.display = 'none';
    }
  });z