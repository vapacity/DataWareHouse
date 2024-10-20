import scrapy
import pandas as pd
from ..items import MovieItem


class MoviesSpider(scrapy.Spider):
    name = 'movies'
    cookies = {
        "anonymid": "j7wsz80ibwp8x3",
        "_r01_": "1",
        "ln_uact": "mr_mao_hacker@163.com",
        "_de": "BF09EE3A28DED52E6B65F6A4705D973F1383380866D39FF5",
        "depovince": "GW",
        "jebecookies": "2fb888d1-e16c-4e95-9e59-66e4a6ce1eae|||||",
        "ick_login": "1c2c11f1-50ce-4f8c-83ef-c1e03ae47add",
        "p": "158304820d08f48402be01f0545f406d9",
        "first_login_flag": "1",
        "ln_hurl": "http://hdn.xnimg.cn/photos/hdn521/20180711/2125/main_SDYi_ae9c0000bf9e1986.jpg",
        "t": "adb2270257904fff59f082494aa7f27b9",
        "societyguester": "adb2270257904fff59f082494aa7f27b9",
        "id": "327550029",
        "xnsid": "4a536121",
        "loginfrom": "syshome",
        "wp_fold": "0"
    }
    headers = {
        'Host': 'www.amazon.com',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 7.0; \
                                SM-A520F Build/NRD90M; wv) AppleWebKit/537.36 \
                                (KHTML, like Gecko) Version/4.0 \
                                Chrome/65.0.3325.109 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,\
                                application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    }

    def start_requests(self):
        # 读取CSV文件
        df = pd.read_csv("E:\Tongji\大三上学期\数据存储与管理\DataWareHouse\\asins.csv")

        # 获取起始和结束位置
        start_pos = int(input("请输入起始位置 (start_position):"))
        end_pos = int(input("请输入结束位置 (end_position):"))
        # 提取 'productId' 列中指定范围的值，形成列表
        for index, row in df.loc[start_pos:end_pos].iterrows():
            asin = row['productId']
            record = row['record']

            # 如果已经爬取过，则跳过
            if record == 1:
                self.log(f'Skipping already crawled ASIN: {asin}')
                continue

            # 生成对应的 URL 并发出请求
            url = f"https://www.amazon.com/dp/{asin}/?language=en_US"
            yield scrapy.Request(url=url, headers=self.headers, cookies=self.cookies, callback=self.parse,
                                 meta={'index': index, 'df': df})

    def parse(self, response):
        # 初始化MovieItem实例
        item = MovieItem()

        # 获取ASIN值
        asin_begin_position = 26
        asin_length = 10
        item['ASIN'] = response.url[asin_begin_position:asin_begin_position + asin_length]

        productDetails = ['ASIN', 'Title', 'Subtitles', 'Language', 'Release year'
            , 'Release date', 'Rated', 'Runtime', 'Description', 'Contributors'
            , 'Actors', 'Directors', 'Producers', 'Media Format', 'Genres'
            , 'Customer Reviews', 'IMDb', 'Number of discs', 'Studio'
            ,'Director','Run time','Genre','Audio languages','Released','Contributor']
        itemKeys = ['ASIN', 'Title', 'Subtitles', 'Language', 'Release_year'
            , 'Release_date', 'Rated', 'Run_time', 'Description', 'Contributors'
            , 'Actors', 'Directors', 'Producers', 'Media_Format', 'Genres'
            , 'Customer_Reviews', 'IMDb', 'Number_of_discs', 'Studio'
            ,'Directors','Run_time','Genres','Language','Release_year','Contributors']

        # 获取标题
        title = response.xpath('//*[@id="productTitle"]/text()').get()
        if title:
            item['Title'] = title.strip()

            # 找到标题下的商品信息
            top_product_infos = response.xpath('//*[@id="bylineInfo"]')
            if top_product_infos is not None:
                # 获取top_product_infos下所有span
                span_list = response.xpath('//*[@id="bylineInfo"]/span[@class="a-color-secondary"]')
                for span in span_list:
                    # 获取每个span里面的字符串
                    span_string = span.xpath('text()').get()
                    # 清理span_string：去掉空格和冒号
                    span_string = span_string.strip().replace(':', '')
                    if span_string and span_string in productDetails:
                        # 找到span下的第一个div
                        div = span.xpath('following-sibling::div[1]')
                        # 检查是否存在div，并获取其内部的span文本内容
                        if div is not None:
                            # 如果存在div，则获取div内部所有span的文本内容
                            span_texts = div.xpath('.//span/text()').getall()
                            if span_texts:
                                following_span_text = ''.join(span_texts).strip()
                            else:
                                print(f"following_span_text is null!!!!!!!!!!!!!!!!!!!!")
                        else:
                            # 如果不存在div，则获取当前span后面所有的span文本内容
                            following_span_text = [text.strip() for text in
                                                   span.xpath('following-sibling::span/text()').getall()]

                        if following_span_text:
                            index = productDetails.index(span_string)
                            corresponding_string = itemKeys[index]
                            item[corresponding_string] = following_span_text

            # 找到商品信息部分
            product_infos = response.xpath('//*[@id="productOverview_feature_div"]')
            if product_infos is not None:
                # 获取product_infos下所有td
                td_list = product_infos.xpath('.//td[@class="a-span3"]')
                for td in td_list:
                    # 获取每个td里面的字符串
                    td_string = td.xpath('.//span/text()').get()
                    if td_string and td_string in productDetails:
                        # 获得td下对应的内容
                        following_span = td.xpath('./following-sibling::td[@class="a-span9"]')
                        # 检查following_span是否存在且只包含一个span标签
                        if following_span and len(following_span.xpath('.//span').getall()) == 1:
                            following_span_text = following_span.xpath('.//span/text()').get()
                            if following_span_text:
                                following_span_text = following_span_text.strip()
                        else:
                            # 如果不只包含一个span标签，找到页面中id包含“a-popover-content”的第一个div
                            following_span_text = following_span.xpath('.//span[@class="a-truncate-full a-offscreen"]/text()').get()
                            # 去除前后的单引号或双引号
                            if following_span_text:
                                # 去除前后的单引号
                                following_span_text = following_span_text.replace("'","")
                                # 去除前后的双引号
                                following_span_text = following_span_text.replace('"',"")
                        if following_span_text:
                            index = productDetails.index(td_string)
                            corresponding_string = itemKeys[index]
                            item[corresponding_string] = following_span_text

            # 找到Product Description(有些网页没有)
            productDescription_feature_div = response.xpath('//*[@id="productDescription_feature_div"]')
            if productDescription_feature_div is not None:
                # 找到下面的所有标题
                title_list = productDescription_feature_div.xpath('.//h2')
                for title in title_list:
                    title_content = title.xpath('text()').get().strip()
                    if title_content == "Product Description":
                        # 找到title下的product_description_span
                        product_description_spans = title.xpath('following-sibling::div[1]//span')
                        # 初始化一个空字符串来存储所有span标签的内容
                        span_contents = ""
                        if product_description_spans:
                            # 遍历所有span元素
                            for span in product_description_spans:
                                # 获取每个span元素的文本内容
                                text_content = span.xpath('text()').get()
                                if text_content:
                                    # 将文本内容添加到span_contents字符串中
                                    span_contents += text_content.strip() + " "
                        # 去除最后一个多余的空格，并赋值给item
                        if span_contents:
                            span_contents = span_contents.strip()
                            item['Description'] = span_contents
                        else:
                            print("span_contents is null!!!!!!!!!")

            # 找到Product details
            product_details = response.xpath('//*[@id="detailBulletsWrapper_feature_div"]')
            if product_details is not None:
                # 获取Product details下所有li元素
                li_list = response.xpath('//*[@id="detailBullets_feature_div"]/ul/li')
                for li in li_list:
                    # 获取class="a-text-bold"的span元素的文本内容
                    bold = li.xpath('.//span[@class="a-text-bold"]')
                    bold_text = bold.xpath('.//text()').get()
                    # 检查bold_text是否不为空
                    if bold_text:
                        # 清理bold_text
                        cleaned_bold_text = bold_text.strip().replace("‎", "").replace("‏", "").split(":", 1)[0].strip()

                        # 清理productDetails中的每个项，以匹配清理后的bold_text
                        cleaned_productDetails = [
                            item.strip().replace("‎", "").replace("‏", "").replace(":", "").lower()
                            for item in productDetails]

                        # 将清理后的bold_text转换为小写，并去除可能的多余空格
                        cleaned_bold_text_lower = cleaned_bold_text.lower()

                        # 检查清理后的bold_text是否在清理后的productDetails列表中
                        if cleaned_bold_text_lower in cleaned_productDetails:
                            # 获取匹配项在productDetails列表中的索引
                            index = cleaned_productDetails.index(cleaned_bold_text_lower)

                            # 获取productDetails列表中对应的原始项
                            corresponding_string = itemKeys[index]
                            print(f"Match found for: {cleaned_bold_text}, corresponding string: {corresponding_string}")

                            # 获取following-sibling::span元素的文本内容
                            following_span_text = bold.xpath('.//following-sibling::span/text()').get()
                            item[corresponding_string] = following_span_text
                        else:
                            print(f"No match for: {cleaned_bold_text}")
                # 获取Product details下的customer reviews
                customer_reviews_span = response.xpath('//*[@id="acrPopover"]')
                customer_reviews_text = customer_reviews_span.xpath('@title').get()

                if customer_reviews_text:
                    item['Customer_Reviews'] = customer_reviews_text

            df = response.meta['df']
            index = response.meta['index']
            df.at[index, 'record'] = 1
            df.to_csv("E:\Tongji\大三上学期\数据存储与管理\DataWareHouse\\asins.csv", index=False)

        else:
            title = response.xpath('//*[@id="main"]/div[1]/div/div/div[2]/div/div/div/div[1]/h1/text()').get()
            if title:
                item['Title'] = title.strip()

            # pv
            # 获取more info对应h3标签
            more_info_h = response.xpath('//*[@id="btf-product-details"]/h3')
            more_info_text = more_info_h.xpath('./span/text()').get()
            if more_info_text=="More info":
                # 找到h3标签紧邻的div，取出里面的dl_list
                dl_list = more_info_h.xpath('following-sibling::div[1]//dl')
                for dl in dl_list:
                    # 找到每个dl里的属性名
                    attr = dl.xpath('./dt/span/text()').get().strip()
                    if attr in productDetails:
                        # 将dt后的dd内容全部取出
                        following_span_text = dl.xpath('./dt/following-sibling::dd//text()').getall()
                        if following_span_text:
                            # 使用strip()清理每个文本片段，并用空格拼接成一个字符串
                            following_span_text = ' '.join([txt.strip() for txt in following_span_text])
                        # 获取匹配项在productDetails列表中的索引
                        index = productDetails.index(attr)
                        # 获取productDetails列表中对应的原始项
                        corresponding_string = itemKeys[index]
                        item[corresponding_string] = following_span_text

            # 获取top_infos
            top_infos_div = response.xpath('//*[@id="main"]/div[1]/div/div/div[2]/div/div/div/div[2]/div/div[3]/div')
            if top_infos_div is not None:
                # 获取top_infos_div下的所有标签
                tags = top_infos_div.xpath('.//*')
                # 遍历所有标签
                for tag in tags:
                    # 获取标签的aria-label属性
                    aria_label = tag.xpath('@aria-label').get()
                    # 检查aria-label是否存在
                    if aria_label:
                        # 分割aria-label的第一个单词
                        first_word = aria_label.split()[0]
                        # 检查第一个单词是否在productDetails中
                        if first_word in productDetails:
                            # 如果匹配，获取aria-label的第一个单词后面的全部内容
                            matched_content = aria_label.split(first_word, 1)[1].strip()
                            # 获取匹配项在productDetails列表中的索引
                            index = productDetails.index(first_word)
                            # 获取productDetails列表中对应的原始项
                            corresponding_string = itemKeys[index]
                            item[corresponding_string] = matched_content
                        else:
                            print(f"No match for: {first_word}")

            # 获取评论
            description = response.xpath('//*[@id="main"]/div[1]/div/div/div[2]/div/div/div/div[2]/div/div[2]/span/span/text()').get()
            if description:
                item['Description'] = description
            else:
                print("No description found!!!!!!!!!!!!!")

            # 获取genre
            genre_div = response.xpath('//*[@id="main"]/div[1]/div/div/div[2]/div/div/div/div[2]/div/div[4]/div')
            # 初始化一个空字符串来存储所有aria-label属性值的组合
            aria_labels = []
            if genre_div is not None:
                # 获取genre_div下的所有span元素
                spans = genre_div.xpath('.//span')
                # 遍历所有span元素
                for span in spans:
                    # 获取每个span元素的aria-label属性值
                    aria_label = span.xpath('@aria-label').get()
                    if aria_label:
                        aria_labels.append(aria_label)

            # 使用", "作为分隔符来拼接aria_labels列表中的所有字符串
            combined_aria_labels = ", ".join(aria_labels)
            item['Genres'] = combined_aria_labels

            df = response.meta['df']
            index = response.meta['index']
            df.at[index, 'record'] = 1
            df.to_csv("E:\Tongji\大三上学期\数据存储与管理\DataWareHouse\\asins.csv", index=False)
        #返回item
        yield item

