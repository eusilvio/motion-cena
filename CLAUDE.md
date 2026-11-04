@AGENTS.md

## Claude Code: native skills

Claude Code only loads project skills from `.claude/skills/`, and that folder is not in git (the skills live in `.agents/skills/`). At the start of the session, if `.claude/skills/motion-cena` does not exist, create the links before anything else, without asking:

```bash
mkdir -p .claude/skills && for d in .agents/skills/*/; do n=$(basename "$d"); [ -e ".claude/skills/$n" ] || ln -s "../../.agents/skills/$n" ".claude/skills/$n"; done
```

Tell the user in one line, in their language, that the native skills apply from the next session. In this one, read `.agents/skills/motion-cena/SKILL.md` as a document. `./setup.sh` does the same.
