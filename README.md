# Vagando

**Vagando** é um radar de oportunidades profissionais remotas, pensado primeiro para pessoas residentes no Brasil e também aberto a oportunidades elegíveis para profissionais da América Latina e de qualquer lugar do mundo.

## Categorias do radar

1. HR & Talent Acquisition
2. Learning & Development
3. Non-profit, Social Impact & Sustainability
4. Customer Experience & Operations
5. Project & Business Operations

A categoria de impacto inclui oportunidades ligadas a direitos humanos, desenvolvimento internacional, bem-estar e proteção animal, conservação da vida silvestre, meio ambiente, clima e sustentabilidade.

## Regra de elegibilidade geográfica

O radar prioriza vagas que indiquem explicitamente que aceitam candidatos no Brasil, na América Latina ou em qualquer lugar do mundo. Uma vaga marcada apenas como “remota” **não** é considerada elegível automaticamente.

A classificação automatizada é uma triagem inicial, não uma garantia. Antes de se candidatar, confira a publicação original, o país de contratação, as exigências de autorização de trabalho, fuso horário e modalidade contratual.

## Como publicar no GitHub

1. Crie um repositório **público** chamado `vagando` (ou mantenha `purpose-driven-careers-radar`, se preferir preservar o nome técnico anterior).
2. Descompacte este projeto e envie todos os arquivos para a raiz do repositório, mantendo a pasta `.github`.
3. No GitHub, abra **Settings → Pages** e selecione **GitHub Actions** como fonte de publicação.
4. Abra **Actions** e habilite os workflows, caso o GitHub solicite.
5. Execute manualmente o workflow **Atualização diária do Vagando** uma vez.
6. Quando a publicação terminar, o site estará disponível em `https://SEU-USUARIO.github.io/NOME-DO-REPOSITORIO/`.

## Visualizar localmente

É necessário Python 3.10 ou superior.

```bash
python -m http.server 8000
```

Acesse `http://localhost:8000`.

Para executar a coleta manualmente:

```bash
python scripts/coletar_vagas.py
```

## Fontes iniciais

- API pública de vagas remotas da Remotive
- API pública de vagas da Arbeitnow

Começamos com duas fontes para validar a coleta e a qualidade dos dados. Novas fontes — incluindo organizações de proteção animal, meio ambiente e terceiro setor — serão adicionadas depois de verificarmos seus métodos de acesso, campos de localização e termos de uso. Não faça scraping de sites que proíbam essa prática.

## Atualização automática

O GitHub Actions está programado para executar diariamente às 10h UTC (7h no horário de Brasília, UTC−3). O GitHub pode atrasar execuções agendadas em períodos de alta demanda; portanto, o horário não é garantido ao minuto.

## Estrutura dos dados

Cada oportunidade pode conter: cargo, organização, categoria, elegibilidade geográfica, localidade, fonte, link original, data de publicação, data de descoberta, modalidade contratual (quando disponível) e descrição resumida.

## Próximas melhorias

- [ ] Adicionar páginas de carreira de organizações selecionadas
- [ ] Incluir mais fontes de terceiro setor, desenvolvimento internacional e impacto
- [ ] Ampliar fontes de bem-estar animal, conservação e meio ambiente
- [ ] Melhorar a validação geográfica e criar revisão manual de casos ambíguos
- [ ] Adicionar filtros de senioridade e modalidade de contratação
- [ ] Criar testes e monitoramento de fontes indisponíveis

## Uso responsável

O Vagando direciona para as publicações originais e não é afiliado a empresas, organizações ou job boards listados. As vagas podem ser encerradas ou alteradas sem aviso.
