import os
import json
from datetime import datetime

def load_url_list(file_path):
    """
    URLリストをファイルから読み込む関数
    
    Args:
        file_path (str): URLリストが記載されたファイルのパス (.txt, .csv, .json)
        
    Returns:
        list: URLのリスト
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"URLリストファイルが見つかりません: {file_path}")
    
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.json':
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'urls' in data:
                return data['urls']
            else:
                raise ValueError("JSONファイルの形式が正しくありません。リストまたは'urls'キーを持つ辞書である必要があります。")
    
    elif file_ext in ['.txt', '.csv']:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 行ごとに読み込み、空白行と#で始まるコメント行を除外
            return [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    
    else:
        raise ValueError(f"サポートされていないファイル形式です: {file_ext}")


def validate_url(url):
    """
    URLの基本的な検証を行う関数
    
    Args:
        url (str): 検証するURL
        
    Returns:
        bool: 有効なURLならTrue
    """
    # 簡易的な検証（より厳密にはre.matchなどを使用可能）
    return (
        url.startswith(('http://', 'https://')) and
        'bizreach.jp' in url
    )


def create_output_filename(base_name, extension, timestamp=True):
    """
    タイムスタンプ付きの出力ファイル名を生成する関数
    
    Args:
        base_name (str): ベースとなるファイル名
        extension (str): ファイル拡張子（.csvなど）
        timestamp (bool): タイムスタンプを追加するかどうか
        
    Returns:
        str: 生成されたファイル名
    """
    if timestamp:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_name}_{timestamp_str}{extension}"
    else:
        filename = f"{base_name}{extension}"
        
    return filename


def ensure_directory_exists(directory_path):
    """
    ディレクトリが存在することを確認し、存在しない場合は作成する関数
    
    Args:
        directory_path (str): 確認/作成するディレクトリのパス
        
    Returns:
        bool: 成功ならTrue
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        return True
    return os.path.isdir(directory_path)


# テスト用モックデータ
def generate_mock_candidate_data(url="https://www.bizreach.jp/company/candidates/12345"):
    """
    テスト用のモック候補者データを生成する関数
    
    Args:
        url (str): モックデータに設定するURL
        
    Returns:
        dict: モックの候補者データ
    """
    return {
        "name": "テスト 太郎",
        "age": "35歳",
        "url": url,
        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "career_history": [
            {
                "company": "株式会社テスト",
                "period": "2018年4月 - 現在",
                "position": "シニアエンジニア"
            },
            {
                "company": "サンプル株式会社",
                "period": "2015年4月 - 2018年3月",
                "position": "Webエンジニア"
            }
        ],
        "skills": ["Python", "JavaScript", "AWS", "Docker"],
        "education": [
            {
                "school": "サンプル大学",
                "period": "2010年4月 - 2014年3月",
                "degree": "工学部 情報工学科"
            }
        ]
    }
