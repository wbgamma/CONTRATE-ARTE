module.exports = function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy("src/img");
  eleventyConfig.addPassthroughCopy("src/css");
  eleventyConfig.addPassthroughCopy("src/js");
  // Fase 0/1: filtro em JS puro sobre os data-attributes do card (ver src/js/busca.js).
  // Fase 2, se o volume de perfis crescer: trocar por FlexSearch (client-side, ainda R$0).

  eleventyConfig.addFilter("primeiraLinha", (texto) => {
    if (!texto) return "";
    return texto.length > 140 ? texto.slice(0, 140).trim() + "…" : texto;
  });

  eleventyConfig.addFilter("linkWhatsApp", (numero) => {
    if (!numero) return null;
    const limpo = numero.replace(/\D/g, "");
    return `https://wa.me/${limpo}`;
  });

  eleventyConfig.addFilter("linkInstagram", (usuario) => {
    if (!usuario) return null;
    const limpo = usuario.replace("@", "").trim();
    return `https://instagram.com/${limpo}`;
  });

  return {
    dir: {
      input: "src",
      output: "_site",
      includes: "_includes",
      data: "_data",
    },
  };
};
