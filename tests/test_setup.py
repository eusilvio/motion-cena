"""setup.sh and setup.ps1 in a throwaway copy of the repo skeleton: they create the local files,
link for Claude Code only the skills in .agents/skills/claude-links.txt, remove the links they made
to skills that left the list, and never overwrite what exists. setup.ps1 runs where pwsh is
installed (GitHub's ubuntu-latest has it; the Windows job in CI covers Windows PowerShell 5.1)."""
import os
import shutil
import stat
import subprocess

import pytest

from conftest import REPO

RUNNERS = {
    "setup.sh": ["bash"],
    "setup.ps1": ["pwsh", "-NoProfile", "-NonInteractive", "-File"],
}
LIST = REPO / ".agents/skills/claude-links.txt"


def listed(path=LIST):
    lines = (line.split("#", 1)[0].strip() for line in path.read_text(encoding="utf-8").splitlines())
    return [name for name in lines if name]


LINKED = listed()
UNLISTED = ("slideshow", "figma", "general-video")  # HyperFrames skills the pipeline reads as documents


@pytest.fixture(params=sorted(RUNNERS))
def skeleton(request, tmp_path):
    name = request.param
    if not (REPO / name).exists():
        pytest.skip(f"{name} não existe")
    if not shutil.which(RUNNERS[name][0]):
        pytest.skip(f"{RUNNERS[name][0]} não está no PATH")
    root = tmp_path / "repo"
    for skill in (*LINKED, *UNLISTED):
        (root / ".agents/skills" / skill).mkdir(parents=True)
        (root / ".agents/skills" / skill / "SKILL.md").write_text(f"# {skill}\n", encoding="utf-8")
    shutil.copyfile(LIST, root / ".agents/skills/claude-links.txt")
    (root / ".agents/skills/motion-cena/assets").mkdir()
    (root / ".agents/skills/motion-cena/assets/registro.template.md").write_text("# Registro\n", encoding="utf-8")
    (root / ".env.example").write_text("ELEVENLABS_API_KEY=\n", encoding="utf-8")
    shutil.copyfile(REPO / name, root / name)  # byte for byte: setup.ps1 keeps its BOM
    return root, name


def run(root, name):
    proc = subprocess.run([*RUNNERS[name], str(root / name)], capture_output=True, text=True, encoding="utf-8",
                          cwd=root.parent, timeout=120)  # from another folder: the script must find its own root
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return proc.stdout


def test_setup_creates_local_files_and_links(skeleton):
    root, name = skeleton
    out = run(root, name)
    env = root / ".env.local"
    assert env.read_text(encoding="utf-8") == "ELEVENLABS_API_KEY=\n"
    if os.name != "nt":
        assert stat.S_IMODE(env.stat().st_mode) == 0o600
    assert (root / "creatives/registro.md").read_text(encoding="utf-8") == "# Registro\n"
    for d in ("projects", "creatives/reels", "creatives/carrossel", "creatives/post", "training/voz", "training/referencias"):
        assert (root / d).is_dir(), d
    for skill in LINKED:
        link = root / ".claude/skills" / skill
        assert (link / "SKILL.md").read_text(encoding="utf-8") == f"# {skill}\n"
        if os.name != "nt":
            assert os.readlink(link) == f"../../.agents/skills/{skill}"  # relative: survives moving the repo
    assert sorted(os.listdir(root / ".claude/skills")) == sorted(LINKED)  # the others are not loaded
    assert "criado  .env.local" in out and f"{len(LINKED)} criado(s)" in out


def test_setup_is_idempotent_and_drops_dangling_links(skeleton):
    root, name = skeleton
    run(root, name)
    env = root / ".env.local"
    env.write_text("ELEVENLABS_API_KEY=minha-chave\n", encoding="utf-8")
    if os.name != "nt":
        os.symlink("../../.agents/skills/sumiu", root / ".claude/skills/sumiu")
    out = run(root, name)
    assert env.read_text(encoding="utf-8") == "ELEVENLABS_API_KEY=minha-chave\n"
    assert "mantido .env.local" in out and "0 criado(s)" in out
    assert not os.path.lexists(root / ".claude/skills/sumiu")
    assert (root / ".claude/skills/motion-cena/SKILL.md").exists()


@pytest.mark.skipif(os.name == "nt", reason="symlinks need privileges on Windows (CI runs setup.ps1 there)")
def test_setup_removes_only_its_own_links_out_of_the_list(skeleton, tmp_path):
    """A clone from before the list has a link to every skill: the unlisted ones go, the skill folder
    stays. The user's own skill, a copy, links pointing elsewhere (even broken) are never touched."""
    root, name = skeleton
    skills = root / ".claude/skills"
    skills.mkdir(parents=True)
    os.symlink("../../.agents/skills/slideshow", skills / "slideshow")              # old layout: relative
    os.symlink(root / ".agents/skills/general-video", skills / "general-video")     # absolute, same place
    os.symlink("../../.agents/skills/motion-cena", skills / "motion-cena")          # listed: kept as is
    (skills / "minha-skill").mkdir()                                                # the user's own skill
    (skills / "minha-skill/SKILL.md").write_text("# minha\n", encoding="utf-8")
    shutil.copytree(root / ".agents/skills/figma", skills / "figma")                # copy fallback: real folder
    elsewhere = tmp_path / "outro-lugar"
    elsewhere.mkdir()
    os.symlink(elsewhere, skills / "externa")                                       # link to another place
    os.symlink(tmp_path / "sumiu-de-outro-lugar", skills / "externa-quebrada")      # broken, but not ours

    out = run(root, name)

    for gone in ("slideshow", "general-video"):
        assert not os.path.lexists(skills / gone), gone
        assert (root / ".agents/skills" / gone / "SKILL.md").exists(), "removing the link must keep the skill"
    assert "2 removido(s)" in out
    assert os.readlink(skills / "motion-cena") == "../../.agents/skills/motion-cena"
    assert (skills / "minha-skill/SKILL.md").read_text(encoding="utf-8") == "# minha\n"
    assert (skills / "figma/SKILL.md").exists() and not (skills / "figma").is_symlink()
    assert ".claude/skills/figma é uma cópia de skill fora da lista" in out
    assert os.readlink(skills / "externa") == str(elsewhere)
    assert os.path.lexists(skills / "externa-quebrada")
    assert f"{len(LINKED) - 1} criado(s)" in out


def test_setup_skips_a_listed_skill_that_does_not_exist(skeleton):
    root, name = skeleton
    with (root / ".agents/skills/claude-links.txt").open("a", encoding="utf-8") as f:
        f.write("  nao-existe   # comment after a name\n\n")
    out = run(root, name)
    assert "nao-existe está na lista, mas" in out
    assert not os.path.lexists(root / ".claude/skills/nao-existe")
    assert f"{len(LINKED)} criado(s)" in out


def test_claude_links_list_names_real_skills():
    """Every listed skill exists (an update of the HyperFrames skills may rename one); motion-cena first."""
    assert LINKED[0] == "motion-cena"
    assert len(LINKED) == len(set(LINKED))
    for name in LINKED:
        assert (REPO / ".agents/skills" / name / "SKILL.md").is_file(), name


def test_setup_ps1_keeps_its_utf8_bom():
    """Windows PowerShell 5.1 reads a script without BOM as ANSI and mangles the accents in its output."""
    ps1 = REPO / "setup.ps1"
    if not ps1.exists():
        pytest.skip("setup.ps1 não existe")
    raw = ps1.read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")
    raw.decode("utf-8")
