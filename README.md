# CONTRATE A ARTE

Diretório público e gratuito de artistas e profissionais da cultura, mantido pelo
[Coletivo WB](https://instagram.com/coletivowb) como legado do projeto **V-Norte II**
(edital PNAB Pedro Leopoldo 01/2026).

**Objetivo:** um produtor busca por área/especialidade/município, encontra o perfil de
um artista, avalia a trajetória e entra em contato direto por WhatsApp/Instagram/e-mail.
Sem chat interno, sem login de artista, sem mensalidade nenhuma.

## Regra arquitetural inegociável: custo recorrente = R$0

Toda peça deste projeto foi escolhida para não ter mensalidade:

| Peça | Função | Custo recorrente |
|---|---|---|
| Google Forms + Sheets | cadastro e aprovação administrativa | R$0 |
| Python (`scripts/build_data.py`) | planilha aprovada → JSON público + fotos comprimidas | R$0 |
| GitHub Actions (repo **público**) | roda o script automaticamente a cada aprovação | R$0 (ilimitado em repo público) |
| Eleventy | gera o site estático a partir do JSON | R$0 |
| Cloudflare Pages | hospedagem + SSL | R$0 |
| Cloudflare Web Analytics | métricas de acesso, sem cookies | R$0 |
| Domínio próprio | opcional | ~R$40-60/ano *(único item não-R$0; por ora usamos o subdomínio gratuito `*.pages.dev`)* |

Se algum dia uma peça exigir pagamento, o critério é: procurar alternativa gratuita
primeiro, documentar a troca, nunca aceitar dependência de mensalidade em silêncio.

## Como rodar localmente

```bash
npm install
npm run build   # roda o script Python (planilha -> JSON + fotos) e depois o Eleventy
npm run dev     # sobe um servidor local em http://localhost:8080 com live-reload
```

Hoje o script lê `data/mock_planilha_exemplo.csv` (dados fictícios, só para testar o
pipeline). Quando a planilha real do Google Sheets existir, `scripts/build_data.py`
troca a função `carregar_linhas()` para ler da Sheets API em vez do CSV — é o único
ponto do código que muda.

## Estrutura do projeto

```
data/                   dados brutos (CSV mock, fotos pendentes) - nunca contém dados reais aprovados
scripts/build_data.py   planilha aprovada -> src/_data/artistas.json + fotos otimizadas
src/                     código-fonte do site Eleventy
  _data/                 artistas.json e stats.json (gerados pelo script, não editar à mão)
  _includes/base.njk     layout comum
  index.njk              página de busca/listagem
  artistas.njk           template de perfil individual (1 página por artista)
  css/ js/ img/           estáticos
docs/                    documentação para quem for administrar o projeto no futuro
.github/workflows/       automação (GitHub Actions) que publica o site sozinho
```

## Estado atual: Fase 0 (spike) concluída

Provado ponta a ponta com dados fictícios: planilha → filtro de aprovação/consentimento
→ JSON → fotos em webp comprimidas → site estático → busca client-side → botão de
contato com link de WhatsApp correto.

**Próximos passos (exigem ações do usuário, não posso criar contas por vocês):**
1. Criar o Google Form de cadastro + a planilha de administração (conta institucional do
   coletivo, não pessoal).
2. Criar o repositório no GitHub (**público**, é o que garante Actions ilimitado grátis).
3. Criar a conta Cloudflare Pages e conectar ao repositório.
4. Criar a service account do Google Sheets API e plugar em `carregar_linhas()`.

Ver [docs/RUNBOOK.md](docs/RUNBOOK.md) para o passo a passo detalhado de administração.
