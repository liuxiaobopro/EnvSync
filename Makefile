.PHONY: help install build clean run

help:
	@echo "可用命令:"
	@echo "  make install    - 安装依赖"
	@echo "  make run        - 运行程序"
	@echo "  make build      - 打包成 exe"
	@echo "  make clean      - 清理构建文件"

install:
	uv sync

run:
	uv run main.py

build:
	@echo "安装 PyInstaller..."
	uv pip install pyinstaller
	@echo "开始打包..."
	uv run pyinstaller --onefile --windowed --name EnvSync --icon=NONE main.py
	@echo "打包完成！exe 文件位于 dist/ 目录"

clean:
	rm -rf build dist __pycache__ *.spec
	@echo "清理完成"

