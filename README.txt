全套图与生成原图技能云端主版本

新电脑首次使用（Windows PowerShell，需要 Git）：
git -c http.sslBackend=openssl clone https://github.com/chiarachen86-ux/skills.git "$env:USERPROFILE\pet-design-skills"
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\pet-design-skills\sync.ps1"

每天使用前运行第二条命令，再在 Codex 新聊天中调用全套图。
同步前会备份本机旧技能到仓库的 .local-backups，不上传备份。
同步脚本安装全套图（replace-pet-air-freshener-suite）和生成原图（generate-pet-originals）。全套图已包含文件夹批量出图与品种选择图流程。生成原图包含圣诞款、花圈款及配色参考模板；通知邮箱使用会话中已授权的私人设置，不写入公开仓库。
全套图默认逐张保存和交付PNG，不生成成品压缩包。
修改后须提交并推送 GitHub，其他电脑再运行同步脚本。不要在两台电脑同时修改。
GitHub 登录只在本机完成，不要在聊天中发送密码或令牌。

Mac 首次使用（终端）：
git clone https://github.com/chiarachen86-ux/skills.git "$HOME/pet-design-skills"
bash "$HOME/pet-design-skills/sync.command"
每天使用前运行第二条命令。Git 未安装时，按 macOS 提示安装命令行开发工具。
Windows 与 Mac 使用同一仓库及相同技能内容，各自运行对应同步脚本。
