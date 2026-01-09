var typed = new Typed(".text", {
    strings: [" Sistema é muito versatil traz muitas Valencias",
       "Está vocacionado apedidos de férias dos funcionarios desta empresa com adevida autorização", 
       "Então faça já o seu pedido por favor caro funcionario!"],
    typeSpeed: 100,
    backSpeed: 100,
    loop: true
    
});
const botao = document.getElementById('botao');

    function criarExplosao() {
      const clone = botao.cloneNode(true);
      clone.classList.add('explode', 'clone');
      document.body.appendChild(clone);

      
      setTimeout(() => {
        clone.remove();
      }, 600); 
    }

    
    setInterval(criarExplosao, 1000);