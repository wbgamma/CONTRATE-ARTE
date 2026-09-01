/**
 * criar_google_form.gs — cria o Google Form "CONTRATE A ARTE" automaticamente,
 * já com todas as seções, perguntas e o texto de consentimento LGPD, e linka
 * a uma planilha nova (a "planilha de administração").
 *
 * COMO USAR:
 *   1. Abra https://script.google.com (logado na conta institucional do coletivo)
 *   2. Novo projeto → apague o conteúdo padrão → cole este arquivo inteiro
 *   3. Rode a função criarFormularioContrateAArte() (menu Executar, ou Ctrl+Enter)
 *   4. Na primeira vez, o Google vai pedir autorização — é normal, autorize
 *      (o script só age dentro da SUA conta, nunca sai dela)
 *   5. Veja o resultado em Execuções (ou Exibir → Registros): vai mostrar o link
 *      do formulário e o link da planilha de respostas
 *
 * Espelha exatamente docs/GOOGLE-FORM.md — se a spec mudar lá, atualizar aqui também.
 */

function criarFormularioContrateAArte() {
  const form = FormApp.create('CONTRATE A ARTE — Cadastro de artistas e profissionais da cultura');

  form.setDescription(
    'Este cadastro alimenta um diretório público e gratuito, mantido pelo Coletivo WB, ' +
    'para conectar você a produtores, eventos e contratantes culturais.\n\n' +
    'Preencha o que puder — só nome, área de atuação e um contato já são suficientes ' +
    'para um perfil mínimo. Quanto mais completo, mais fácil ser encontrado(a).\n\n' +
    'Seu perfil só fica público depois de revisado pela nossa equipe. Isso costuma ' +
    'levar até alguns dias.\n\n' +
    'Dúvidas: batalhawb2.0@gmail.com'
  );

  form.setCollectEmail(true);
  form.setLimitOneResponsePerUser(false);
  form.setAllowResponseEdits(true);

  // ---------- Seção 1 — Identificação ----------
  form.addSectionHeaderItem().setTitle('Identificação');

  form.addTextItem().setTitle('Nome artístico').setRequired(true);

  try {
    form.addFileUploadItem().setTitle('Foto de perfil').setRequired(false);
  } catch (e) {
    // Upload de arquivo via Apps Script depende do Forms permitir a criação
    // programática desse tipo de item; se falhar aqui, adicione a pergunta
    // manualmente na interface do Forms (Inserir → Upload de arquivo).
    Logger.log('Aviso: não foi possível criar a pergunta de upload de foto automaticamente. ' +
      'Adicione manualmente: "Foto de perfil" (Upload de arquivo, 1 imagem, até 10MB, opcional).');
  }

  form.addTextItem().setTitle('Município').setRequired(true);

  form.addTextItem()
    .setTitle('Bairro, distrito ou região (sem endereço exato)')
    .setHelpText('Não pedimos endereço exato — só a região, pra ajudar produtores a entender de onde você é.')
    .setRequired(false);

  // ---------- Seção 2 — Atuação ----------
  form.addPageBreakItem().setTitle('Atuação');

  form.addCheckboxItem()
    .setTitle('Área de atuação')
    .setChoiceValues(['Música', 'Audiovisual', 'Artes visuais', 'Dança', 'Teatro', 'Literatura', 'Artesanato', 'Produção cultural'])
    .showOtherOption(true)
    .setRequired(true);

  form.addTextItem()
    .setTitle('Especialidades (ex.: DJ, Fotógrafo, MC, Grafiteiro, Produtor musical...)')
    .setHelpText('Separe por vírgula se tiver mais de uma. Ex.: DJ, Produção musical')
    .setRequired(false);

  form.addParagraphTextItem().setTitle('Bio curta (até ~300 caracteres)').setRequired(false);

  form.addTextItem().setTitle('Há quantos anos atua?').setRequired(false);

  // ---------- Seção 3 — Trajetória e portfólio ----------
  form.addPageBreakItem().setTitle('Trajetória e portfólio');

  form.addParagraphTextItem().setTitle('Conte sua trajetória').setRequired(false);
  form.addParagraphTextItem().setTitle('Projetos realizados (um por linha)').setRequired(false);
  form.addParagraphTextItem().setTitle('Premiações (um por linha)').setRequired(false);
  form.addParagraphTextItem().setTitle('Participação em editais/projetos culturais (um por linha)').setRequired(false);
  form.addParagraphTextItem().setTitle('Link(s) de portfólio (um por linha)').setRequired(false);
  form.addTextItem().setTitle('Instagram (usuário, sem @)').setRequired(false);
  form.addTextItem().setTitle('YouTube (link do canal)').setRequired(false);
  form.addTextItem().setTitle('Spotify (link do perfil/artista)').setRequired(false);
  form.addParagraphTextItem().setTitle('Outros links relevantes (um por linha)').setRequired(false);

  // ---------- Seção 4 — Contato ----------
  form.addPageBreakItem().setTitle('Contato');

  form.addSectionHeaderItem()
    .setTitle('Preencha pelo menos um destes dois — ou use o Instagram já informado antes.')
    .setHelpText('É assim que o produtor vai te encontrar. Sem nenhum contato, o cadastro não pode ser publicado.');

  form.addTextItem().setTitle('WhatsApp profissional (com DDD)').setRequired(false);
  form.addTextItem().setTitle('E-mail profissional').setRequired(false);

  // ---------- Seção 5 — Consentimento (LGPD) ----------
  form.addPageBreakItem().setTitle('Consentimento');

  const textoConsentimento =
    'Autorizo a publicação pública, no site CONTRATE A ARTE, dos dados de contato que ' +
    'enviei neste formulário (WhatsApp, e-mail e/ou Instagram, conforme o que eu preenchi), ' +
    'assim como das demais informações de perfil, foto e portfólio aqui fornecidas. Entendo que:\n' +
    '- a publicação depende de revisão e aprovação prévia pela equipe do coletivo;\n' +
    '- posso pedir correção ou remoção do meu perfil a qualquer momento, escrevendo para ' +
    'batalhawb2.0@gmail.com;\n' +
    '- meus dados de cadastro (mesmo os não publicados) ficam guardados na planilha de ' +
    'administração do coletivo, usada só para gerenciar este diretório.';

  form.addCheckboxItem()
    .setTitle('Consentimento de publicação')
    .setHelpText(textoConsentimento)
    .setChoiceValues(['Li e autorizo, conforme descrito acima.'])
    .setRequired(true);

  // ---------- Linka a uma planilha nova (planilha de administração) ----------
  const planilha = SpreadsheetApp.create('CONTRATE A ARTE — Cadastros (planilha de administração)');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, planilha.getId());

  Logger.log('Formulário criado: ' + form.getPublishedUrl());
  Logger.log('Link de edição: ' + form.getEditUrl());
  Logger.log('Planilha de respostas: ' + planilha.getUrl());

  return {
    formularioPublico: form.getPublishedUrl(),
    formularioEdicao: form.getEditUrl(),
    planilha: planilha.getUrl(),
  };
}
