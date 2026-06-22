"""
下载 Kaggle 安全帽检测数据集
使用 opendatasets 库，需要输入 Kaggle 用户名和 API Key
"""
import opendatasets as od

dataset_url = "https://www.kaggle.com/datasets/andrewmvd/hard-hat-detection"
output_dir = "F:/safety_helmet_dataset"

print("=" * 50)
print("下载 Kaggle 安全帽检测数据集")
print("=" * 50)
print(f"数据集: {dataset_url}")
print(f"保存到: {output_dir}")
print()
print("提示：首次运行会要求输入 Kaggle 用户名和 API Key")
print("API Key 获取方式：")
print("  1. 登录 https://www.kaggle.com")
print("  2. 点击头像 -> Settings -> API -> Create New Token")
print("  3. 下载的 kaggle.json 中包含用户名和 key")
print()

od.download(dataset_url, data_dir=output_dir)
print("\n下载完成！")
