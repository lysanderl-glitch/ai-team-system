"""
HR知识库文件监控器
监控OBS HR目录，文件变化时自动同步到YAML配置
自动同步Claude Code记忆到.claude目录
"""

import time
import logging
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

# 配置 - 支持环境变量自定义，默认使用相对路径
import os
REPO_ROOT = Path(__file__).parent.parent
OBS_HR_PATH = Path(os.environ.get("OBS_HR_PATH", REPO_ROOT / "obs" / "01-team-knowledge" / "HR"))
OBS_MEMORY_PATH = Path(os.environ.get("OBS_MEMORY_PATH", REPO_ROOT / "obs" / "00-system" / "claude-code-memory"))
CONFIG_DIR = Path(__file__).parent / "config"
SYNC_SCRIPT = Path(__file__).parent / "hr_base.py"
CLAUDE_MEMORY_SYNC = REPO_ROOT / "scripts" / "sync-claude-memory.sh"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HRDirHandler(FileSystemEventHandler):
    """HR目录文件变化处理器"""

    def __init__(self):
        super().__init__()
        self.last_sync = {}
        self.cooldown = 2  # 秒内防抖

    def should_sync(self, path: str) -> bool:
        """检查是否应该同步（防抖）"""
        now = time.time()
        last = self.last_sync.get(path, 0)
        if now - last < self.cooldown:
            return False
        self.last_sync[path] = now
        return True

    def on_modified(self, event):
        """文件修改事件"""
        if event.is_directory:
            return

        path = Path(event.src_path)
        # 监控.md文件（personnel/ 和 positions/ 目录）
        if path.suffix == '.md' and ('personnel' in str(path) or 'positions' in str(path)):
            if self.should_sync(event.src_path):
                logger.info(f"检测到HR文件变化: {path.name}")
                self._do_hr_sync()

    def on_created(self, event):
        """文件创建事件"""
        if event.is_directory:
            return

        path = Path(event.src_path)
        if path.suffix == '.md' and 'personnel' in str(path):
            logger.info(f"检测到HR新文件: {path.name}")
            self._do_hr_sync()

    def on_deleted(self, event):
        """文件删除事件"""
        if event.is_directory:
            return

        path = Path(event.src_path)
        if path.suffix == '.md' and 'personnel' in str(path):
            logger.info(f"检测到HR文件删除: {path.name}")
            self._do_hr_sync()

    def _do_hr_sync(self):
        """执行HR同步"""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("hr_base", SYNC_SCRIPT)
            hr_base = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(hr_base)

            logger.info("开始同步HR...")
            results = hr_base.sync_all_teams()
            logger.info(f"HR同步完成: 成功 {len(results['synced'])}, 失败 {len(results['failed'])}")
        except Exception as e:
            logger.error(f"HR同步失败: {e}")


class ClaudeMemoryHandler(FileSystemEventHandler):
    """Claude Code记忆目录变化处理器"""

    def __init__(self):
        super().__init__()
        self.last_sync = {}
        self.cooldown = 2

    def should_sync(self, path: str) -> bool:
        now = time.time()
        last = self.last_sync.get(path, 0)
        if now - last < self.cooldown:
            return False
        self.last_sync[path] = now
        return True

    def on_any_event(self, event):
        """处理任何文件变化事件"""
        if event.is_directory:
            return

        path = Path(event.src_path)
        if path.suffix == '.md' and self.should_sync(event.src_path):
            logger.info(f"检测到Claude Memory文件变化: {path.name}")
            self._do_memory_sync()

    def _do_memory_sync(self):
        """执行Claude Memory同步"""
        try:
            result = subprocess.run(
                ["bash", str(CLAUDE_MEMORY_SYNC)],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info("Claude Memory同步成功")
            else:
                logger.error(f"Claude Memory同步失败: {result.stderr}")
        except Exception as e:
            logger.error(f"Claude Memory同步异常: {e}")


def start_watcher():
    """启动文件监控"""
    logger.info(f"启动HR知识库监控: {OBS_HR_PATH}")
    logger.info(f"启动Claude Memory监控: {OBS_MEMORY_PATH}")

    # HR知识库监控
    hr_handler = HRDirHandler()
    hr_observer = Observer()
    hr_observer.schedule(hr_handler, str(OBS_HR_PATH), recursive=True)

    # Claude Memory监控
    memory_handler = ClaudeMemoryHandler()
    memory_observer = Observer()
    memory_observer.schedule(memory_handler, str(OBS_MEMORY_PATH), recursive=True)

    # 启动两个监控
    hr_observer.start()
    memory_observer.start()

    logger.info("监控已启动，按 Ctrl+C 停止")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("停止监控")
        hr_observer.stop()
        memory_observer.stop()
    hr_observer.join()
    memory_observer.join()


if __name__ == "__main__":
    start_watcher()
