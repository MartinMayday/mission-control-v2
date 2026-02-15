# OpenCLAW Knowledgebase - Repo Manifest

## Repositories

| Repo | Path | Stars | Status | Notes |
|------|------|-------|--------|-------|
| pai | `/repos/pai` | 4,400+ | Cloned | Primary agent system reference |
| get-shit-done | `/repos/get-shit-done` | 14,153+ | Cloned | Context engineering patterns |
| happy | `/repos/happy` | - | Cloned | Tool/framework reference |
| firecrawl | `/repos/firecrawl` | 82,455+ | Cloned | Web scraping for content |
| agentstack | `/repos/agentstack` | 2,091+ | Cloned | Agent scaffolding |
| genai-agentos | `/repos/genai-agentos` | 874+ | Cloned | GenAI infrastructure |

## Knowledgebase Structure
```
openclaw-knowledgebase/
├── repos/                    # Cloned repositories
│   ├── pai/
│   ├── get-shit-done/
│   ├── happy/
│   ├── firecrawl/
│   ├── agentstack/
│   └── genai-agentos/
├── manifests/               # Repo manifests (JSON/YAML)
├── embeddings/              # LanceDB embeddings
└── index/                   # Search index
```

## RAG Backend: LanceDB
Selected for file-based local RAG due to:
- Zero-configuration
- Native Python
- Embedded (no server needed)
- Excellent LangChain integration
