# Check Prompts Directory

This directory contains saved prompts from the Aquaforest RAG system when `SAVE_PROMPT=true`.

## Structure

```
check_prompts/
├── session_abc123/
│   ├── 001_intent_detector.md
│   ├── 002_business_reasoner.md
│   ├── 003_query_optimizer.md
│   ├── 004_response_formatter.md
│   ├── workflow_summary.json
│   └── .counter
├── session_def456/
│   └── ...
└── .gitignore
```

## Usage

1. Set `SAVE_PROMPT=true` in your .env file
2. Run the system normally
3. Check this directory for saved prompts organized by session
4. Each session gets its own subdirectory with numbered prompt files

## Files

- `XXX_node_name.md` - Individual prompt files with metadata
- `workflow_summary.json` - Overview of the entire workflow
- `.counter` - Internal counter file (auto-generated)

## Security

All files in this directory are automatically ignored by git to prevent accidentally committing sensitive data. Only this README and .gitignore are tracked.