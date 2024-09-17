import json
import requests
import os

class DouyinVideoDownloader:
    def __init__(self, download_folder='/root/autodl-tmp/dy/downloaded_videos'):
        self.download_folder = download_folder
        self.base_url = "http://0.0.0.0:80/api/douyin/web/fetch_user_post_videos"
        
        # 创建下载文件夹，如果不存在
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

    def get_all_user_video_data(self, user_id, max_count=20):
        """循环获取用户的所有视频数据"""
        max_cursor = 0
        all_videos = []
        has_more = True
        
        while has_more:
            if len(all_videos) >= max_count:
                break
            # 构建请求参数
            params = {
                "sec_user_id": user_id,
                "max_cursor": max_cursor,
                "count": 20
            }

            # 发送 GET 请求
            response = requests.get(self.base_url, params=params)

            # 检查请求是否成功
            if response.status_code == 200:
                data = response.json()
                # 将当前批次数据加入总数据中
                all_videos.extend(data['data']['aweme_list'])
                
                # 更新 max_cursor 和 has_more
                max_cursor = data.get('data', {}).get('max_cursor', 0)
                has_more = data.get('data', {}).get('has_more', False)
                
                print(f"Fetched {len(data['data']['aweme_list'])} videos, next cursor: {max_cursor}")
            else:
                print(f"Error: Unable to fetch data, status code: {response.status_code}")
                has_more = False

        return all_videos[:max_count]

    def save_to_json(self, data, filename="/root/autodl-tmp/dy/user_video_data.json"):
        # 将数据保存到 JSON 文件
        try:
            with open(filename, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            print(f"Data successfully saved to {filename}")
        except IOError as e:
            print(f"Error saving data to {filename}: {e}")

    def download_mp4_videos(self, json_file_path):
        # 打开并读取JSON文件
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 解析aweme_list中的每个作品信息
        for aweme in data:
            video_info = aweme.get('video', {})
            play_addr = video_info.get('play_addr', {})
            url_list = play_addr.get('url_list', [])
            
            # 检查是否为mp4格式
            if 'format' in video_info and video_info['format'] == "mp4":
                # 获取作品名称
                work_name = aweme['desc'].split('#')[0].replace(" ", "_")
                download_url = url_list[-1]  # 获取最后一个MP4下载链接
                
                # 生成文件保存路径
                file_name = f"{work_name}.mp4"
                file_path = os.path.join(self.download_folder, file_name)
                
                # 下载视频并保存到本地
                response = requests.get(download_url, stream=True)
                if response.status_code == 200:
                    with open(file_path, 'wb') as video_file:
                        for chunk in response.iter_content(chunk_size=1024):
                            video_file.write(chunk)
                    print(f"Downloaded: {file_name}")
                else:
                    print(f"Failed to download {file_name}")

# 使用示例
sec_user_id = "MS4wLjABAAAAim-zIeoEqFPtFQ69seyIb5c70pdancDu0povDPuOq6nzBbEcofJ1pLX4z0CphcRI"
downloader = DouyinVideoDownloader()

# 获取视频数据
video_data = downloader.get_all_user_video_data(sec_user_id)

# 保存视频数据到 JSON 文件
if video_data:
    downloader.save_to_json(video_data)

# 下载 MP4 视频
json_file_path = '/root/autodl-tmp/dy/user_video_data.json'  # 替换为实际的文件路径
downloader.download_mp4_videos(json_file_path)
