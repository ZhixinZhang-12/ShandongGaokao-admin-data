from flask import Flask, request, render_template_string  
import subprocess  
  
app = Flask(__name__)  
pythonPath='D:/anaconda3/python'
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
   <h1>学校查询部分</h1>  
    <form action="/run" method="post">  
      <label for="inputText">请输入学校名称:</label>  
      <input type="text" id="inputText" name="inputText">  
      <button type="submit">查询数据</button>  
    </form>  
    <h1>为什么不放到一个页面，确实是我不会(爬虫水平前端)，扔到另一个html里面更容易一些</h1>  

    
    {% if result %}  
      <h2>查询过程:</h2>  
      <pre>{{ result }}</pre>  
    {% endif %}  
  </body>  
</html>  
'''  
  
@app.route('/')  
def index():  
    return render_template_string(html_template, result=None)  
  
@app.route('/run', methods=['POST'])  
def run_script():  
    input_text = request.form['inputText']  
    # 这里我们简单地通过subprocess运行一个Python脚本，并将输入文本作为参数传递  
    # 假设脚本名为script.py，并且接受一个命令行参数  
    result = subprocess.run([pythonPath, 'script.py', input_text], capture_output=True, text=True)  
    return render_template_string(html_template, result=result.stdout)  
  
if __name__ == '__main__':  
    app.run(debug=True,port=5000)