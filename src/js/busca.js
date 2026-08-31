// Busca e filtro 100% client-side, sem dependências, sem backend.
// Fase 0/1: adequado para dezenas/centenas de perfis. Se crescer muito, trocar por FlexSearch (Fase 2).
(function () {
  const campoBusca = document.getElementById("busca");
  const cards = Array.from(document.querySelectorAll("#grade-resultados .card"));
  const msgVazio = document.getElementById("msg-vazio");
  const botoesArea = Array.from(document.querySelectorAll("#filtros-area .filtro-chip"));

  let areaAtiva = "";

  function normaliza(texto) {
    return (texto || "").toLowerCase();
  }

  function aplicarFiltro() {
    const termo = normaliza(campoBusca.value).trim();
    let visiveis = 0;

    cards.forEach((card) => {
      const alvo = [
        card.dataset.nome,
        card.dataset.areas,
        card.dataset.especialidades,
        card.dataset.municipio,
      ].join(" ");

      const bateTermo = !termo || alvo.includes(termo);
      const bateArea = !areaAtiva || card.dataset.areas.includes(areaAtiva);
      const visivel = bateTermo && bateArea;

      card.hidden = !visivel;
      if (visivel) visiveis += 1;
    });

    msgVazio.hidden = visiveis > 0;
  }

  campoBusca.addEventListener("input", aplicarFiltro);

  botoesArea.forEach((botao) => {
    botao.addEventListener("click", () => {
      areaAtiva = normaliza(botao.dataset.filtroArea);
      botoesArea.forEach((b) => b.setAttribute("aria-pressed", b === botao ? "true" : "false"));
      aplicarFiltro();
    });
  });
})();
