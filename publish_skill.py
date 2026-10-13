#!/usr/bin/env python3
"""
publish_skill.py - 一键发布 WorkBuddy skill 到 GitHub 并打包

完整流程：
  1. 验证 skill 结构（通过 package_skill.py）
  2. 生成 zip 分发包
  3. 生成丰富 README（含 SVG 视觉资产，如果缺失）
  4. 创建/复用 GitHub 仓库
  5. 提交并推送
  6. 输出 WorkBuddy 技能市场上传指引

用法:
    python publish_skill.py <skill_dir> [选项]

必填:
    skill_dir                 skill 源目录路径（含 SKILL.md）

可选:
    --repo NAME               GitHub 仓库名（默认 = skill 目录名）
    --visibility public|private  仓库可见性（默认 public）
    --no-push                 只打包不推送
    --message "commit msg"    自定义 commit message
    --user NAME               Git 用户名（默认读 gh CLI 当前账号）
    --email EMAIL             Git 邮箱（默认用 noreply 邮箱）

示例:
    python publish_skill.py ~/.workbuddy/skills/topic-idea-generator
    python publish_skill.py ./my-skill --repo my-cool-skill --visibility private
    python publish_skill.py ./my-skill --no-push
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import dedent


# ---------- 工具函数 ----------

def run(cmd, cwd=None, check=True, capture=True):
    """Run a shell command and return (returncode, stdout)."""
    result = subprocess.run(
        cmd, shell=True, cwd=cwd, capture_output=capture, text=True
    )
    if check and result.returncode != 0:
        print(f"\n[FAIL] 命令失败: {cmd}")
        if result.stderr:
            print(result.stderr)
        sys.exit(1)
    return result.returncode, (result.stdout or "").strip()


def info(msg):
    print(f"\n[INFO] {msg}")


def ok(msg):
    print(f"[OK]   {msg}")


# ---------- Step 1: 验证并打包 ----------

def package_skill(skill_dir: Path, output_dir: Path) -> Path:
    """调用 skill-creator 的 package_skill.py 验证并打包。"""
    info(f"校验并打包: {skill_dir.name}")
    script = Path.home() / ".workbuddy" / "plugins" / "cache" / "workbuddy-builtin" / "skill-skill-creator" / "0.1.0" / "scripts" / "package_skill.py"
    if not script.exists():
        print(f"[FAIL] 找不到 package_skill.py: {script}")
        sys.exit(1)

    run(f'python "{script}" "{skill_dir}" "{output_dir}"')
    zip_path = output_dir / f"{skill_dir.name}.zip"
    if not zip_path.exists():
        print(f"[FAIL] 打包失败: {zip_path} 不存在")
        sys.exit(1)
    ok(f"已生成: {zip_path}")
    return zip_path


# ---------- Step 2: 生成丰富 README ----------

WORKFLOW_SVG = """<svg width="100%" viewBox="0 0 680 280" xmlns="http://www.w3.org/2000/svg" role="img">
  <title>workflow</title>
  <desc>Skill 工作流示意图</desc>
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="#5F5E5A" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>
  <g class="node c-blue">
    <rect x="40" y="100" width="160" height="56" rx="8" fill="#E6F1FB" stroke="#185FA5" stroke-width="0.5"/>
    <text x="120" y="128" text-anchor="middle" fill="#042C53" font-size="13" font-weight="500">输入</text>
    <text x="120" y="146" text-anchor="middle" fill="#185FA5" font-size="11">用户参数</text>
  </g>
  <g class="node c-purple">
    <rect x="260" y="100" width="160" height="56" rx="8" fill="#EEEDFE" stroke="#534AB7" stroke-width="0.5"/>
    <text x="340" y="128" text-anchor="middle" fill="#26215C" font-size="13" font-weight="500">处理</text>
    <text x="340" y="146" text-anchor="middle" fill="#534AB7" font-size="11">skill 核心逻辑</text>
  </g>
  <g class="node c-teal">
    <rect x="480" y="100" width="160" height="56" rx="8" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.5"/>
    <text x="560" y="128" text-anchor="middle" fill="#04342C" font-size="13" font-weight="500">输出</text>
    <text x="560" y="146" text-anchor="middle" fill="#0F6E56" font-size="11">结构化结果</text>
  </g>
  <path d="M200 128 L260 128" fill="none" stroke="#5F5E5A" stroke-width="1.5" marker-end="url(#arrow)"/>
  <path d="M420 128 L480 128" fill="none" stroke="#5F5E5A" stroke-width="1.5" marker-end="url(#arrow)"/>
