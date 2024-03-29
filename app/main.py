import io
from flask import Flask, request, jsonify, send_file, render_template
from optimizedSD.arguments import Arguments
from flask_accept import accept
from os import listdir
from os.path import isfile, join
from optimizedSD.optimized_txt2img import StableDiffusionTxt2Img

models_path = 'models/ldm/stable-diffusion-v1/'
model = StableDiffusionTxt2Img()
app = Flask(__name__)

generating = False


def serve_pil_image(pil_img):
    """ Stream a PIL.Image result """
    img_io = io.BytesIO()
    pil_img.save(img_io, 'PNG', quality=100)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


def error(message: str):
    return jsonify({
        'error': message
    })


@app.route("/", methods=['GET'])
def index():
    models = [f for f in listdir(models_path) if isfile(join(models_path, f)) and f.endswith('.ckpt')]
    return render_template('index.html', models=models)


@app.route("/imagine", methods=['POST'])
@accept('application/json', '*/*')
def text_to_image():
    """
     Route for generating and returning `n` image results,
     where `n` :== `args.n_samples`

     Serialized as an array of B64-encoded byte arrays.
    """

    global generating
    global model

    if generating:
        return error('text-to-image operation is already running')

    args = Arguments()
    args.bind_json(request.data)

    generating = True
    try:
        result = model.imagine(args, image_format='binary')
    finally:
        generating = False

    return jsonify(result)


@app.route("/imagine", methods=['POST'])
@text_to_image.support('image/png')
def text_to_image_stream():
    """ Route for streaming a single image result """

    global generating
    global model

    if generating:
        return error('text-to-image operation is already running')

    args = Arguments()

    # Force single image when streaming result content
    args.n_samples = 1

    args.bind_json(request.data)

    generating = True
    try:
        result = model.imagine(args, image_format='png')
    finally:
        generating = False

    first_result = result[0]

    return serve_pil_image(first_result)


app.run()
