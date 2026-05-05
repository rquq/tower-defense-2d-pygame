"""
Tập tin khởi chạy chính của trò chơi Tower Defense. 
Thực hiện việc kiểm tra tham số dòng lệnh và bắt đầu tiến trình vận hành của Engine.
"""
import sys

from core.engine import Engine

if __name__ == "__main__":
    is_dev = "--DEV" in sys.argv or "-DEV" in sys.argv
    game = Engine(is_dev)
    game.run()
