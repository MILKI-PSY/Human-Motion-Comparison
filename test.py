import base64
from io import BytesIO

from flask import Flask, render_template, request
from matplotlib.figure import Figure

app = Flask(__name__)


@app.route("/")
def student():
    return render_template('input.html')


@app.route('/result', methods=['POST'])
def my_form_post():
    print(request.form)
    return render_template("result.html")


# def hello():
#     # Generate the figure **without using pyplot**.
#     fig = Figure()
#     ax = fig.subplots()
#     ax.plot([1, 2])
#     # Save it to a temporary buffer.
#     buf = BytesIO()
#     fig.savefig(buf, format="png")
#     # Embed the result in the html output.
#     data = base64.b64encode(buf.getbuffer()).decode("ascii")
#     return render_template('input.html',
#                            src=f'data:image/png;base64,{data}',
#                            my_str="aaa"
#                            )


if __name__ == '__main__':
    app.run()
