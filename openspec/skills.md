# Skills opcionais para implementação

Consulta ao skills.sh e aos repositórios de origem em 2026-10-03 (BRT). Contagens aproximadas, sujeitas a mudança. São ferramentas opcionais para contribuidores, sem dependência obrigatória no projeto.

| Skill | Origem | Instalações no catálogo | Estrelas do repositório | Uso no Elosys |
| --- | --- | --- | --- | --- |
| [webapp-testing](https://www.skills.sh/anthropics/skills/webapp-testing) | [Anthropic](https://github.com/anthropics/skills) | 170 mil | 179,5 mil | Testar busca e tabelas com Playwright e banco sintético |
| [vercel-react-best-practices](https://www.skills.sh/vercel-labs/agent-skills/vercel-react-best-practices) | [Vercel](https://github.com/vercel-labs/agent-skills) | 768 mil | 31,9 mil | Revisar consultas, renderização e exportação no frontend |

Instalação opcional:

```bash
npx skills add anthropics/skills@webapp-testing
npx skills add vercel-labs/agent-skills@vercel-react-best-practices
```

O backend utilizará a skill TDD já disponível e testes reais de SQLite. A presença de uma skill não dispensa ler os guias da versão de Next.js instalada nem validar o resultado no projeto.
