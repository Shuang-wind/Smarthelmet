import os

# 你的 labels 根目录路径
labels_root = r"F:\大一下\作业\safety_helmet_detection\data\labels"

def remove_person_labels(labels_dir):
    """遍历指定文件夹下的所有 txt 标注文件，删除 class_id 为 2（person）的行"""
    removed_count = 0
    file_count = 0

    for filename in os.listdir(labels_dir):
        if filename.endswith('.txt'):
            filepath = os.path.join(labels_dir, filename)
            file_count += 1

            # 读取原文件所有行
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 过滤掉 class_id 为 2 的行
            new_lines = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) > 0 and parts[0] != '2':
                    new_lines.append(line + '\n')
                else:
                    removed_count += 1

            # 写回过滤后的内容
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

    print(f"[{os.path.basename(labels_dir)}] 处理完成！")
    print(f"  扫描文件数：{file_count}")
    print(f"  删除 person 标注数：{removed_count}\n")

if __name__ == "__main__":
    # 处理 train 和 valid 两个子文件夹
    train_labels_dir = os.path.join(labels_root, "train")
    valid_labels_dir = os.path.join(labels_root, "valid")

    print("===== 开始处理标注文件 =====")
    remove_person_labels(train_labels_dir)
    remove_person_labels(valid_labels_dir)
    print("===== 所有标注处理完毕 =====")