from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import pandas as pd
import json
import os
from datetime import datetime


class BizreachScraper:
    """ビズリーチの求職者情報をスクレイピングするためのクラス"""

    def __init__(self, chrome_driver_path=None):
        """
        ビズリーチスクレイパーの初期化
        
        Args:
            chrome_driver_path (str, optional): Chromeドライバーのパス。None の場合は自動検出・ダウンロードされます。
        """
        self.chrome_driver_path = chrome_driver_path
        self.options = webdriver.ChromeOptions()
        
        # ゲストモードの設定
        self.options.add_argument("--guest")
        
        # その他の設定
        self.options.add_argument("--disable-notifications")
        self.options.add_argument("--disable-popup-blocking")
        self.options.add_argument("--disable-extensions")
        
        self.driver = None
        self.wait = None
        self.candidate_data = []
    
    def start_browser(self):
        """ブラウザを起動する"""
        if self.chrome_driver_path:
            # 指定されたドライバーパスを使用
            service = Service(self.chrome_driver_path)
            self.driver = webdriver.Chrome(service=service, options=self.options)
        else:
            # ChromeDriverManagerを使用して自動検出・ダウンロード
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=self.options)
            
        self.wait = WebDriverWait(self.driver, 20)
        self.driver.maximize_window()
        return True
        
    def login(self, username, password, login_url="https://www.bizreach.jp/company/login"):
        """
        ビズリーチにログインする
        
        Args:
            username (str): ログイン用ユーザー名/メールアドレス
            password (str): パスワード
            login_url (str): ログインページのURL
        
        Returns:
            bool: ログイン成功ならTrue、失敗ならFalse
        """
        try:
            # ログインページにアクセス
            self.driver.get(login_url)
            
            # ユーザー名とパスワードを入力
            self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            
            # IDとPASSWORDのセレクターは実際のものに変更してください
            username_field = self.driver.find_element(By.ID, "username")
            username_field.clear()
            username_field.send_keys(username)
            
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(password)
            
            # ログインボタンをクリック
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # ログイン後のページが表示されるまで待機
            self.wait.until(EC.url_contains("dashboard"))
            
            return True
            
        except Exception as e:
            print(f"ログイン中にエラーが発生しました: {str(e)}")
            return False
    
    def scrape_candidate_page(self, url):
        """
        求職者ページから情報をスクレイピングする
        
        Args:
            url (str): 求職者ページのURL
        
        Returns:
            dict: 取得した求職者情報
        """
        try:
            self.driver.get(url)
            
            # ページが完全に読み込まれるまで待機
            time.sleep(3)  # ページ読み込みのための明示的な待機
            
            # 基本情報の取得（セレクターは実際のものに調整してください）
            candidate_info = {}
            
            # 氏名
            try:
                name_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.candidate-name")))
                candidate_info["name"] = name_element.text
            except Exception:
                candidate_info["name"] = "取得できませんでした"
            
            # 年齢
            try:
                age_element = self.driver.find_element(By.CSS_SELECTOR, "span.candidate-age")
                candidate_info["age"] = age_element.text
            except Exception:
                candidate_info["age"] = "不明"
            
            # 経歴情報
            try:
                career_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.career-history-item")
                career_history = []
                
                for element in career_elements:
                    company = element.find_element(By.CSS_SELECTOR, "div.company-name").text
                    period = element.find_element(By.CSS_SELECTOR, "div.period").text
                    position = element.find_element(By.CSS_SELECTOR, "div.position").text
                    
                    career_history.append({
                        "company": company,
                        "period": period,
                        "position": position
                    })
                
                candidate_info["career_history"] = career_history
            except Exception:
                candidate_info["career_history"] = []
            
            # スキル情報
            try:
                skill_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.skill-item")
                skills = [element.text for element in skill_elements]
                candidate_info["skills"] = skills
            except Exception:
                candidate_info["skills"] = []
            
            # 学歴情報
            try:
                education_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.education-item")
                education = []
                
                for element in education_elements:
                    school = element.find_element(By.CSS_SELECTOR, "div.school-name").text
                    period = element.find_element(By.CSS_SELECTOR, "div.edu-period").text
                    degree = element.find_element(By.CSS_SELECTOR, "div.degree").text
                    
                    education.append({
                        "school": school,
                        "period": period,
                        "degree": degree
                    })
                
                candidate_info["education"] = education
            except Exception:
                candidate_info["education"] = []
            
            # URL情報も保存
            candidate_info["url"] = url
            
            # スクレイピング時刻
            candidate_info["scraped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return candidate_info
            
        except Exception as e:
            return {"url": url, "error": str(e), "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    def scrape_multiple_candidates(self, url_list, wait_time_range=(3, 5)):
        """
        複数の求職者ページをスクレイピングする
        
        Args:
            url_list (list): 求職者ページのURLリスト
            wait_time_range (tuple): 各リクエスト間の待機時間の範囲（最小値, 最大値）
        
        Returns:
            list: 取得した求職者情報のリスト
        """
        self.candidate_data = []
        total_urls = len(url_list)
        
        for i, url in enumerate(url_list, 1):
            # スクレイピングを実行
            candidate_data = self.scrape_candidate_page(url)
            self.candidate_data.append(candidate_data)
            
            # 最後のURL以外は待機時間を設ける
            if i < total_urls:
                wait_time = wait_time_range[0] + (i % (wait_time_range[1] - wait_time_range[0] + 1))
                time.sleep(wait_time)
        
        return self.candidate_data
    
    def save_data_to_csv(self, filename="bizreach_candidates.csv"):
        """
        取得したデータをCSVファイルに保存する
        
        Args:
            filename (str): 保存先のファイル名
            
        Returns:
            bool: 保存成功ならTrue、失敗ならFalse
        """
        try:
            # データが複雑なので、フラット化する必要がある
            flat_data = []
            
            for candidate in self.candidate_data:
                flat_candidate = {
                    "name": candidate.get("name", ""),
                    "age": candidate.get("age", ""),
                    "url": candidate.get("url", ""),
                    "scraped_at": candidate.get("scraped_at", "")
                }
                
                # キャリア履歴は最新の3つまでを列として追加
                career_history = candidate.get("career_history", [])
                for i in range(min(3, len(career_history))):
                    flat_candidate[f"company_{i+1}"] = career_history[i].get("company", "")
                    flat_candidate[f"period_{i+1}"] = career_history[i].get("period", "")
                    flat_candidate[f"position_{i+1}"] = career_history[i].get("position", "")
                
                # スキルはカンマ区切りで1つの列に
                flat_candidate["skills"] = ", ".join(candidate.get("skills", []))
                
                # 学歴も最新のものを追加
                education = candidate.get("education", [])
                if education:
                    flat_candidate["school"] = education[0].get("school", "")
                    flat_candidate["edu_period"] = education[0].get("period", "")
                    flat_candidate["degree"] = education[0].get("degree", "")
                
                flat_data.append(flat_candidate)
            
            # DataFrameに変換してCSVに保存
            df = pd.DataFrame(flat_data)
            df.to_csv(filename, index=False, encoding="utf-8-sig")  # Excel対応のためUTF-8 with BOMで保存
            
            return True
            
        except Exception as e:
            print(f"データの保存中にエラーが発生しました: {str(e)}")
            return False
    
    def save_data_to_json(self, filename="bizreach_candidates.json"):
        """
        取得したデータをJSONファイルに保存する（全データを保持）
        
        Args:
            filename (str): 保存先のファイル名
            
        Returns:
            bool: 保存成功ならTrue、失敗ならFalse
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.candidate_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"JSONデータの保存中にエラーが発生しました: {str(e)}")
            return False
    
    def close_browser(self):
        """
        ブラウザを閉じる
        
        Returns:
            bool: 成功ならTrue
        """
        if self.driver:
            self.driver.quit()
            self.driver = None
            return True
        return False
