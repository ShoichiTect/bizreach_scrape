import unittest
import os
import sys
import tempfile
import json
from unittest.mock import patch, MagicMock

# テスト対象のモジュールのパスを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from bizreach_scraper import BizreachScraper
from utils import generate_mock_candidate_data

# ChromeDriverManagerをモック化
from unittest.mock import patch, MagicMock


class TestBizreachScraper(unittest.TestCase):
    """BizreachScraperクラスのテストクラス"""
    
    def setUp(self):
        """テスト前の準備"""
        # 一時ディレクトリを作成
        self.temp_dir = tempfile.mkdtemp()
        
        # サンプルURLとモックデータ
        self.sample_urls = [
            "https://www.bizreach.jp/company/candidates/12345",
            "https://www.bizreach.jp/company/candidates/67890"
        ]
        
        self.mock_data = [
            generate_mock_candidate_data(self.sample_urls[0]),
            generate_mock_candidate_data(self.sample_urls[1])
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
    
    @patch('bizreach_scraper.webdriver')
    @patch('bizreach_scraper.ChromeDriverManager')
    def test_start_browser(self, mock_chrome_driver_manager, mock_webdriver):
        """ブラウザの起動テスト"""
        # モックの設定
        mock_driver = MagicMock()
        mock_service = MagicMock()
        mock_webdriver.Chrome.return_value = mock_driver
        mock_chrome_driver_manager.return_value.install.return_value = '/mock/path/to/chromedriver'
        
        # スクレイパーの初期化と実行
        scraper = BizreachScraper()
        result = scraper.start_browser()
        
        # 検証
        self.assertTrue(result)
        self.assertEqual(scraper.driver, mock_driver)
    
    @patch('bizreach_scraper.webdriver')
    def test_login_success(self, mock_webdriver):
        """ログイン成功のテスト"""
        # モックの設定
        mock_driver = MagicMock()
        mock_wait = MagicMock()
        mock_element = MagicMock()
        
        mock_webdriver.Chrome.return_value = mock_driver
        mock_driver.find_element.return_value = mock_element
        
        # スクレイパーの初期化
        scraper = BizreachScraper()
        scraper.start_browser()
        scraper.wait = mock_wait
        
        # テスト実行
        result = scraper.login("test@example.com", "password123")
        
        # 検証
        self.assertTrue(result)
        mock_driver.get.assert_called_once()
        self.assertEqual(mock_driver.find_element.call_count, 3)  # username, password, login button
        mock_element.send_keys.assert_called()
        mock_element.click.assert_called_once()
    
    @patch('bizreach_scraper.webdriver')
    def test_login_failure(self, mock_webdriver):
        """ログイン失敗のテスト"""
        # モックの設定
        mock_driver = MagicMock()
        mock_wait = MagicMock()
        
        mock_webdriver.Chrome.return_value = mock_driver
        mock_wait.until.side_effect = Exception("Login timeout")
        
        # スクレイパーの初期化
        scraper = BizreachScraper()
        scraper.start_browser()
        scraper.wait = mock_wait
        
        # テスト実行
        result = scraper.login("test@example.com", "wrong_password")
        
        # 検証
        self.assertFalse(result)
    
    @patch('bizreach_scraper.webdriver')
    def test_scrape_candidate_page(self, mock_webdriver):
        """候補者ページのスクレイピングテスト"""
        # モックの設定
        mock_driver = MagicMock()
        mock_wait = MagicMock()
        mock_name_element = MagicMock()
        mock_name_element.text = "テスト 太郎"
        
        mock_webdriver.Chrome.return_value = mock_driver
        mock_wait.until.return_value = mock_name_element
        
        # スクレイパーの初期化
        scraper = BizreachScraper()
        scraper.start_browser()
        scraper.wait = mock_wait
        scraper.driver = mock_driver
        
        # テスト実行
        url = self.sample_urls[0]
        result = scraper.scrape_candidate_page(url)
        
        # 検証
        self.assertIsInstance(result, dict)
        self.assertEqual(result["url"], url)
        self.assertEqual(result["name"], "テスト 太郎")
        mock_driver.get.assert_called_once_with(url)
    
    @patch('bizreach_scraper.webdriver')
    @patch('bizreach_scraper.time')
    def test_scrape_multiple_candidates(self, mock_time, mock_webdriver):
        """複数候補者のスクレイピングテスト"""
        # モックの設定
        mock_driver = MagicMock()
        mock_webdriver.Chrome.return_value = mock_driver
        
        # スクレイパーの初期化
        scraper = BizreachScraper()
        scraper.start_browser()
        
        # scrape_candidate_pageをモックに置き換え
        scraper.scrape_candidate_page = MagicMock(side_effect=[
            self.mock_data[0],
            self.mock_data[1]
        ])
        
        # テスト実行
        results = scraper.scrape_multiple_candidates(self.sample_urls)
        
        # 検証
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["url"], self.sample_urls[0])
        self.assertEqual(results[1]["url"], self.sample_urls[1])
        self.assertEqual(scraper.scrape_candidate_page.call_count, 2)
        self.assertEqual(mock_time.sleep.call_count, 1)  # 2ページなので1回の待機
    
    @patch('bizreach_scraper.webdriver')
    def test_save_data_to_csv(self, mock_webdriver):
        """CSVへのデータ保存テスト"""
        # モックの設定
        mock_webdriver.Chrome.return_value = MagicMock()
        
        # スクレイパーの初期化
        scraper = BizreachScraper()
        scraper.start_browser()
        
        # データを設定
        scraper.candidate_data = self.mock_data
        
        # 保存先ファイル名
        csv_filename = os.path.join(self.temp_dir, "test_output.csv")
        
        # テスト実行
        result = scraper.save_data_to_csv(csv_filename)
        
        # 検証
        self.assertTrue(result)
        self.assertTrue(os.path.exists(csv_filename))
        
        # CSVファイルの内容を確認
        import pandas as pd
        df = pd.read_csv(csv_filename)
        self.assertEqual(len(df), 2)
        self.assertIn("name", df.columns)
        self.assertIn("age", df.columns)
        self.assertIn("url", df.columns)
    
    @patch('bizreach_scraper.webdriver')
    def test_save_data_to_json(self, mock_webdriver):
        """JSONへのデータ保存テスト"""
        # モックの設定
        mock_webdriver.Chrome.return_value = MagicMock()
        
        # スクレイパーの初期化
        scraper = BizreachScraper()
        scraper.start_browser()
        
        # データを設定
        scraper.candidate_data = self.mock_data
        
        # 保存先ファイル名
        json_filename = os.path.join(self.temp_dir, "test_output.json")
        
        # テスト実行
        result = scraper.save_data_to_json(json_filename)
        
        # 検証
        self.assertTrue(result)
        self.assertTrue(os.path.exists(json_filename))
        
        # JSONファイルの内容を確認
        with open(json_filename, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(len(loaded_data), 2)
        self.assertEqual(loaded_data[0]["url"], self.sample_urls[0])
        self.assertEqual(loaded_data[1]["url"], self.sample_urls[1])
    
    @patch('bizreach_scraper.webdriver')
    def test_close_browser(self, mock_webdriver):
        """ブラウザの終了テスト"""
        # モックの設定
        mock_driver = MagicMock()
        mock_webdriver.Chrome.return_value = mock_driver
        
        # スクレイパーの初期化
        scraper = BizreachScraper()
        scraper.start_browser()
        
        # テスト実行
        result = scraper.close_browser()
        
        # 検証
        self.assertTrue(result)
        mock_driver.quit.assert_called_once()
        self.assertIsNone(scraper.driver)


if __name__ == '__main__':
    unittest.main()
