# Publicar no Cloudflare Pages

Gratuito para sempre no volume deste projeto: 500 builds/mês grátis (a automação
diária usa ~30), banda ilimitada, SSL incluso. Ver [README.md](../README.md) para a
tabela de custos completa.

## Passo a passo

1. Crie uma conta em https://dash.cloudflare.com/sign-up (grátis, só e-mail).
   **Use a conta institucional do coletivo**, não a pessoal de um integrante — mesmo
   motivo do Google: quem sai do coletivo não pode levar o acesso junto.
2. No painel, vá em **Workers & Pages → Create → Pages → Connect to Git**.
3. Autorize o Cloudflare a acessar o GitHub e selecione o repositório
   `wbgamma/CONTRATE-ARTE`.
4. Nas configurações de build, preencha exatamente:
   | Campo | Valor |
   |---|---|
   | Framework preset | `None` |
   | Build command | `npm run build:site` |
   | Build output directory | `_site` |
   | Root directory | `/` |

   **Por que só `build:site` e não `npm run build`:** o passo que fala com a
   planilha (`build:data`, o script Python) roda só no GitHub Actions, que já
   commita `src/_data/*.json` e as fotos processadas no repositório. O Cloudflare
   só constrói o HTML a partir do que já está commitado — se ele rodasse
   `build:data` também, cairia no CSV mock (sem as credenciais da planilha) e
   sobrescreveria os dados reais com dados fictícios a cada deploy.
5. Clique em **Save and Deploy**. O primeiro build leva 1-2 minutos.
6. Ao terminar, o Cloudflare dá uma URL gratuita. Dependendo de como o projeto foi
   criado, ela pode sair como `*.pages.dev` (fluxo clássico) ou `*.workers.dev`
   (fluxo unificado atual de "Workers com assets estáticos") — é a mesma
   infraestrutura gratuita nos dois casos. **Se a URL aparecer como "No URLs enabled"
   / domínio "Disabled"** na aba Overview do projeto, vá em **Domains** (ou clique no
   toggle ao lado do domínio `workers.dev`) e habilite — o deploy pode ter funcionado
   sem a URL pública estar ativa por padrão.
   URL em produção deste projeto: https://contrate-a-arte.batalhawb2-0.workers.dev
7. **Ative o Cloudflare Web Analytics** (Workers & Pages → seu projeto → Analytics →
   Web Analytics → Enable): grátis, sem cookies, dá pageviews/visitas pro relatório
   de impacto do edital.

## Depois disso

Todo `git push` na branch `main` (seja manual, seja pela automação do GitHub Actions)
dispara um novo build e deploy automático — não precisa fazer nada no Cloudflare de
novo depois do setup inicial.

## Se quiser um domínio próprio depois

Workers & Pages → seu projeto → Custom domains → Add a domain. Isso é o único item
com custo recorrente real (~R$40-60/ano de registro do domínio, pago no registrador,
não no Cloudflare) — decisão explicitamente adiada, ver README.md.
