import flask
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup
import subprocess

appold = flask.Flask(__name__)
pythonPath = "python"
# HTML模板
html_template = '''  
<!doctype html>  
<html lang="en">  
  <head>  
    <meta charset="utf-8">  
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">  
    <title>Run Python Script</title>  
  </head>  
  <body>  
   <h1>学校查询部分,带括号的学校括号请用英文括号,比如中国地质大学(武汉)</h1>  
    <form action="/run" method="post">  
      <label for="inputText">请输入学校名称:</label>  
      <input type="text" id="inputText" name="inputText">  
      <button type="submit">查询数据</button>  
    </form>  
    <h1>为什么长得这么丑,主要是我真不会前端</h1>
    <div>我都不知道他怎么跑起来的,下面那echarts表格是直接用render_embed加上sys.stdout嗯打印出来的  </div>

    <div> 
      {{ result|safe }}  
    </div>
  </body>  
</html>  
'''


@appold.route('/')
def index():
    return flask.render_template_string(html_template, result=None)


@appold.route('/run', methods=['POST'])
def run_script():
    input_text = flask.request.form['inputText']
    # 这里我们简单地通过subprocess运行一个Python脚本，并将输入文本作为参数传递
    # 假设脚本名为script.py，并且接受一个命令行参数
    try:
        # 运行 script.py 并捕获输出
        result = subprocess.run(
            [pythonPath, 'script.py', input_text],
            capture_output=True,
            text=True,
            check=True  # 如果脚本返回非零退出码，将引发 CalledProcessError
        )
        html_code = result.stdout.strip()  # 去除可能的空白字符
        return flask.render_template_string(html_template, result=html_code)
    except subprocess.CalledProcessError as e:
        # 处理脚本执行错误
        return f"脚本执行失败: {e}", 500


if __name__ == '__main__':
    appold.run(debug=True)
