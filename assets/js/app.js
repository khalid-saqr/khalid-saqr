
(function(){
  const clusterButtons = document.querySelectorAll('[data-filter]');
  const chips = document.querySelectorAll('.id-chip');
  clusterButtons.forEach(btn => btn.addEventListener('click', () => {
    const filter = btn.dataset.filter;
    clusterButtons.forEach(b => b.classList.toggle('active', b === btn));
    chips.forEach(chip => {
      chip.style.opacity = (filter === 'all' || chip.dataset.cluster === filter) ? '1' : '.32';
    });
  }));
  const domains = document.querySelectorAll('.domain-node');
  domains.forEach(btn => btn.addEventListener('click', () => {
    btn.classList.toggle('active');
  }));
  const input = document.getElementById('pubSearch');
  if(input){
    input.addEventListener('input', () => {
      const q = input.value.trim().toLowerCase();
      document.querySelectorAll('.pub-card').forEach(card => {
        card.classList.toggle('hidden', q && !card.textContent.toLowerCase().includes(q));
      });
    });
  }
  if('serviceWorker' in navigator){
    window.addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(()=>{}));
  }
})();
