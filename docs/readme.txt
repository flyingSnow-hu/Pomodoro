一个会长番茄的番茄钟

====================
打包流程说明
====================

Windows 打包流程
1. 打开 PowerShell，进入项目根目录。
2. 创建并激活虚拟环境（如已创建可跳过创建步骤）。
	python -m venv .venv
	.\.venv\Scripts\Activate.ps1
3. 安装依赖。
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt
4. 若上次打包后的程序还在运行，先关闭托盘程序，避免 dist\PomodoroPy\PomodoroPy.exe 被占用。
5. 在项目根目录执行打包脚本。
	python build.py
6. 打包完成后检查产物目录。
	dist\PomodoroPy\PomodoroPy.exe
	dist\PomodoroPy\_internal\
7. 分发时请发送整个 dist\PomodoroPy 文件夹，不要只发 exe。

macOS 打包流程
1. 必须在 macOS 机器上打包（不能在 Windows 上直接产出可运行的 macOS 程序）。
2. 打开 Terminal，进入项目根目录。
3. 创建并激活虚拟环境（如已创建可跳过创建步骤）。
	python3 -m venv .venv
	source .venv/bin/activate
4. 安装依赖。
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt
5. 执行打包脚本。
	python build.py
6. 打包完成后检查产物目录（名称与 Windows 一致）。
	dist/PomodoroPy/
7. 建议分发前在一台干净的 macOS 环境中验证：
	- 托盘图标是否正常显示
	- 设置窗口是否可打开
	- 计时、提示音、番茄累积是否正常

常见问题
1. 报 PermissionError: [WinError 5] 拒绝访问
	原因通常是旧的 PomodoroPy.exe 仍在运行并占用文件。
	处理：退出托盘程序后再打包，必要时手动结束进程并删除 dist、build 目录后重试。
2. Windows 下命令 tail 不可用
	可改用 PowerShell 命令查看最后输出：
	Get-Content .\build.log -Tail 50