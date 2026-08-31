# Especificação do Google Form — Cadastro CONTRATE A ARTE

Pronto para copiar direto no Google Forms. Cada pergunta já está mapeada para a coluna
que `scripts/build_data.py` espera (coluna `CSV` na tabela) — quando a Sheets API
substituir o CSV mock, os títulos das perguntas do Forms viram os cabeçalhos das
colunas na planilha de respostas automaticamente, então **o texto da pergunta e o
nome da coluna devem bater**.

## Configurações do formulário (antes de criar as perguntas)

- **Configurações → Respostas → Coletar endereços de e-mail**: ativar. Permite avisar o
  artista quando o perfil for aprovado/rejeitado, sem precisar pedir e-mail de novo.
- **Configurações → Respostas → Permitir 1 resposta**: desativar (um artista pode
  querer corrigir reenviando; a triagem manual lida com duplicidade).
- Depois de publicado: **Respostas → planilha de destino → criar nova planilha** — é
  ela que vira a "planilha de administração".

## Texto de abertura do formulário

> **CONTRATE A ARTE — Cadastro de artistas e profissionais da cultura**
>
> Este cadastro alimenta um diretório público e gratuito, mantido pelo Coletivo WB,
> para conectar você a produtores, eventos e contratantes culturais.
>
> Preencha o que puder — só nome, área de atuação e um contato já são suficientes
> para um perfil mínimo. Quanto mais completo, mais fácil ser encontrado(a).
>
> **Seu perfil só fica público depois de revisado pela nossa equipe.** Isso costuma
> levar até alguns dias.
>
> Dúvidas: batalhawb2.0@gmail.com

---

## Seção 1 — Identificação

| Pergunta (Forms) | Tipo | Obrigatório | Coluna (CSV) |
|---|---|---|---|
| Nome artístico | Resposta curta | Sim | `nome_artistico` |
| Foto de perfil | Upload de arquivo (1 imagem, até 10MB) | Não | `foto_arquivo` |
| Município | Resposta curta | Sim | `municipio` |
| Bairro, distrito ou região (sem endereço exato) | Resposta curta | Não | `regiao` |

Texto de ajuda no campo "Bairro/região": *"Não pedimos endereço exato — só a região,
pra ajudar produtores a entender de onde você é."*

## Seção 2 — Atuação

| Pergunta (Forms) | Tipo | Obrigatório | Coluna (CSV) |
|---|---|---|---|
| Área de atuação | Caixas de seleção (Música, Audiovisual, Artes visuais, Dança, Teatro, Literatura, Artesanato, Produção cultural, Outro) | Sim | `area_atuacao` |
| Especialidades (ex.: DJ, Fotógrafo, MC, Grafiteiro, Produtor musical...) | Resposta curta | Não | `especialidades` |
| Bio curta (até ~300 caracteres) | Parágrafo | Não | `bio` |
| Há quantos anos atua? | Resposta curta (número) | Não | `tempo_atuacao_anos` |

Texto de ajuda em "Especialidades": *"Separe por vírgula se tiver mais de uma. Ex.:
DJ, Produção musical"* — o script junta por `|` internamente, então instrua vírgula no
Forms e trate a conversão vírgula→pipe no parser da Sheets API (ver nota técnica no
fim deste documento).

## Seção 3 — Trajetória e portfólio

| Pergunta (Forms) | Tipo | Obrigatório | Coluna (CSV) |
|---|---|---|---|
| Conte sua trajetória | Parágrafo | Não | `trajetoria` |
| Projetos realizados (um por linha) | Parágrafo | Não | `projetos` |
| Premiações (um por linha) | Parágrafo | Não | `premiacoes` |
| Participação em editais/projetos culturais (um por linha) | Parágrafo | Não | `editais` |
| Link(s) de portfólio (um por linha) | Parágrafo | Não | `portfolio_links` |
| Instagram (usuário, sem @) | Resposta curta | Não | `instagram` |
| YouTube (link do canal) | Resposta curta | Não | `youtube` |
| Spotify (link do perfil/artista) | Resposta curta | Não | `spotify` |
| Outros links relevantes (um por linha) | Parágrafo | Não | `outros_links` |

## Seção 4 — Contato (pelo menos um obrigatório)

> Texto de instrução na seção: **"Preencha pelo menos um destes três — é assim que o
> produtor vai te encontrar."** O Google Forms não valida "pelo menos 1 de 3" de forma
> nativa; isso é conferido na revisão manual (e o script já rejeita automaticamente
> cadastros sem nenhum contato, ver `linha_valida()` em `build_data.py`).

| Pergunta (Forms) | Tipo | Obrigatório | Coluna (CSV) |
|---|---|---|---|
| WhatsApp profissional (com DDD) | Resposta curta | Não* | `whatsapp` |
| E-mail profissional | Resposta curta | Não* | `email` |

*(Instagram da Seção 3 também conta como canal de contato válido.)*

## Seção 5 — Consentimento (LGPD)

| Pergunta (Forms) | Tipo | Obrigatório |
|---|---|---|
| Ver texto abaixo | Caixas de seleção (1 opção, deve poder ser marcada) | **Sim** |

> **Texto da pergunta de consentimento:**
>
> "Autorizo a publicação pública, no site CONTRATE A ARTE, dos dados de contato que
> enviei neste formulário (WhatsApp, e-mail e/ou Instagram, conforme o que eu
> preenchi), assim como das demais informações de perfil, foto e portfólio aqui
> fornecidas. Entendo que:
> - a publicação depende de revisão e aprovação prévia pela equipe do coletivo;
> - posso pedir correção ou remoção do meu perfil a qualquer momento, escrevendo para
>   batalhawb2.0@gmail.com;
> - meus dados de cadastro (mesmo os não publicados) ficam guardados na planilha de
>   administração do coletivo, usada só para gerenciar este diretório."
>
> ☐ **Li e autorizo, conforme descrito acima.**

Isso mapeia direto para a coluna `consentimento_publicacao` — marcado = `TRUE`.

---

## Nota técnica — da resposta do Forms até `artistas.json`

1. Cada resposta do Forms vira uma linha na planilha de respostas.
2. O admin adiciona (ou já existe por fórmula/Apps Script) uma coluna `status`, começando
   `pendente`, que o admin muda pra `aprovado`/`rejeitado`/`removido`.
3. Campos "um por linha" (projetos, premiações, editais, portfolio_links, outros_links)
   chegam do Forms com quebras de linha reais dentro da célula — o parser da Sheets API
   deve fazer `.split("\n")` nesses campos (hoje o CSV mock usa `|`; ao trocar pra Sheets
   API, ajustar `lista_de()` em `build_data.py` para aceitar quebra de linha também).
4. "Especialidades" chega com vírgula (`DJ, Produção musical`) — ajustar o parser pra
   `.split(",")` nesse campo específico, diferente dos campos "um por linha".
5. Foto: o Forms salva o upload no Drive do dono do formulário. O script de build
   precisa baixar via Drive API antes de comprimir — este é o pedaço mais arriscado
   tecnicamente (mencionado na Fase 0 da análise original) e deve ser testado cedo
   quando a integração real entrar.