</svg>
"""


def generate_readme(skill_dir: Path, zip_path: Path):
    """如果仓库目录里没有 README.md，就生成一个含 SVG 的丰富版本。"""
    readme = skill_dir / "README.md"
    if readme.exists():
        ok(f"README.md 已存在，跳过生成")
        return

    info(f"生成 README.md（含 SVG 工作流图）")
    skill_md = skill_dir / "SKILL.md"
    description = ""
    name = skill_dir.name
    if skill_md.exists():
        text = skill_md.read_text(encoding="utf-8")
        m = re.search(r"^description:\s*(.+)$", text, re.M)
        if m:
            description = m.group(1).strip()
        m = re.search(r"^name:\s*(.+)$", text, re.M)
        if m:
            name = m.group(1).strip()

    workflow_svg = skill_dir / "assets" / "workflow.svg"
    if not workflow_svg.exists():
        (skill_dir / "assets").mkdir(parents=True, exist_ok=True)
        (workflow_svg).write_text(WORKFLOW_SVG, encoding="utf-8")

    readme.write_text(dedent(f"""\
        # {name}

        > {description}

        ## 工作流

        ![workflow](./assets/workflow.svg)

        ## 快速开始

        ### 安装

        下载 [`{name}.zip`](./{name}.zip)（已通过 WorkBuddy 官方校验器）。

        在 WorkBuddy 中导入：

        ```
        设置 → 技能管理 → 导入本地 Skill → 选择 zip
        ```

        ## 文件结构

        ```
        {name}/
        ├── SKILL.md
        ├── references/
        ├── assets/
        └── {name}.zip
        ```

        ## License

        MIT
        """), encoding="utf-8")
    ok(f"已生成: {readme}")


# ---------- Step 3: Git + GitHub ----------

def get_gh_user() -> str:
    """从 gh CLI 当前账号读用户名。"""
    _, out = run("gh api user --jq .login")
    return out


def ensure_repo(repo_name: str, visibility: str) -> bool:
    """检查仓库是否存在；不存在就创建。返回 True 表示复用已存在的。"""
    code, _ = run(f"gh repo view {repo_name} --json name >/dev/null 2>&1", check=False)
    if code == 0:
        ok(f"GitHub 仓库已存在: {repo_name}")
        return True
    info(f"创建 GitHub 仓库: {repo_name} ({visibility})")
    run(f'gh repo create {repo_name} --{visibility} --description "WorkBuddy skill"')
    return False


def ensure_git_repo(work_dir: Path, repo_name: str, user: str, email: str, message: str):
    """在工作目录里初始化 git、提交并推送。"""
    info("配置 git 身份")
    run(f'git -c user.name="{user}" -c user.email="{email}" config user.name "{user}"', cwd=work_dir)
    run(f'git -c user.name="{user}" -c user.email="{email}" config user.email "{email}"', cwd=work_dir)

    if not (work_dir / ".git").exists():
        info("初始化 git 仓库")
        run("git init", cwd=work_dir)
        run("git branch -M main", cwd=work_dir)
        run("git remote add origin https://github.com/{user}/{repo_name}.git".format(user=user, repo_name=repo_name), cwd=work_dir)

    info("暂存文件")
    run("git add .", cwd=work_dir)

    info("提交")
    run(f'git commit -m "{message}"', cwd=work_dir, check=False)

    info("推送到 main 分支")
    run("git push -u origin main --force", cwd=work_dir, check=False)
    ok(f"已推送到 https://github.com/{user}/{repo_name}")


# ---------- Step 4: WorkBuddy 市场指引 ----------

def print_market_instructions(skill_dir: Path, zip_path: Path):
    """打印 WorkBuddy 技能市场手动上传步骤。"""
    print(dedent(f"""

        ====================================================================
          WorkBuddy 技能市场上传指引（手动操作）
        ====================================================================

        WorkBuddy 技能市场没有公开 CLI 上传路径，需要在客户端操作：

        1. 打开 WorkBuddy 客户端
        2. 左侧导航栏 → "专家" 或顶部 "+ 新建"
        3. 找到 "导入本地 Skill" 或 "从 ZIP 安装"
        4. 选择文件: {zip_path}
        5. 等校验通过
        6. 填写信息:
             名称: {skill_dir.name}
             分类: 内容创作
             标签: (按 skill 领域填)
             描述: 从 GitHub README 取前两段
        7. 打开 "发布为公开" 开关
        8. 点确认

        仓库地址: https://github.com/{get_gh_user()}/{skill_dir.name}
        ====================================================================
        """))


# ---------- 主流程 ----------

def main():
    parser = argparse.ArgumentParser(
        description="一键发布 WorkBuddy skill 到 GitHub 并打包",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("skill_dir", help="skill 源目录路径（含 SKILL.md）")
    parser.add_argument("--repo", help="GitHub 仓库名（默认 = skill 目录名）")
    parser.add_argument("--visibility", choices=["public", "private"], default="public")
    parser.add_argument("--no-push", action="store_true", help="只打包不推送")
    parser.add_argument("--message", help="自定义 commit message")
    parser.add_argument("--user", help="Git 用户名（默认读 gh 当前账号）")
    parser.add_argument("--email", help="Git 邮箱")

    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).expanduser().resolve()
    if not skill_dir.exists():
        print(f"[FAIL] skill 目录不存在: {skill_dir}")
        sys.exit(1)
    if not (skill_dir / "SKILL.md").exists():
        print(f"[FAIL] 目录里没有 SKILL.md: {skill_dir}")
        sys.exit(1)

    repo_name = args.repo or skill_dir.name
    user = args.user or get_gh_user()
    email = args.email or f"{user}@users.noreply.github.com"
    message = args.message or f"Release {skill_dir.name}"

    print(f"\n{'=' * 70}")
    print(f"  发布 skill: {skill_dir.name}")
    print(f"  仓库: {user}/{repo_name} ({args.visibility})")
    print(f"{'=' * 70}\n")

    # Step 1: 打包
    output_dir = skill_dir.parent
    zip_path = package_skill(skill_dir, output_dir)

    # Step 2: README
    generate_readme(skill_dir, zip_path)

    if args.no_push:
        ok(f"已跳过推送（--no-push）。本地 zip: {zip_path}")
        return

    # Step 3: GitHub 仓库
    ensure_repo(repo_name, args.visibility)

    # Step 4: 推送到一个新工作目录（避免与 skill_dir 互相干扰）
    work_dir = Path.home() / ".workbuddy" / "tmp" / repo_name
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)

    info(f"复制 skill 到临时工作目录: {work_dir}")
    for item in skill_dir.iterdir():
        if item.name == "scripts" and item.is_dir():
            continue
        target = work_dir / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)
    shutil.copy2(zip_path, work_dir / zip_path.name)

    ensure_git_repo(work_dir, repo_name, user, email, message)

    # Step 5: 打印市场指引
    print_market_instructions(skill_dir, zip_path)


if __name__ == "__main__":
    main()
