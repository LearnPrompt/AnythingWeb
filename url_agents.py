import asyncio
import os
from pydantic import BaseModel
from agents import Agent, Runner, trace
from url_processor import extract_urls, process_url

"""
This example demonstrates a deterministic flow, where each step is performed by an agent.
1. The first agent generates a Typed Markdown
2. We feed the content into the second agent
3. The second agent checks if the content is good quality
4. If the outline is not good quality, we stop here
5. If the outline is good quality, we feed the content into the third agent
6. The third agent writes the website
"""

content_formatter_agent = Agent(
    name="content_formatter_agent",
    instructions="格式化和去重网页内容，按照以下结构排版：1. 标题使用Markdown标题格式(#, ##等)；2. 保留文章主体内容；3. 整理相关文章为列表格式；4. 去除重复内容；5. 保留图片链接；7. 如有视频内容，放在最前面。",
)

class ContentCheckerOutput(BaseModel):
    good_quality: bool

content_checker_agent = Agent(
    name="content_checker_agent",
    instructions="检查格式化后的内容质量，判断是否满足排版规范、内容完整性和可读性要求。",
    output_type=ContentCheckerOutput,
)

webpage_generator_agent = Agent(
    name="webpage_generator_agent",
    instructions="""我会给你一个文件，分析内容，并将其转化为美观漂亮的中文可视化网页作品集：

## 内容要求
- 所有页面内容必须为简体中文
- 保持原文件的核心信息，但以更易读、可视化的方式呈现
- 在页面底部添加作者信息区域，包含：
  - 作者姓名: [卡尔]
  - 社交媒体链接: 至少包含Twitter/X：https://x.com/@aiwarts
  - 版权信息和年份

## 设计风格
- 整体风格参考Linear App的简约现代设计
- 使用清晰的视觉层次结构，突出重要内容
- 配色方案应专业、和谐，适合长时间阅读

## 技术规范
- 使用HTML5、TailwindCSS 3.0+（通过CDN引入）和必要的JavaScript
- 实现完整的深色/浅色模式切换功能，默认跟随系统设置
- 代码结构清晰，包含适当注释，便于理解和维护

## 响应式设计
- 页面必须在所有设备上（手机、平板、桌面）完美展示
- 针对不同屏幕尺寸优化布局和字体大小
- 确保移动端有良好的触控体验

## 媒体资源
- 使用文档中的Markdown图片链接（如果有的话）
- 使用文档中的视频嵌入代码（如果有的话）

## 图标与视觉元素
- 使用专业图标库如Font Awesome或Material Icons（通过CDN引入）
- 根据内容主题选择合适的插图或图表展示数据
- 避免使用emoji作为主要图标

## 交互体验
- 添加适当的微交互效果提升用户体验：
  - 按钮悬停时有轻微放大和颜色变化
  - 卡片元素悬停时有精致的阴影和边框效果
  - 页面滚动时有平滑过渡效果
  - 内容区块加载时有优雅的淡入动画

## 性能优化
- 确保页面加载速度快，避免不必要的大型资源
- 图片使用现代格式(WebP)并进行适当压缩
- 实现懒加载技术用于长页面内容

## 输出要求
- 提供完整可运行的单一HTML文件，包含所有必要的CSS和JavaScript
- 确保代码符合W3C标准，无错误警告
- 页面在不同浏览器中保持一致的外观和功能

请根据上传文件的内容类型（文档、数据、图片等），创建最适合展示该内容的可视化网页。""",
    output_type=str,
)

async def main():
    # 读取input2.txt文件
    input_file_path = "./input/input2.txt"
    with open(input_file_path, "r", encoding="utf-8") as f:
        input_content = f.read()
    
    print(f"从文件读取URL: {input_content}")
    
    # 提取URL并处理
    urls = extract_urls(input_content)
    if not urls:
        print("未找到有效URL，请检查输入文件")
        exit(1)
    
    # 处理所有URL并拼接内容
    processed_content = ""
    for url in urls:
        print(f"处理URL: {url}")
        try:
            content = process_url(url)
            processed_content += content + "\n\n"
        except Exception as e:
            print(f"处理URL失败: {url}, 错误: {str(e)}")
    
    if not processed_content:
        print("所有URL处理失败，无法继续")
        exit(1)
        
    # 将处理后的内容写入process.txt文件
    with open("./output/process.txt", "w", encoding="utf-8") as f:
        f.write(processed_content)
    print("已将处理后的内容保存到process.txt")
    
    # # 确保整个工作流是单一追踪
    # with trace("网页内容处理流程"):
    #     # 1. 格式化内容
    #     formatter_result = await Runner.run(
    #         content_formatter_agent,
    #         processed_content,
    #     )
    #     print("内容已格式化")

    #     # 2. 检查内容质量
    #     checker_result = await Runner.run(
    #         content_checker_agent,
    #         formatter_result.final_output,
    #     )

    #     # 3. 如果内容质量不佳则停止
    #     assert isinstance(checker_result.final_output, ContentCheckerOutput)
    #     if not checker_result.final_output.good_quality:
    #         print("内容质量不佳，处理终止。")
    #         exit(0)

    #     print("内容质量良好，继续生成网页。")

    #     # 4. 生成网页
    #     webpage_result = await Runner.run(
    #         webpage_generator_agent,
    #         formatter_result.final_output,
    #     )
    #     print(f"网页已生成，保存到output.html")
        
    #     # 保存生成的HTML到文件
    #     with open("./output/output.html", "w", encoding="utf-8") as f:
    #         f.write(webpage_result.final_output)
    #     print("运行成功！")


if __name__ == "__main__":
    asyncio.run(main())