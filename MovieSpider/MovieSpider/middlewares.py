from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy import signals
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MoviespiderDownloaderMiddleware:
    def __init__(self):
        # 初始化 Chrome 浏览器选项
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        # 禁用图片、CSS、JS加载以提高速度
        chrome_prefs = {"profile.managed_default_content_settings.images": 2,
                        "profile.managed_default_content_settings.stylesheets": 2,
                        "profile.managed_default_content_settings.javascript": 1}  # 保留 JS，避免影响页面加载
        chrome_options.add_experimental_option("prefs", chrome_prefs)

        # 添加性能优化选项
        chrome_options.add_argument("--disable-dev-shm-usage")  # 使用共享内存
        chrome_options.add_argument("--disable-infobars")  # 禁用自动化提示
        chrome_options.add_argument("--disable-extensions")  # 禁用扩展
        chrome_options.add_argument("--disable-browser-side-navigation")  # 禁用侧导航
        chrome_options.add_argument("--disable-software-rasterizer")  # 禁用软件光栅化器

        # 初始化 WebDriver
        self.driver = webdriver.Chrome(options=chrome_options)

    @classmethod
    def from_crawler(cls, crawler):
        # 创建中间件实例
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)  # 确保在爬虫关闭时关闭浏览器
        return s

    def process_request(self, request, spider):
        self.driver.get(request.url)

        try:
            # 显式等待关键元素（如标题）加载出来，最长等待 3 秒
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.ID, "productTitle"))
            )
        except Exception as e:
            # 如果加载失败，记录错误
            spider.logger.error(f"Failed to load element on page {request.url}: {e}")
            return None

        # 获取页面的源代码
        body = self.driver.page_source

        # 返回带有页面源代码的响应对象
        return HtmlResponse(url=self.driver.current_url, body=body, encoding='utf-8', request=request)

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")

    def spider_closed(self, spider):
        # 在爬虫关闭时关闭 WebDriver
        self.driver.quit()
        spider.logger.info(f"Spider closed: {spider.name}")
