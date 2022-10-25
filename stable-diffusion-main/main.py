from flask import Flask, request, jsonify
from optimizedSD.arguments import Arguments
from optimizedSD.optimized_txt2img import StableDiffusion

model = StableDiffusion()
app = Flask(__name__)


@app.route("/imagine", methods=['POST'])
def text_to_image():
    args = Arguments()
    args.bind_json(request.data)

    result = model.imagine(args)

    return jsonify(result)


@app.route("/", methods=['GET'])
def test():
    return "hello"


app.run()
print('server started')
