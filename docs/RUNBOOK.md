# Manual de administração — CONTRATE A ARTE

Escrito para quem não escreveu o código. Se algo aqui estiver desatualizado, o código é
a fonte da verdade — mas isso significa que este arquivo precisa ser revisado sempre
que o pipeline mudar.

## Como aprovar um novo cadastro (rotina do dia a dia)

1. Abra a planilha "CONTRATE A ARTE — Cadastros" no Google Sheets.
2. Cada linha nova chega com status `pendente`.
3. Revise: nome, área, pelo menos um contato preenchido (WhatsApp/e-mail/Instagram),
   foto sem conteúdo impróprio.
4. Mude a coluna `status` para `aprovado` (ou `rejeitado`, se não passar na revisão).
5. Confirme que a coluna `consentimento_publicacao` está `TRUE` — sem isso o perfil
   nunca é publicado, mesmo aprovado (é uma trava proposital do script).
6. Pronto. O site atualiza sozinho no próximo ciclo automático (hoje: 1x/dia via
   GitHub Actions — ver `.github/workflows/build-deploy.yml`). Para forçar agora, use
   o botão "Run workflow" na aba Actions do GitHub.

## Critérios de rejeição (escrever aqui antes de precisar decidir sob pressão)

- Sem nenhum canal de contato preenchido.
- Conteúdo ofensivo, discurso de ódio, ou não relacionado a atividade cultural.
- Foto inapropriada ou de terceiros sem autorização.
- Dado de contato que não é do próprio artista.

*(Este é um ponto de partida — o coletivo deve revisar e ajustar esta lista antes do
lançamento público.)*

## Quem tem acesso a quê (bus factor — mantenha isto atualizado)

- Conta Google institucional do coletivo: administra Forms + Sheets. **Não deve ser a
  conta pessoal de um único integrante** — se essa pessoa sair do coletivo (como
  aconteceu com Caelis), ninguém mais consegue administrar.
- Repositório GitHub: pelo menos 2 pessoas devem ter permissão de admin.
- Cloudflare Pages: pelo menos 2 pessoas com acesso à conta.

## Se o site parar de atualizar

1. Veja a aba "Actions" do repositório no GitHub — se o último "Publicar site" falhou,
   o log mostra o erro. GitHub avisa por e-mail automaticamente quem está inscrito no
   repositório quando uma Action falha.
2. Causas mais prováveis: credencial da Sheets API expirada, planilha com uma linha
   mal formatada, cota de imagem excedida.

## Se um artista pedir remoção ou correção dos dados

- Remoção: marque `status` como `removido` na planilha (não apague a linha — mantém
  histórico interno). No próximo build, o perfil some do site.
- Correção: edite a linha diretamente na planilha.
- **Limitação conhecida:** o histórico do Git (repositório público) mantém versões
  antigas dos arquivos publicados anteriormente. Isso está documentado na política de
  privacidade como uma limitação aceita. Se um pedido de remoção exigir apagar
  também do histórico, isso requer reescrever o histórico do repositório
  manualmente (ação rara, avaliar caso a caso).

## Pendências para tirar do papel (ver README.md "Próximos passos")

- [ ] Criar o Google Form real + planilha (conta institucional)
- [ ] Criar o repositório GitHub público
- [ ] Conectar Cloudflare Pages ao repositório
- [ ] Criar service account da Google Sheets API e configurar o secret
      `SHEETS_SERVICE_ACCOUNT_JSON` no GitHub Actions
- [ ] Trocar `carregar_linhas()` em `scripts/build_data.py` de CSV mock para a Sheets API
- [ ] Escrever o texto de consentimento/privacidade que aparece no Google Form
- [ ] Configurar Cloudflare Web Analytics no domínio do Pages
