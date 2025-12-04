(function(){
  const key = 'gm-theme';
  // Default to light for the new Apple-like theme
  const current = localStorage.getItem(key) || 'light';
  document.documentElement.setAttribute('data-theme', current);
  
  const btn = document.getElementById('gm-theme-toggle');
  const icon = btn ? btn.querySelector('i') : null;

  function updateIcon(theme) {
    if(!icon) return;
    if(theme === 'dark') {
      icon.classList.remove('bi-moon-stars');
      icon.classList.add('bi-sun');
    } else {
      icon.classList.remove('bi-sun');
      icon.classList.add('bi-moon-stars');
    }
  }

  if(btn){
    updateIcon(current);
    btn.addEventListener('click', ()=>{
      const currentTheme = document.documentElement.getAttribute('data-theme');
      const next = (currentTheme === 'dark') ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem(key, next);
      updateIcon(next);
    });
  }
})();
