# Orientações para Claude Code

Leia e siga o [AGENTS.md](AGENTS.md) na raiz antes de trabalhar neste projeto. Ele concentra as orientações compartilhadas sobre estrutura, métricas, estilo visual, credenciais, testes e publicação. Consulte também [docs/profile-automation.md](docs/profile-automation.md) ao alterar as automações.

## Contexto rápido

- Este repositório é o perfil de Marcus Vinícius (`V1nic1us`) no GitHub e no GitLab, com README em português brasileiro.
- O foco atual é desenvolvimento front-end e mobile; QA é experiência anterior.
- Há três componentes independentes: painéis SVG em Python, badge oficial de visitantes únicos do repositório e cobrinha gerada por GitHub Actions.
- Use Python 3.10 ou superior e a biblioteca padrão. Não há aplicação para iniciar, dependências de produção para instalar ou build de frontend.

## Verificação

Para mudanças de código, execute:

```sh
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/update_languages.py scripts/profile_charts.py scripts/update_visitors.py
git diff --check
```

Os testes funcionam sem rede e sem credenciais reais. A coleta real exige tokens e altera os assets; execute-a somente quando a tarefa precisar de atualização dos dados.

## Cuidados essenciais

- Preserve os SVGs anteriores quando uma consulta de API falhar.
- Não confunda visitantes únicos do repositório nos últimos 14 dias com visualizações totais do perfil.
- Preserve a cobrinha e suas versões clara/escura ao alterar o README ou os gráficos.
- Nunca imprima ou versione tokens. Use variáveis de ambiente e secrets do CI.
- Verifique o remoto antes de publicar: `origin` é GitLab; o GitHub tem histórico independente.
- Mantenha as regras compartilhadas no `AGENTS.md` para evitar orientações contraditórias entre agentes.
