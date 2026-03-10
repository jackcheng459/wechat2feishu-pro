
import os
import shutil
from pathlib import Path

def install():
    print("🚀 开始安装 WeChat2Feishu-Pro 技能...")
    
    # 1. 获取当前项目的绝对路径
    project_root = Path(__file__).parent.absolute()
    python_exec = project_root / ".venv" / "bin" / "python"
    main_script = project_root / "main.py"
    
    if not python_exec.exists():
        print(f"❌ 错误：未找到虚拟环境。请先运行 bash setup.sh")
        return

    # 2. 读取技能模板
    skill_template_path = project_root / "skills" / "wechat2feishu-pro.md"
    if not skill_template_path.exists():
        print(f"❌ 错误：未找到技能定义文件")
        return
        
    skill_content = skill_template_path.read_text(encoding="utf-8")

    # 3. 动态替换路径
    # 将模板中的绝对路径占位符替换为当前电脑的实际路径
    # 注意：我们将模板中的硬编码路径替换为通用的逻辑
    updated_content = skill_content.replace(
        "/Users/zhanghanlin/Documents/VibeCoding2/wechat2feishu/.venv/bin/python",
        str(python_exec)
    ).replace(
        "/Users/zhanghanlin/Documents/VibeCoding2/wechat2feishu/main.py",
        str(main_script)
    )

    # 4. 确定 OpenClaw 技能目录
    openclaw_skill_dir = Path.home() / ".openclaw" / "skills"
    openclaw_skill_dir.mkdir(parents=True, exist_ok=True)
    
    target_path = openclaw_skill_dir / "wechat2feishu-pro.md"
    
    # 5. 写入并完成
    target_path.write_text(updated_content, encoding="utf-8")
    
    print(f"✅ 技能已成功安装至：{target_path}")
    print(f"💡 现在的路径已指向：{project_root}")
    print("👉 现在您可以尝试在飞书里给机器人发一个微信链接了！")

if __name__ == "__main__":
    install()
