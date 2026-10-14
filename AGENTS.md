# Orientações para agentes

## Contexto do projeto

Este é o repositório do perfil de Marcus Vinícius (`V1nic1us`) no GitHub e no GitLab. O produto principal é o `README.md`, acompanhado de SVGs gerados e automações de atualização. Não há aplicação web, servidor, banco de dados ou processo de build.

O perfil está em português brasileiro. Marcus é desenvolvedor front-end e mobile e já atuou como QA. Seus interesses incluem Linux, games, livros, IoT e Raspberry Pi. Preserve esses dados e não invente cargos, tecnologias dominadas, títulos de livros, autores ou edições.

## Mapa do repositório

- `README.md`: apresentação pública, tecnologias, leituras, gráficos, contador e cobrinha.
- `scripts/update_languages.py`: consultas REST/GraphQL, coleta dos calendários e geração dos dois painéis.
- `scripts/profile_charts.py`: SVGs com calendário 3D, rosca de linguagens e radar semanal.
- `scripts/update_visitors.py`: badge de visitantes únicos do repositório GitHub.
- `assets/`: SVGs gerados e versionados, referenciados pelo README.
- `tests/`: testes com `unittest`, sem acesso à rede ou credenciais reais.
- `.github/workflows/update-languages.yml`: gráficos e visitantes, a cada 12 horas (`17 */12 * * *`, UTC).
- `.github/workflows/main.yml`: cobrinha, a cada 12 horas (`0 */12 * * *`, UTC), publicada no branch `output` do GitHub.
- `.gitlab-ci.yml`: atualização dos gráficos por agendamento/manual e detecção de segredos.
- `docs/profile-automation.md`: configuração, credenciais, fontes e significado das métricas.

## Ambiente e comandos

Use Python 3.10 ou superior. Os scripts e testes usam apenas a biblioteca padrão; não introduza dependências sem necessidade. O CI usa Python 3.12. Execute os comandos a partir da raiz.

Validação de código Python:

```sh
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/update_languages.py scripts/profile_charts.py scripts/update_visitors.py
git diff --check
```

Geração real dos arquivos, quando necessária e com credenciais no ambiente:

```sh
python3 scripts/update_languages.py
python3 scripts/update_visitors.py
```

Gerar os gráficos consulta as APIs e altera os SVGs, incluindo seus horários de atualização. Não execute a coleta real apenas para validar mudanças de texto ou documentação. Os testes não precisam de tokens. Para mudanças de lógica, acrescente testes de comportamento e execute a suíte completa. Para mudanças somente no README, confira o conteúdo, os links e `git diff --check`.

## Regras das métricas

- Linguagens: apenas repositórios públicos próprios, sem forks, com linguagens detectadas; arquivados também entram.
- GitHub: percentuais calculados pela soma dos bytes de código por linguagem.
- GitLab: média dos percentuais dos projetos, com peso igual para cada projeto elegível. Consulte detalhes do projeto para identificar forks; a listagem pública pode omitir esse campo.
- Os rankings são independentes. Não some as métricas nem deduplique espelhos sem definir outra metodologia com o usuário.
- Mostre seis linguagens e agrupe as demais em “Outras”. Dados vazios devem aparecer como ausência de dados, sem valores fictícios.
- Calendários: janela de 365 dias em UTC; datas ausentes recebem zero. Os blocos representam a atividade diária; o radar soma por dia da semana.
- O GitHub usa GraphQL autenticado. O GitLab usa o calendário público `/users/<usuário>/calendar.json`, que não é uma API REST versionada.
- Complete as consultas das duas plataformas antes de substituir os painéis. Falhas de API devem preservar os últimos SVGs válidos, sem publicar zeros como se fossem dados reais.
- Visitantes: use `uniques` da API oficial de tráfego do repositório GitHub, na janela móvel de 14 dias. Não use `count`, não some leituras sucessivas e não apresente esse número como visitas ao perfil inteiro ou total histórico. Recarregar o SVG não deve incrementar um contador.

## Credenciais e CI

- `GH_TOKEN` ou `GITHUB_TOKEN`: necessário para o calendário GraphQL. O coletor dá preferência a `GH_TOKEN`.
- `GITLAB_TOKEN`: opcional para consultar linguagens de projetos públicos; o calendário público é consultado sem autenticação.
- `PROFILE_TRAFFIC_TOKEN`: usado pelo CI para visitantes, com acesso ao repositório e permissão `Administration: read`. Localmente, o script também aceita `GH_TOKEN`/`GITHUB_TOKEN` com acesso adequado.
- O token temporário do GitHub Actions não fornece a permissão de tráfego. Sem `PROFILE_TRAFFIC_TOKEN`, o workflow mantém o badge anterior.
- Nunca grave tokens, `.env`, cabeçalhos de autenticação ou saídas de comandos que exponham credenciais no Git, nos SVGs ou nos logs.
- No GitLab, o agendamento é cadastrado na plataforma; o YAML sozinho não o cria. Push por `CI_JOB_TOKEN` depende da configuração do projeto e das permissões do responsável pelo agendamento.
- Preserve a detecção de segredos e os controles que evitam loops de commits no CI.

## Visual e arquivos gerados

Mantenha a identidade de terminal, com roxo e rosa, consistente entre painéis e cobrinha. A paleta dos painéis está em `scripts/profile_charts.py`; a da cobrinha está nos parâmetros `color_snake` e `color_dots` de `.github/workflows/main.yml`. São exatamente cinco cores para os quadradinhos da cobrinha, do nível zero ao maior nível.

Edite o gerador para mudanças permanentes nos SVGs e regenere os arquivos afetados. Preserve os nomes usados pelo README. Mantenha o escape de texto XML, os títulos, as descrições acessíveis e a identificação de cada plataforma. Confira mudanças visuais em um navegador com suporte a SVG; uma conversão por ImageMagick pode omitir os segmentos da rosca.

A cobrinha é independente dos gráficos 3D. Preserve o `<picture>` com versões clara/escura e os URLs do branch `output`. No GitLab, esses URLs também exibem a animação hospedada no GitHub.

## Git e publicação

Confira `git status`, remotos e diferenças antes de editar ou publicar. Preserve alterações do usuário e não inclua arquivos alheios à tarefa.

O remoto local `origin` aponta para o GitLab. O GitHub também possui `V1nic1us/V1nic1us`, mas os dois repositórios têm históricos distintos e não há espelhamento automático. Ao publicar nos dois, confira cada branch remoto e preserve seus históricos; não use force push para contornar divergências. Publicar no GitLab não atualiza a cobrinha no GitHub.

Faça commit e push quando solicitados. Ao concluir, informe quais arquivos mudaram, quais verificações foram executadas e se houve publicação ou apenas alterações locais. Não afirme que agendamentos, secrets ou workflows estão ativos sem verificá-los.

Atualize este arquivo e o guia de automação quando a estrutura, os comandos ou as regras das métricas mudarem.
