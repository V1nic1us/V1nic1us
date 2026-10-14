# Atualização dos gráficos e visitantes

O mesmo script gera os cards do GitHub e do GitLab. Cada plataforma atualiza os arquivos na sua própria cópia do repositório; publicar as alterações nas duas não configura espelhamento entre elas.

## Rodar localmente

Requer Python 3.10 ou superior, sem dependências externas. Antes de gerar os painéis, defina `GITHUB_TOKEN` ou `GH_TOKEN` no ambiente com acesso de leitura à API do GitHub. Os testes não precisam de credenciais:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/update_languages.py
```

`GITHUB_TOKEN` (ou `GH_TOKEN`) é obrigatório para o calendário GraphQL do GitHub. `GITLAB_TOKEN` é opcional para consultar as linguagens dos projetos públicos no GitLab. Nunca salve tokens no repositório. No CI do GitLab, configure `GITHUB_TOKEN` como variável mascarada; acesso de leitura a repositórios públicos é suficiente. O calendário público do GitLab é consultado sem token.

## GitHub: a cada 12 horas

1. Publique estes arquivos no branch `main` do repositório `V1nic1us/V1nic1us` no GitHub.
2. Na aba **Actions**, habilite workflows caso necessário. O arquivo `.github/workflows/update-languages.yml` usa o token temporário do próprio GitHub com `contents: write`.
3. Execute **Atualizar gráficos do perfil → Run workflow** para conferir a primeira execução. Opcionalmente cadastre `GITLAB_TOKEN` em Actions secrets se a API pública do GitLab atingir limites.

Cron: `17 */12 * * *` (00:17 e 12:17 UTC, ou 20:17 e 08:17 em Boa Vista). Execuções agendadas podem atrasar; o GitHub também pode desativá-las após 60 dias sem atividade em repositórios públicos. Proteções de branch devem permitir commits do workflow ou exigir uma estratégia por pull request.

Para atualizar diariamente, altere o cron para `17 0 * * *`.

## GitLab: a cada 12 horas

1. Publique os arquivos no branch padrão do projeto no GitLab.
2. Em **Settings → CI/CD → Variables**, configure `GITHUB_TOKEN` como variável mascarada para evitar o limite baixo das consultas anônimas. `GITLAB_TOKEN` é opcional para consultas públicas.
3. Em **Settings → CI/CD → Job token permissions**, habilite **Allow Git push requests to the repository**. O job usa o `CI_JOB_TOKEN` temporário de sua própria pipeline para gravar os cards. O responsável pelo agendamento precisa ter permissão de push no branch padrão.
4. Em **Build → Pipeline schedules**, crie um agendamento para o branch padrão, cron `17 */12 * * *`, fuso UTC. Para 24 horas, use `17 0 * * *`.
5. Execute o agendamento manualmente para conferir o primeiro resultado.

O cron do GitLab é cadastrado na plataforma: o `.gitlab-ci.yml` sozinho não cria o agendamento. O job também fica disponível como ação manual em pipelines iniciadas pela interface. A detecção de segredos existente foi preservada.

## Como os números são calculados

- Só entram repositórios públicos pertencentes ao usuário, sem forks, com linguagens detectadas. Repositórios arquivados também entram.
- GitHub: soma dos bytes por linguagem em todos os repositórios elegíveis, dividida pelo total de bytes.
- GitLab: cada projeto tem peso igual; seus percentuais são somados e normalizados. Projetos sem linguagens são ignorados.
- Os cards mostram seis linguagens e agrupam as restantes em “Outras”. A soma pode variar levemente por arredondamento.
- São rankings independentes: um projeto espelhado nas duas plataformas aparece em ambos. A coleta não mede tempo de programação ou experiência.
- Se qualquer API falhar, a execução termina com erro antes de substituir os cards. O último resultado válido continua no perfil.

Documentação: [API GitHub](https://docs.github.com/en/rest/repos/repos#list-repository-languages), [API GitLab](https://docs.gitlab.com/api/projects/#get-project-languages), [agendamentos GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule), [agendamentos GitLab](https://docs.gitlab.com/ci/pipelines/schedules/), [push com job token](https://docs.gitlab.com/ci/jobs/ci_job_token/#allow-git-push-requests-to-your-project-repository).

## Painéis 3D

Os SVGs reúnem calendário isométrico dos últimos 365 dias, gráfico de rosca de linguagens e radar de atividade por dia da semana. A altura dos blocos usa escala de raiz quadrada para manter visíveis dias com menos atividade. As cores e alturas são relativas ao pico de cada plataforma, não comparáveis entre painéis.

O calendário do GitHub usa GraphQL `contributionsCollection` e precisa de `GITHUB_TOKEN` ou `GH_TOKEN`, inclusive localmente. Os totais seguem as contribuições visíveis ao token; podem incluir contagens privadas agregadas conforme as permissões e configurações do perfil, sem exibir nomes ou conteúdo de projetos privados.

O calendário do GitLab é consultado sem autenticação no endpoint público do perfil `/users/V1nic1us/calendar.json`. Ele corresponde à atividade exibida publicamente pelo GitLab e não é uma API REST versionada; mudanças nesse endpoint fazem a execução falhar, preservando os últimos cards. Datas ausentes são preenchidas com zero dentro da janela de 365 dias em UTC.

As plataformas definem contribuições de formas diferentes. Os calendários não somam nem deduplicam atividade entre elas. A rosca mantém as métricas de linguagens descritas acima, independentes da atividade do calendário.

Referência visual: [painel enviado](https://raw.githubusercontent.com/Ahtisham-1214/Ahtisham-1214/output-3d-contrib/profile-green-dual.svg). O SVG é gerado localmente pelo nosso script com os dados de V1nic1us.

Fonte do endpoint de calendário do GitLab: [UsersController](https://gitlab.com/gitlab-org/gitlab/-/blob/master/app/controllers/users_controller.rb).

## Visitantes sem contador de recarregamentos

O badge `assets/visitors.svg` exibe diretamente `uniques` da API oficial de tráfego de `V1nic1us/V1nic1us`, no GitHub, para a janela móvel dos últimos 14 dias. É tráfego do repositório, não uma medição de todas as visitas à página do perfil; a mesma imagem no GitLab continua mostrando a métrica do repositório GitHub. O número pode diminuir ao sair da janela, e não reaproveita o histórico do antigo Komarev.

O SVG é estático: abrir ou recarregar o perfil não executa um incremento. A deduplicação dos visitantes do repositório é a fornecida pelo GitHub; não há tentativa de identificar pessoas por IP ou cookies, nem garantia de uma pessoa única para sempre em todos os dispositivos.

Para a atualização automática, cadastre **PROFILE_TRAFFIC_TOKEN** como secret do GitHub Actions e/ou variável mascarada do GitLab. Use um token com acesso apenas a este repositório e permissão **Administration: read**, exigida pelo endpoint de tráfego. O `GITHUB_TOKEN` temporário do workflow não oferece essa permissão. Sem o secret, a automação mantém a última leitura; o horário da coleta está no texto descritivo do SVG.

Localmente, com `PROFILE_TRAFFIC_TOKEN` ou `GH_TOKEN`/`GITHUB_TOKEN` adequado no ambiente:

```sh
python3 scripts/update_visitors.py
```

Fonte: [API oficial de tráfego](https://docs.github.com/en/rest/metrics/traffic#get-page-views). O contador antigo do Komarev mede acessos à imagem e não garante visitantes únicos no README.

## Cobrinha de contribuições

O workflow original do GitHub, `.github/workflows/main.yml`, foi preservado nesta cópia, com permissão explícita `contents: write` para publicar as imagens no branch `output`. Ele continua agendado a cada 12 horas e também roda em pushes no `main` ou manualmente.

A seção da cobrinha no README usa os SVGs claro/escuro desse branch. O calendário 3D e a cobrinha coexistem, em workflows separados. No GitLab, o README exibe a mesma animação hospedada no GitHub.

A cobrinha usa rosa, com quadradinhos em tons de roxo e rosa alinhados aos painéis 3D. O SVG claro usa fundo das células em lavanda; o escuro e o GIF usam a paleta escura do painel. A mudança aparece depois de publicar o workflow e executar novamente a geração da cobrinha.
