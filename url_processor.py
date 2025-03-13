import re
import json
import requests

def jina_proxy_url(original_url):
    """为普通网页生成Jina代理链接并返回原始markdown"""
    # 添加支持markdown格式的请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "x-respond-with": "markdown",
        "x-with-generated-alt": "true",  # 同时启用图片描述生成
        # 使用更通用的选择器,针对常见的文章容器类名
        "x-target-selector": "article, .article, .post-content, .entry-content, .content-area, main, .content"
    }
    
    # 直接请求处理后的内容
    proxy_url = f"https://r.jina.ai/{original_url}"
    
    try:
        response = requests.get(proxy_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.text
        
        # 如果是422错误，尝试使用不同的选择器
        if response.status_code == 422:
            # 尝试不使用选择器
            headers.pop("x-target-selector", None)
            response = requests.get(proxy_url, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.text
                
        # 如果仍然失败，尝试直接请求原始URL
        print(f"Jina代理请求失败，尝试直接请求原始URL: {original_url}")
        direct_response = requests.get(original_url, timeout=30)
        if direct_response.status_code == 200:
            # 简单提取标题和正文
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(direct_response.text, 'html.parser')
            title = soup.title.string if soup.title else "无标题"
            
            # 尝试提取正文内容
            content_elements = soup.select('article, .article, .post-content, .entry-content, .content-area, main, .content')
            content = ""
            if content_elements:
                for element in content_elements:
                    content += element.get_text() + "\n\n"
            else:
                # 如果没有找到内容元素，尝试提取所有段落
                paragraphs = soup.find_all('p')
                for p in paragraphs:
                    content += p.get_text() + "\n\n"
            
            return f"# {title}\n\n{content}"
            
        raise Exception(f"Jina代理请求失败，状态码：{response.status_code}，直接请求也失败，状态码：{direct_response.status_code}")
    except Exception as e:
        raise Exception(f"处理URL时出错: {str(e)}")

def bilibili_embed_code(video_url):
    """生成B站视频嵌入代码"""
    # 增强BV号提取正则表达式
    bvid_match = re.search(r'/(BV[\w]+)[/?]', video_url)
    if not bvid_match:
        raise ValueError("无效的B站视频链接")
    bvid = bvid_match.group(1)
    
    # 获取视频cid（添加请求头和异常处理）
    api_url = f"https://api.bilibili.com/x/player/pagelist?bvid={bvid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.bilibili.com/"
    }
    response = requests.get(api_url, headers=headers)
    
    # 添加HTTP状态码检查
    if response.status_code != 200:
        raise Exception(f"API请求失败，状态码：{response.status_code}")
    
    # 添加JSON解析异常处理
    try:
        data = response.json()
    except json.JSONDecodeError:
        raise ValueError("无效的API响应内容")
        
    if data['code'] != 0:
        raise Exception(f"API错误：{data.get('message', '未知错误')}")
    
    # 使用第一个分P的cid
    cid = data['data'][0]['cid']
    
    # 构造嵌入代码
    return f"""<iframe src="https://player.bilibili.com/player.html?isOutside=true&bvid={bvid}&cid={cid}&p=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"></iframe>"""

def process_url(url):
    """主处理函数"""
    if 'bilibili.com/video/BV' in url:
        return bilibili_embed_code(url)
    return jina_proxy_url(url)

def extract_urls(text):
    """从文本中提取URL"""
    url_pattern = re.compile(r'https?://\S+')
    return url_pattern.findall(text)

# 使用示例
if __name__ == "__main__":
    test_url = input("请输入URL: ")
    try:
        print(process_url(test_url))
    except Exception as e:
        print(f"处理失败: {str(e)}")