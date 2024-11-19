import os
import shutil
import tkinter as tk
from tkinter import messagebox
import requests
import re  # 导入正则表达式模块

__version__ = '1.0.1'  # 版本号

class App:
    def __init__(self, root):
        self.root = root
        self.hosts_path = '/etc/hosts'  # host文件路径
        self.temp_path = '/tmp/hosts'  # 临时文件夹路径

        # 创建并复制host文件到临时文件夹
        shutil.copy(self.hosts_path, self.temp_path)

        # 创建提示信息和文本框
        self.label = tk.Label(root, text="【提示】多个请换行，也可获取host进行更新")
        self.label.grid(row=0, column=0, pady=20,padx=10)
        self.text = tk.Text(root, height=8, width=50)
        self.text.grid(row=1, column=0, padx=10)
        # 创建一个新的Frame
        self.frame = tk.Frame(root)
        self.frame.grid(row=2, column=0, pady=10, padx=10)

        # 在这个Frame中创建可点击的label
        self.label1 = tk.Label(self.frame, text="获取Figma Host", fg="#14D6B3", cursor="hand2")
        self.label1.grid(row=0, column=0, padx=20)
        self.label1.bind("<Button-1>", lambda e: self.fetch_text('https://ghp.ci/https://gist.githubusercontent.com/winskymobile/2a36a953425e75d30d7a5cdd82fe0c0b/raw/figma-host.txt'))

        self.label2 = tk.Label(self.frame, text="获取Adobe Host", fg="#14D6B3", cursor="hand2")
        self.label2.grid(row=0, column=1, padx=20)
        self.label2.bind("<Button-1>", lambda e: self.fetch_text('https://ghp.ci/https://gist.githubusercontent.com/winskymobile/59deede094f0c5ea816bde547098f1be/raw/adboe-host.txt'))
        # 创建按钮
        self.button_replace = tk.Button(root, text="更新Host", command=self.replace_hosts)
        self.button_replace.grid(row=3, column=0, pady=10)

    def fetch_text(self, url):
        # 获取网址的文本并插入到文本框中
        try:
            response = requests.get(url)
            response.raise_for_status()
            self.text.delete('1.0', 'end')  # 清空文本框
            self.text.insert('1.0', response.text)  # 插入获取的文本
            messagebox.showinfo('提示', '获取成功，请点击按钮更新')
        except requests.HTTPError as e:
            messagebox.showinfo('提示', f'获取失败: {e}')

    def parse_hosts(self, content):
        # 解析host信息，返回一个字典，键为主机名，值为IP地址
        hosts = {}
        lines = content.split('\n')
        for line in lines:
            parts = line.split()
            if len(parts) >= 2 and re.match(r'\d+\.\d+\.\d+\.\d+', parts[0]):  # 检查是否为有效的IP地址
                hosts[parts[1]] = parts[0]
        return hosts

    def replace_hosts(self):
        # 获取文本框内容
        content = self.text.get('1.0', 'end-1c')
        if not content:
            messagebox.showinfo('提示', '输入框为空，请输入host信息')
            return

        # 解析文本框和临时host文件的内容
        new_hosts = self.parse_hosts(content)
        lines = []
        with open(self.temp_path, 'r') as f:
            lines = f.readlines()

        # 对比并更新host文件
        updated = 0
        added = 0
        for host, ip in new_hosts.items():
            found = False
            for i, line in enumerate(lines):
                parts = line.split()
                if len(parts) >= 2 and parts[1] == host:
                    found = True
                    if parts[0] != ip:
                        # 更新IP地址
                        lines[i] = f'{ip} {host}\n'
                        updated += 1
                    break
            if not found:
                # 添加新的host信息
                lines.append(f'\n{ip} {host}')
                added += 1

        # 将更新后的host信息写回临时文件
        with open(self.temp_path, 'w') as f:
            f.writelines(lines)

        # 使用AppleScript获取管理员权限并替换host文件
        command = f'''
        do shell script "cp {self.temp_path} {self.hosts_path}" with administrator privileges
        '''
        if os.system(f"osascript -e '{command}'") == 0:
            messagebox.showinfo('提示', f'替换host成功，更新了{updated}条，新增了{added}条host信息')
        else:
            messagebox.showinfo('提示', '替换host失败')

root = tk.Tk()
root.title("VHost")

# 窗口大小
root.geometry("380x280+530+220")

app = App(root)
root.mainloop()
