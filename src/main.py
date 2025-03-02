#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from bizreach_scraper import BizreachScraper
from utils import load_url_list, create_output_filename, ensure_directory_exists


def parse_arguments():
    """コマンドライン引数を解析する関数"""
    parser = argparse.ArgumentParser(description='ビズリーチ求職者情報スクレイピングツール')
    
    parser.add_argument('-u', '--username', required=True,
                        help='ビズリーチのログインユーザー名/メールアドレス')
    
    parser.add_argument('-p', '--password', required=True,
                        help='ビズリーチのログインパスワード')
    
    parser.add_argument('-d', '--driver', default=None,
                        help='Chromeドライバーのパス（省略可）')
    
    parser.add_argument('-i', '--input', required=True,
                        help='スクレイピング対象URLのリストファイル（.txt, .csv, .json）')
    
    parser.add_argument('-o', '--output-dir', default='./data',
                        help='出力ディレクトリのパス（デフォルト: ./data）')
    
    parser.add_argument('-f', '--format', choices=['csv', 'json', 'both'], default='both',
                        help='出力形式（csv, json, both）（デフォルト: both）')
    
    parser.add_argument('-w', '--wait', type=int, default=3,
                        help='リクエスト間の待機時間（秒）（デフォルト: 3）')
    
    return parser.parse_args()


def main():
    """メイン関数"""
    # 引数の解析
    args = parse_arguments()
    
    # 出力ディレクトリの作成
    ensure_directory_exists(args.output_dir)
    
    # URLリストの読み込み
    try:
        url_list = load_url_list(args.input)
        print(f"URLリストを読み込みました: {len(url_list)}件")
    except Exception as e:
        print(f"URLリストの読み込みに失敗しました: {str(e)}")
        sys.exit(1)
    
    # スクレイパーの初期化
    scraper = BizreachScraper(args.driver)
    
    try:
        # ブラウザの起動
        scraper.start_browser()
        print("ブラウザを起動しました")
        
        # ログイン処理
        if not scraper.login(args.username, args.password):
            print("ログインに失敗しました。ユーザー名とパスワードを確認してください。")
            sys.exit(1)
        
        print("ログインに成功しました")
        
        # スクレイピングの実行
        print(f"スクレイピングを開始します（対象URL: {len(url_list)}件）")
        scraper.scrape_multiple_candidates(url_list, (args.wait, args.wait + 2))
        
        # 取得したデータの保存
        if args.format in ['csv', 'both']:
            csv_filename = os.path.join(
                args.output_dir, 
                create_output_filename('bizreach_candidates', '.csv')
            )
            if scraper.save_data_to_csv(csv_filename):
                print(f"CSVファイルに保存しました: {csv_filename}")
        
        if args.format in ['json', 'both']:
            json_filename = os.path.join(
                args.output_dir, 
                create_output_filename('bizreach_candidates', '.json')
            )
            if scraper.save_data_to_json(json_filename):
                print(f"JSONファイルに保存しました: {json_filename}")
        
        print("スクレイピングが完了しました")
        
    except KeyboardInterrupt:
        print("\nユーザーによって中断されました")
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
    finally:
        # ブラウザの終了
        if scraper.close_browser():
            print("ブラウザを終了しました")


if __name__ == "__main__":
    main()
