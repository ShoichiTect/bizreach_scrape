#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
import os

# 親ディレクトリのパスを追加して、ソースコードをインポートできるようにします
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def run_tests():
    """すべてのテストを実行します"""
    # テストディレクトリからすべてのテストを検出
    test_suite = unittest.defaultTestLoader.discover(
        os.path.dirname(__file__),  # 現在のディレクトリ（testsディレクトリ）
        pattern='test_*.py'         # テストファイルの命名パターン
    )
    
    # テストの実行
    result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # テスト結果に基づいて終了コードを設定
    sys.exit(not result.wasSuccessful())


if __name__ == '__main__':
    run_tests()
