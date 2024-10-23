from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os

# CSVファイルの読み込み
url_csv_file = 'url.csv'
input_csv_file = 'input.csv'

url_data = pd.read_csv(url_csv_file)
input_data = pd.read_csv(input_csv_file)

# 入力データを辞書形式に変換
input_dict = {
    'name': input_data['name'][0],
    'kana': input_data['kana'][0],
    'company': input_data['company'][0],
    'tel': input_data['tel'][0],
    'mail': input_data['mail'][0],
    'subject': input_data['subject'][0],
    'content': input_data['content'][0]
}

# ChromeOptionsの設定（ヘッドレスモードを有効化）
chrome_options = Options()
# chrome_options.add_argument('--headless')  # ヘッドレスモードで実行
# chrome_options.add_argument('--no-sandbox')  # サンドボックスモードを無効化（サーバー上で必要な場合あり）
# chrome_options.add_argument('--disable-dev-shm-usage')  # 共有メモリの使用を無効化（サーバー上で必要な場合あり）

# ChromeDriverのパスを指定
service = Service('/usr/local/bin/chromedriver')

# エラーログファイルのパスを指定
download_folder = os.path.expanduser('~/Downloads')
log_file_path = os.path.join(download_folder, 'form_submission_log.txt')

# ログファイルを作成またはクリア
with open(log_file_path, 'w', encoding='utf-8') as f:
    f.write("フォーム送信ログ:\n")

# 各フォームURLについてフィールド名を確認
for index, row in url_data.iterrows():
    form_url = row['form_url']

    try:
        # ヘッドレスモードでブラウザを起動
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # フォームページにアクセス
        driver.get(form_url)
        time.sleep(2)  # ページが完全に読み込まれるのを待つ

        # フォーム内の全てのinput要素を取得
        input_elements = driver.find_elements(By.TAG_NAME, 'input')
        textarea_elements = driver.find_elements(By.TAG_NAME, 'textarea')
        button_elements = driver.find_elements(By.TAG_NAME, 'button')
        submit_button = None

        # inputフィールドにデータを入力
        for input_element in input_elements:
            field_name = input_element.get_attribute('name')
            field_type = input_element.get_attribute('type')

            # テキストフィールドへの入力
            if field_type == 'text':
                if 'company' in field_name:
                    input_element.send_keys(input_dict['company'])
                elif 'kana' in field_name:
                    input_element.send_keys(input_dict['kana'])
                elif 'tel' in field_name:
                    input_element.send_keys(input_dict['tel'])
                elif 'mail' in field_name:
                    input_element.send_keys(input_dict['mail'])
                elif 'subject' in field_name:
                    input_element.send_keys(input_dict['subject'])
            
            # telフィールドへのデータ入力
            elif field_type == 'tel':
                if 'tel' in field_name:
                    input_element.send_keys(input_dict['tel'])

            # emailフィールドへのデータ入力
            elif field_type == 'email':
                if 'mail' in field_name:
                    input_element.send_keys(input_dict['mail'])

            # 送信ボタンの特定
            elif field_type == 'submit' and 'submit' in field_name:
                submit_button = input_element

        # textareaフィールドへのデータ入力
        for textarea_element in textarea_elements:
            field_name = textarea_element.get_attribute('name')
            if 'content' in field_name:
                textarea_element.send_keys(input_dict['content'])
            elif 'message' in field_name:
                textarea_element.send_keys(input_dict['content'])
            elif 'textarea' in field_name:
                textarea_element.send_keys(input_dict['content'])

        # 送信ボタンがinputでみつかっていない場合
        if submit_button == None:
            # button要素の中から送信ボタンを探す
            for button_element in button_elements:
                field_type = button_element.get_attribute("type")
                if field_type == 'submit':
                    submit_button = button_element

        # 送信ボタンをクリック（あれば）
        if submit_button:
            submit_button.click()

            # エラーメッセージを確認（クラス名に "err" または "error" を含む要素）
            try:
                error_message = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'err') or contains(@class, 'error')]"))
                )
                if error_message:
                    with open(log_file_path, 'a', encoding='utf-8') as f:
                        f.write(f"failed: {form_url} - エラーメッセージ: {error_message.text}\n")
            except:
                # エラーメッセージが見つからない場合、送信成功と見なす
                with open(log_file_path, 'a', encoding='utf-8') as f:
                    f.write(f"success: {form_url}\n")

    except Exception as e:
        # エラー発生時のログ出力
        with open(log_file_path, 'a', encoding='utf-8') as f:
            f.write(f"failed: {form_url} - エラーメッセージ: {str(e)}\n")
    
    finally:
        # ブラウザを閉じる
        driver.quit()
