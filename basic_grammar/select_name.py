import webview
import random
import threading

# 全局变量
name_list = []


class Api:
    def __init__(self):
        self.window = None

    def set_window(self, window):
        self.window = window

    def read_file(self):
        """读取姓名文件"""
        global name_list
        try:
            with open("name.txt", "r", encoding="utf-8") as file:
                name_list = [line.strip() for line in file if line.strip()]
            return {"success": True, "count": len(name_list), "message": f"成功加载 {len(name_list)} 个姓名"}
        except Exception as e:
            return {"success": False, "message": f"读取文件失败: {str(e)}"}

    def select_names(self, mode):
        """根据模式选择姓名"""
        global name_list

        if not name_list:
            read_result = self.read_file()
            if not read_result["success"]:
                return {"success": False, "names": [], "message": read_result["message"]}

        mode_num = {"1": 1, "2": 3, "3": 9}.get(mode, 1)

        if len(name_list) < mode_num:
            return {"success": False, "names": [], "message": f"姓名数量不足，需要{mode_num}个，但只有{len(name_list)}个"}

        try:
            selected = random.sample(name_list, mode_num)
            return {"success": True, "names": selected, "message": f"成功选择 {mode_num} 个姓名"}
        except Exception as e:
            return {"success": False, "names": [], "message": f"选择失败: {str(e)}"}


def load_html_content():
    """返回HTML界面"""
    return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>随机点名系统</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            padding: 30px;
            width: 90%;
            max-width: 500px;
            text-align: center;
        }

        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 24px;
        }

        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }

        .status {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 20px;
            font-size: 14px;
            color: #495057;
        }

        .mode-selector {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-bottom: 25px;
        }

        .mode-btn {
            background: #fff;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 12px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .mode-btn:hover {
            border-color: #667eea;
            background: #f8f9ff;
        }

        .mode-btn.active {
            border-color: #667eea;
            background: #667eea;
            color: white;
        }

        .action-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 15px 30px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s ease;
        }

        .action-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }

        .action-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        .result {
            margin-top: 25px;
            min-height: 100px;
        }

        .result-title {
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }

        .names-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
        }

        .name-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px 15px;
            border-radius: 20px;
            font-weight: bold;
            animation: popIn 0.5s ease;
        }

        @keyframes popIn {
            0% { transform: scale(0.8); opacity: 0; }
            100% { transform: scale(1); opacity: 1; }
        }

        .message {
            margin-top: 15px;
            padding: 10px;
            border-radius: 5px;
            font-size: 14px;
        }

        .success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 随机点名系统</h1>
        <div class="subtitle">选择模式并开始随机选择姓名</div>

        <div class="status" id="status">
            准备就绪，请选择模式...
        </div>

        <div class="mode-selector">
            <button class="mode-btn" data-mode="1">模式 1 - 选择 1 个姓名</button>
            <button class="mode-btn" data-mode="2">模式 2 - 选择 3 个姓名</button>
            <button class="mode-btn" data-mode="3">模式 3 - 选择 9 个姓名</button>
        </div>

        <button class="action-btn" id="startBtn" disabled>开始选择</button>

        <div class="result">
            <div class="result-title">选择结果：</div>
            <div class="names-container" id="namesContainer">
                <!-- 姓名将在这里显示 -->
            </div>
            <div class="message" id="message"></div>
        </div>
    </div>

    <script>
        let currentMode = null;
        let statusElement = document.getElementById('status');
        let namesContainer = document.getElementById('namesContainer');
        let messageElement = document.getElementById('message');
        let startBtn = document.getElementById('startBtn');

        // 模式选择
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentMode = btn.dataset.mode;
                startBtn.disabled = false;
                updateStatus(`已选择模式 ${currentMode}，点击开始按钮进行选择`);
            });
        });

        // 开始选择
        startBtn.addEventListener('click', async () => {
            if (!currentMode) {
                showMessage('请先选择模式！', 'error');
                return;
            }

            startBtn.disabled = true;
            startBtn.textContent = '选择中...';
            clearMessage();

            try {
                const result = await pywebview.api.select_names(currentMode);

                if (result.success) {
                    displayNames(result.names);
                    showMessage(result.message, 'success');
                    updateStatus(`成功选择 ${result.names.length} 个姓名`);
                } else {
                    showMessage(result.message, 'error');
                    updateStatus('选择失败');
                }
            } catch (error) {
                showMessage('调用Python函数失败: ' + error.toString(), 'error');
                updateStatus('发生错误');
            } finally {
                startBtn.disabled = false;
                startBtn.textContent = '开始选择';
            }
        });

        function displayNames(names) {
            namesContainer.innerHTML = '';
            names.forEach(name => {
                const nameElement = document.createElement('div');
                nameElement.className = 'name-card';
                nameElement.textContent = name;
                namesContainer.appendChild(nameElement);
            });
        }

        function showMessage(text, type) {
            messageElement.textContent = text;
            messageElement.className = `message ${type}`;
        }

        function clearMessage() {
            messageElement.textContent = '';
            messageElement.className = 'message';
        }

        function updateStatus(text) {
            statusElement.textContent = text;
        }

        // 初始化：读取文件
        window.addEventListener('pywebviewready', async function() {
            try {
                const result = await pywebview.api.read_file();
                if (result.success) {
                    updateStatus(`已加载 ${result.count} 个姓名，请选择模式`);
                } else {
                    updateStatus('文件加载失败');
                    showMessage(result.message, 'error');
                }
            } catch (error) {
                updateStatus('初始化失败');
                showMessage('初始化失败: ' + error.toString(), 'error');
            }
        });
    </script>
</body>
</html>
"""


def main():
    """主函数"""
    api = Api()

    # 创建窗口
    window = webview.create_window(
        '随机点名系统',
        html=load_html_content(),
        width=600,
        height=700,
        resizable=False,
        js_api=api
    )

    api.set_window(window)

    # 启动应用
    webview.start(debug=False)


if __name__ == '__main__':
    main()