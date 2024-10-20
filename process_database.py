import csv

def process_ID(file_path, output_file):
    product_ids = set()
    batch_size = 200  # 每次处理200条记录
    count = 0  # 记录处理的总数

    # 打开输入文件
    with open(file_path, 'r', encoding='iso-8859-1') as file:
        # 打开输出文件，设置为追加模式
        with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["productId"])  # 写入标题（如果文件已经有内容可以注释掉）

            for line in file:
                if line.startswith('product/productId'):
                    product_id = line.split(":")[1].strip()
                    product_ids.add(product_id)
                    count += 1

                    # 每处理 200 条记录，将其写入文件
                    if count % batch_size == 0:
                        for pid in product_ids:
                            writer.writerow([pid])
                        product_ids.clear()  # 清空集合以便下一批

            # 文件末尾如果不足200条，也需要写入
            if product_ids:
                print(f"Processed {count} records. Writing remaining records to file...")
                for pid in product_ids:
                    writer.writerow([pid])

    print(f"Total records processed: {count}")

import pandas as pd

# 将 file_path 替换为你 CSV 文件的实际路径
file_path = "E:/Projects/AmazonDataWareHouse/asins.csv"

# 读取 CSV 文件
df = pd.read_csv(file_path)

# 检查是否存在 'record' 列，如果不存在则初始化该列为 0
if 'record' not in df.columns:
    df['record'] = 0  # 初始化为 0，表示尚未爬取

# 将修改后的 DataFrame 写回到 CSV 文件中
df.to_csv(file_path, index=False)

# 显示前几行确认修改成功
print(df.head())
