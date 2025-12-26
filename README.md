# EnvSync / 环境同步器

Windows 环境变量实时刷新工具，修改环境变量后无需重启命令行窗口即可立即生效。

## 特性

- 🚀 **实时刷新**：修改环境变量后立即生效，无需重启命令行
- 🎯 **完整 CRUD**：支持新建、编辑、删除环境变量
- 📋 **分类管理**：分别管理用户变量和系统变量
- 🔧 **Path 编辑**：专门的 Path 变量编辑器，支持路径列表管理
- 💻 **原生体验**：仿 Windows 原生环境变量对话框界面

## 安装

使用 [uv](https://github.com/astral-sh/uv) 安装：

```bash
uv sync
```

或使用 Makefile：

```bash
make install
```

## 使用

### 运行程序

```bash
uv run main.py
```

或使用 Makefile：

```bash
make run
```

### 打包成 exe

使用 Makefile 打包：

```bash
make build
```

打包完成后，exe 文件位于 `dist/` 目录。

手动打包：

```bash
uv pip install pyinstaller
uv run pyinstaller --onefile --windowed --name EnvSync main.py
```

### 功能说明

1. **查看环境变量**
   - 用户变量：显示当前用户的环境变量
   - 系统变量：显示系统级环境变量

2. **新建环境变量**
   - 点击"新建"按钮
   - 输入变量名和变量值
   - 点击"确定"保存

3. **编辑环境变量**
   - 双击变量名或点击"编辑"按钮
   - 对于 Path 变量，会打开专门的路径编辑器
   - 修改后点击"确定"保存

4. **删除环境变量**
   - 选择要删除的变量
   - 点击"删除"按钮
   - 确认删除

5. **刷新环境变量**
   - 修改完成后，点击"确定并刷新"按钮
   - 环境变量会立即生效
   - 已打开的命令行窗口需要关闭后重新打开才能看到新的环境变量

### Path 变量编辑

Path 变量有专门的编辑器，支持：
- 新建路径
- 编辑路径
- 浏览文件夹
- 删除路径
- 上移/下移路径
- 编辑文本（批量编辑）

## 技术实现

- 使用 Windows Registry API 读写环境变量
- 通过 `WM_SETTINGCHANGE` 消息广播环境变量变更
- 使用 `SetEnvironmentVariable` API 更新当前进程环境变量

## 依赖

- Python 3.14+
- pywin32

## 许可证

MIT

