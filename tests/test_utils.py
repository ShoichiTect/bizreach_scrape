import unittest
import os
import json
import tempfile
from datetime import datetime
import sys

# テスト対象のモジュールのパスを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from utils import load_url_list, validate_url, create_output_filename, ensure_directory_exists, generate_mock_candidate_data


class TestUtils(unittest.TestCase):
    """ユーティリティ関数のテストクラス"""
    
    def setUp(self):
        """テスト前の準備"""
        # 一時ディレクトリを作成
        self.temp_dir = tempfile.mkdtemp()
        
        # サンプルURLリスト
        self.sample_urls = [
            "https://www.bizreach.jp/company/candidates/12345",
            "https://www.bizreach.jp/company/candidates/67890",
            "https://www.bizreach.jp/company/candidates/54321"
        ]
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        # 一時ファイルの削除
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)
    
    def test_load_url_list_from_txt(self):
        """TXTファイルからURLリストを読み込むテスト"""
        # テスト用のTXTファイルを作成
        txt_path = os.path.join(self.temp_dir, "urls.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.sample_urls))
            f.write("\n# これはコメントです\n")
            f.write("\n")  # 空行
        
        # テスト実行
        loaded_urls = load_url_list(txt_path)
        
        # 検証
        self.assertEqual(len(loaded_urls), 3)
        self.assertEqual(loaded_urls, self.sample_urls)
    
    def test_load_url_list_from_json(self):
        """JSONファイルからURLリストを読み込むテスト"""
        # テスト用のJSONファイルを作成（リスト形式）
        json_list_path = os.path.join(self.temp_dir, "urls_list.json")
        with open(json_list_path, 'w', encoding='utf-8') as f:
            json.dump(self.sample_urls, f)
        
        # テスト用のJSONファイルを作成（辞書形式）
        json_dict_path = os.path.join(self.temp_dir, "urls_dict.json")
        with open(json_dict_path, 'w', encoding='utf-8') as f:
            json.dump({"urls": self.sample_urls}, f)
        
        # テスト実行
        loaded_urls_list = load_url_list(json_list_path)
        loaded_urls_dict = load_url_list(json_dict_path)
        
        # 検証
        self.assertEqual(loaded_urls_list, self.sample_urls)
        self.assertEqual(loaded_urls_dict, self.sample_urls)
    
    def test_load_url_list_file_not_found(self):
        """存在しないファイルからのURLリスト読み込みテスト"""
        with self.assertRaises(FileNotFoundError):
            load_url_list(os.path.join(self.temp_dir, "not_exist.txt"))
    
    def test_load_url_list_invalid_format(self):
        """サポートされていない形式のファイルからのURLリスト読み込みテスト"""
        invalid_path = os.path.join(self.temp_dir, "invalid.xlsx")
        with open(invalid_path, 'w') as f:
            f.write("dummy")
        
        with self.assertRaises(ValueError):
            load_url_list(invalid_path)
    
    def test_validate_url(self):
        """URL検証のテスト"""
        # 有効なURL
        self.assertTrue(validate_url("https://www.bizreach.jp/company/candidates/12345"))
        self.assertTrue(validate_url("http://www.bizreach.jp/company/candidates/12345"))
        
        # 無効なURL
        self.assertFalse(validate_url("ftp://www.bizreach.jp/company/candidates/12345"))
        self.assertFalse(validate_url("https://www.example.com/company/candidates/12345"))
        self.assertFalse(validate_url("www.bizreach.jp/company/candidates/12345"))
    
    def test_create_output_filename(self):
        """出力ファイル名生成のテスト"""
        # タイムスタンプありのケース
        filename_with_timestamp = create_output_filename("test", ".csv", True)
        self.assertTrue(filename_with_timestamp.startswith("test_"))
        self.assertTrue(filename_with_timestamp.endswith(".csv"))
        self.assertGreater(len(filename_with_timestamp), 10)  # タイムスタンプ部分があることを確認
        
        # タイムスタンプなしのケース
        filename_without_timestamp = create_output_filename("test", ".json", False)
        self.assertEqual(filename_without_timestamp, "test.json")
    
    def test_ensure_directory_exists(self):
        """ディレクトリ存在確認/作成のテスト"""
        # 新しいディレクトリの作成
        new_dir = os.path.join(self.temp_dir, "new_directory")
        self.assertFalse(os.path.exists(new_dir))
        
        result = ensure_directory_exists(new_dir)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(new_dir))
        self.assertTrue(os.path.isdir(new_dir))
        
        # すでに存在するディレクトリの確認
        result = ensure_directory_exists(new_dir)
        self.assertTrue(result)
    
    def test_generate_mock_candidate_data(self):
        """モック候補者データ生成のテスト"""
        url = "https://www.bizreach.jp/company/candidates/test"
        mock_data = generate_mock_candidate_data(url)
        
        # 基本的な構造の検証
        self.assertEqual(mock_data["url"], url)
        self.assertIsInstance(mock_data["name"], str)
        self.assertIsInstance(mock_data["age"], str)
        self.assertIsInstance(mock_data["scraped_at"], str)
        
        # 経歴情報の検証
        self.assertIsInstance(mock_data["career_history"], list)
        self.assertGreater(len(mock_data["career_history"]), 0)
        
        # スキル情報の検証
        self.assertIsInstance(mock_data["skills"], list)
        
        # 学歴情報の検証
        self.assertIsInstance(mock_data["education"], list)


if __name__ == '__main__':
    unittest.main()
